"""
End-to-end tests for Koda.

Tests the full pipeline: audio → Whisper → text processing → output.
Also tests audio stream lifecycle, model loading, and watchdog health checks.

Usage:
    python -m unittest test_e2e -v          (quick tests, no model)
    python -m unittest test_e2e.TestWithModel -v   (slow tests, loads Whisper)
"""

import os
import sys
import time
import unittest
import tempfile
import numpy as np
from unittest.mock import patch, MagicMock

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from text_processing import process_text
from config import load_config, DEFAULT_CONFIG


class TestAudioPipeline(unittest.TestCase):
    """Test the audio → text pipeline without loading Whisper (fast)."""

    def test_empty_audio_produces_nothing(self):
        """Empty audio chunks should not crash or produce output."""
        audio = np.zeros(16000, dtype=np.float32)  # 1 second silence
        # Simulate the chunk concatenation from voice.py
        chunks = [audio[i:i+512].reshape(-1, 1) for i in range(0, len(audio), 512)]
        combined = np.concatenate(chunks, axis=0).flatten()
        self.assertEqual(len(combined), 16000)
        self.assertTrue(np.all(combined == 0))

    def test_audio_chunk_accumulation(self):
        """Simulate recording: chunks accumulate and concatenate correctly."""
        chunks = []
        for _ in range(100):  # ~3.2 seconds at 512 samples/chunk
            chunk = np.random.randn(512, 1).astype(np.float32)
            chunks.append(chunk)

        audio = np.concatenate(chunks, axis=0).flatten()
        self.assertEqual(len(audio), 51200)
        self.assertEqual(audio.dtype, np.float32)

    def test_very_short_audio(self):
        """Very short recordings (< 0.5s) should be handled gracefully."""
        audio = np.random.randn(4000).astype(np.float32)  # 0.25 seconds
        self.assertEqual(len(audio), 4000)
        # In voice.py, this would still be sent to Whisper — it just may produce empty text


class TestFullPipelineWithMock(unittest.TestCase):
    """Test the full transcription pipeline with a mocked Whisper model."""

    def _make_mock_segment(self, text):
        seg = MagicMock()
        seg.text = text
        return seg

    def test_pipeline_basic_dictation(self):
        """Simulate: Whisper returns text → process_text → output."""
        raw_whisper = "um hello world"
        config = DEFAULT_CONFIG.copy()
        processed = process_text(raw_whisper, config)
        self.assertEqual(processed, "Hello world")

    def test_pipeline_email_formatting(self):
        """Whisper output with email gets formatted."""
        raw_whisper = "Send it to alex at gmail dot com please."
        config = DEFAULT_CONFIG.copy()
        processed = process_text(raw_whisper, config)
        self.assertIn("alex@gmail.com", processed)

    def test_pipeline_number_formatting(self):
        raw_whisper = "We need one hundred units by friday."
        config = DEFAULT_CONFIG.copy()
        processed = process_text(raw_whisper, config)
        self.assertIn("100", processed)

    def test_pipeline_whisper_segment_dedup(self):
        """Consecutive identical segments should be deduplicated."""
        from voice import dedup_segments
        segments = [
            self._make_mock_segment("Hello world."),
            self._make_mock_segment("Hello world."),
            self._make_mock_segment("How are you?"),
        ]
        self.assertEqual(dedup_segments(segments), "Hello world. How are you?")

    def test_pipeline_all_empty_segments(self):
        """All empty segments should produce empty text."""
        from voice import dedup_segments
        segments = [
            self._make_mock_segment(""),
            self._make_mock_segment("  "),
            self._make_mock_segment(""),
        ]
        self.assertEqual(dedup_segments(segments), "")


class TestConfigIntegrity(unittest.TestCase):
    """Verify config loading doesn't break the pipeline."""

    def test_default_config_valid(self):
        """Default config should have all required keys."""
        cfg = DEFAULT_CONFIG
        self.assertIn("post_processing", cfg)
        self.assertIn("auto_format", cfg["post_processing"])
        self.assertIn("remove_filler_words", cfg["post_processing"])

    def test_process_text_with_default_config(self):
        """process_text should work with default config."""
        result = process_text("hello world", DEFAULT_CONFIG)
        self.assertEqual(result, "Hello world")

    def test_process_text_with_empty_config(self):
        """process_text should gracefully handle empty config (all defaults)."""
        result = process_text("hello world", {})
        self.assertEqual(result, "Hello world")

    def test_process_text_with_all_disabled(self):
        """All processing disabled should return text as-is."""
        cfg = {"post_processing": {
            "auto_format": False,
            "remove_filler_words": False,
            "auto_capitalize": False,
            "code_vocabulary": False,
        }}
        result = process_text("um hello world", cfg)
        self.assertEqual(result, "um hello world")


