"""Test wake word detection. Run this and follow the prompts."""
import sounddevice as sd
import numpy as np
import time
import threading

print()
print("=" * 50)
print("  KODA WAKE WORD TEST")
print("=" * 50)
print()

# Show mic info
idx = sd.default.device[0]
dev = sd.query_devices(idx)
print(f"Using mic: {dev['name']}")
print()

# Step 1: Test mic volume
input("Press ENTER, then say something into your mic...")
print("Recording 4 seconds...")
buf = []
lock = threading.Lock()
def cb(indata, frames, ti, status):
    with lock:
        buf.append(indata.copy())

stream = sd.InputStream(samplerate=16000, channels=1, dtype='float32', callback=cb)
stream.start()
time.sleep(4)
stream.stop()
stream.close()

with lock:
    audio = np.concatenate(buf, axis=0).flatten()

peak = np.max(np.abs(audio))
print(f"Peak volume: {peak:.4f}")
if peak < 0.01:
    print("** VERY QUIET — your mic might be muted or wrong device **")
elif peak < 0.05:
    print("** Quiet — try speaking louder or moving closer **")
else:
    print("** Good volume! **")
print()

# Step 2: Test Whisper
print("Testing speech recognition...")
from faster_whisper import WhisperModel
model = WhisperModel('base', device='cpu', compute_type='int8')
segs, _ = model.transcribe(audio, beam_size=5, language='en')
text = ' '.join(s.text for s in segs).strip()
print(f'Whisper heard: "{text}"')
print()

# Step 3: Test wake word model
print("Now testing wake word model...")
print()
input('Press ENTER, then say "ALEXA" clearly...')
print("Recording 5 seconds...")

buf2 = []
def cb2(indata, frames, ti, status):
    with lock:
        buf2.append(indata.copy())

stream = sd.InputStream(samplerate=16000, channels=1, dtype='float32', callback=cb2)
stream.start()
time.sleep(5)
stream.stop()
stream.close()

with lock:
    audio2 = np.concatenate(buf2, axis=0).flatten()

peak2 = np.max(np.abs(audio2))
print(f"Peak: {peak2:.4f}")

from openwakeword.model import Model as OWW
oww = OWW(wakeword_models=['alexa_v0.1'], inference_framework='onnx')

# Normalize
if peak2 > 0.001:
    audio_norm = audio2 / peak2 * 0.9
else:
    audio_norm = audio2
audio_int16 = (audio_norm * 32767).astype(np.int16)

max_score = 0
for i in range(0, len(audio_int16) - 1280, 1280):
    oww.predict(audio_int16[i:i+1280])
    for name, scores in oww.prediction_buffer.items():
        if scores and scores[-1] > max_score:
            max_score = scores[-1]

print(f"Wake word score: {max_score:.4f} (need > 0.5 for detection)")
if max_score > 0.5:
    print("** DETECTED! Wake word works! **")
elif max_score > 0.2:
    print("** Close but not confident enough. Try speaking louder/clearer. **")
else:
    print("** Not detected. The model didn't hear the wake word. **")

print()
input("Press ENTER to exit...")