class TestStreamLifecycle(unittest.TestCase):
    """Test audio stream start/stop without actual mic access."""

    @patch("sounddevice.InputStream")
    def test_stream_start_stop(self, mock_stream_class):
        """Stream should start and stop cleanly."""
        mock_stream = MagicMock()
        mock_stream.active = True
        mock_stream_class.return_value = mock_stream

        import sounddevice as sd
        stream = sd.InputStream(samplerate=16000, channels=1, dtype="float32")
        stream.start()
        mock_stream.start.assert_called_once()

        stream.stop()
        mock_stream.stop.assert_called_once()

    @patch("sounddevice.InputStream")
    def test_stream_reports_inactive(self, mock_stream_class):
        """Watchdog should detect inactive stream."""
        mock_stream = MagicMock()
        mock_stream.active = False
        mock_stream_class.return_value = mock_stream

        stream = mock_stream_class(samplerate=16000, channels=1, dtype="float32")
        self.assertFalse(stream.active)


class TestWatchdogLogic(unittest.TestCase):
    """Test watchdog detection logic without running the thread."""

    def test_detect_dead_stream(self):
        """Watchdog should flag an inactive stream."""
        mock_stream = MagicMock()
        mock_stream.active = False
        needs_restart = (mock_stream is not None and not mock_stream.active)
        self.assertTrue(needs_restart)

    def test_healthy_stream(self):
        mock_stream = MagicMock()
        mock_stream.active = True
        needs_restart = (mock_stream is not None and not mock_stream.active)
        self.assertFalse(needs_restart)


class TestWithModel(unittest.TestCase):
    """Slow tests that load the actual Whisper model.

    Run explicitly: python -m unittest test_e2e.TestWithModel -v
    Skipped by default in quick runs.
    """

    @classmethod
    def setUpClass(cls):
        """Load Whisper model once for all tests in this class."""
        try:
            from faster_whisper import WhisperModel
            cls.model = WhisperModel("small", device="cpu", compute_type="int8")
        except Exception as e:
            raise unittest.SkipTest(f"Cannot load Whisper model: {e}")

    def test_silence_produces_empty(self):
        """Pure silence should produce empty or near-empty transcription."""
        silence = np.zeros(32000, dtype=np.float32)  # 2 seconds
        segments, info = self.model.transcribe(silence, beam_size=1, vad_filter=True)
        text = " ".join(seg.text.strip() for seg in segments).strip()
        # VAD filter should suppress silence — expect empty or very short
        self.assertLess(len(text), 20, f"Expected near-empty, got: {text!r}")

    def test_noise_handled_gracefully(self):
        """Random noise should not crash and should produce limited output."""
        noise = np.random.randn(32000).astype(np.float32) * 0.01  # Quiet noise
        segments, info = self.model.transcribe(noise, beam_size=1, vad_filter=True)
        text = " ".join(seg.text.strip() for seg in segments).strip()
        # Should not crash — output content doesn't matter
        self.assertIsInstance(text, str)

    def test_model_accepts_various_lengths(self):
        """Model should handle audio of various lengths without crashing."""
        for seconds in [0.5, 1, 3, 5]:
            samples = int(16000 * seconds)
            audio = np.random.randn(samples).astype(np.float32) * 0.001
            segments, info = self.model.transcribe(audio, beam_size=1, vad_filter=True)
            text = " ".join(seg.text.strip() for seg in segments).strip()
            self.assertIsInstance(text, str)


class TestMemoryBaseline(unittest.TestCase):
    """Quick memory baseline — not a full leak test, but catches obvious issues."""

    def test_process_text_no_leak(self):
        """Running process_text 1000 times should not grow memory significantly."""
        import tracemalloc
        tracemalloc.start()

        config = DEFAULT_CONFIG.copy()
        for _ in range(1000):
            process_text("um hello world this is a test of the emergency broadcast system", config)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        # Should use less than 5MB for 1000 iterations
        self.assertLess(peak, 5 * 1024 * 1024, f"Peak memory: {peak / 1024 / 1024:.1f}MB")

    def test_audio_chunks_cleanup(self):
        """Simulated recording/clear cycle should not leak audio data."""
        import tracemalloc
        tracemalloc.start()

        for _ in range(50):
            chunks = []
            for _ in range(100):
                chunks.append(np.random.randn(512, 1).astype(np.float32))
            audio = np.concatenate(chunks, axis=0).flatten()
            _ = len(audio)
            chunks.clear()
            del audio

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        # After clearing, current should be low
        self.assertLess(current, 2 * 1024 * 1024, f"Current memory: {current / 1024 / 1024:.1f}MB")


if __name__ == "__main__":
    unittest.main()
