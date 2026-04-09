# Alex Session 2 Handover — 2026-04-09

## Branch
`master` — pushed to `origin/master`, up to date. No uncommitted changes (config.json is gitignored).

## Repo
**https://github.com/Alex-Alternative/koda** — Working dir: `C:\Users\alex\whisper-setup`

## What Was Built This Session

### Wake Word System (openwakeword)
- Replaced broken Whisper-based wake word detection with **openwakeword** — a proper tiny neural network like Alexa/Siri
- Uses ONNX backend (tflite doesn't work on Python 3.14)
- Audio normalization to handle quiet mics
- Currently using "alexa" pre-trained model as placeholder (confirmed working at 0.88 score)
- **Currently disabled** in config — false triggers from ambient noise (phone notifications, music, keystrokes) on the Jabra headset. Needs dedicated mic.
- Files: wake word code in `voice.py`, test script at `test_wakeword.py`

### Read-Back / Text-to-Speech
- **Ctrl+Shift+R** — reads last transcription aloud using Windows SAPI via pyttsx3
- **Ctrl+Shift+T** — reads whatever text is selected on screen aloud
- Press either hotkey again while reading to stop
- Icon turns purple while reading
- TTS engine initialized lazily to avoid COM threading conflicts that were freezing the paste function

### Single .exe Build
- `build_exe.py` script creates standalone `Koda.exe` via PyInstaller
- Output: `dist/Koda.exe` (148MB)
- Bundles all Python deps but Whisper model still downloads on first run (~150MB)
- Build artifacts (build/, dist/, *.spec) added to .gitignore

### Bug Fixes
- **VAD filter disabled for transcription** — was killing short phrases like "yes", "are you working". Whisper's vad_filter=True strips audio it thinks is silence, which included short utterances on quiet mics.
- **Beam size reduced to 3** (from 5) for faster transcription
- **TTS lazy initialization** — pyttsx3 uses COM objects that caused threading deadlocks when initialized at startup. Now initialized on first use.
- **Mic device index shifting** — device indices change when audio devices are added/removed. Setting `mic_device: null` (system default) is more reliable than hardcoding an index.

## Decisions Made

1. **Wake word disabled for now** — Whisper-based approach was fundamentally wrong (hallucinations, false triggers). Switched to openwakeword (proper approach) but the Jabra headset picks up too much ambient noise causing false triggers. Will revisit when dedicated mic arrives.

2. **"Alexa" as temporary wake word model** — openwakeword has pre-trained models for "alexa", "hey_jarvis", "hey_mycroft". Custom "Hey Koda" model needs training. "Alexa" was confirmed working at 0.88 detection score.

3. **LLM polish disabled by default** — When Ollama isn't running, the LLM polish call hangs silently, preventing paste from working. Kept disabled unless user explicitly enables it and has Ollama running.

4. **VAD filter turned off for transcription** — Short phrases were being lost. The energy-based VAD for auto-stop recording (toggle mode) is separate and still works.

5. **System beeps for wake word confirmation** — .wav files play through the default audio output which might not be the Jabra. `winsound.Beep()` goes through the PC speaker and is always audible. But user found the high pitch (1000/1200 Hz) annoying — lowered to 500/600 Hz.

## User Feedback & Corrections

- **Very frustrated with wake word false triggers** — "it keeps beeping like a heart monitor", "its beeping and I am not saying anything!", "fuck this is annoying". The Whisper-based approach was wrong; openwakeword is right but needs a better mic.
- **High-pitched beeps are annoying** — Lowered confirmation beeps from 1000/1200 Hz to 500/600 Hz.
- **Short phrases not pasting** — "if I only say 'are you working' it doesn't do anything". Fixed by disabling Whisper VAD filter.
- **App stopped pasting after read-back** — pyttsx3 COM threading froze the app. Fixed with lazy init.
- **Mic device index unreliable** — Use `null` (system default) not hardcoded numbers. Indices shift when devices are added/removed.
- **User switched from Jabra headset to regular speakers** mid-session, which changed the default audio device.

## Waiting On

1. **Dedicated microphone** — User ordered one. Critical for wake word reliability. The Jabra headset picks up too much ambient noise.

## Current Config State (config.json)
```json
{
  "hotkey_dictation": "ctrl+space",
  "hotkey_command": "ctrl+shift+.",
  "hotkey_correction": "ctrl+shift+z",
  "hotkey_readback": "ctrl+shift+r",
  "hotkey_readback_selected": "ctrl+shift+t",
  "mic_device": null,
  "wake_word": { "enabled": false },
  "llm_polish": { "enabled": false }
}
```

## Next Session Priorities

1. **Train custom "Hey Koda" wake word** — Use openwakeword's `train_custom_verifier` to train from user voice samples. Needs the dedicated mic.
2. **Stop word** — Voice command to end recording (e.g., "Koda stop", "Over", "That's all"). Needs deep reasoning on what phrase won't conflict with normal speech.
3. **Test LLM polish** — Enable Ollama, test the prompt cleanup with Ctrl+Shift+Period. Make sure Ollama auto-starts or show clear error if not running.
4. **Fix .wav sound routing** — Sounds play through default output (PC speakers) not necessarily through the active headset. Consider using system beeps as fallback or detecting audio output device.
5. **Update README** — Add read-back hotkeys, Ollama instructions, current hotkey reference.
6. **Rebuild Koda.exe** — Current .exe doesn't include today's fixes (TTS, VAD filter fix).
7. **Clean up test files** — `test_wake.wav`, `test_wakeword.py` in repo root.

## Files Changed This Session

| File | Description |
|---|---|
| `voice.py` | Added openwakeword wake word, read-back TTS, lazy TTS init, VAD filter fix |
| `config.py` | Added readback hotkey defaults |
| `config.json` | Updated with new hotkeys, wake word disabled, LLM disabled |
| `build_exe.py` | PyInstaller build script |
| `test_wakeword.py` | Interactive wake word test (step-by-step with Enter prompts) |
| `sounds/wakeword.wav` | Distinct wake word confirmation chime |
| `requirements.txt` | Added pyttsx3 |
| `.gitignore` | Added build/, dist/, *.spec |

## Key Reminders

- **Python 3.14** — tflite-runtime has no wheels. openwakeword must use `inference_framework='onnx'`.
- **Mic device = null** — Don't hardcode device indices. They shift when hardware changes.
- **LLM polish + Ollama** — Ollama must be running (`ollama serve`) before enabling LLM polish. If it's not running, paste silently fails. Ollama is at `C:\Users\alex\AppData\Local\Programs\Ollama\ollama.exe`. Model `phi3:mini` is already pulled.
- **pyttsx3 COM threading** — Must be initialized lazily in the thread that uses it, not at startup. Otherwise it deadlocks the paste function.
- **Wake word normalization** — Quiet mics (Jabra at desk distance) need audio normalized before feeding to openwakeword. But normalizing amplifies background noise causing false triggers. Need a proper mic to solve this tradeoff.
- **GitHub CLI** at `"C:\Program Files\GitHub CLI\gh.exe"`, authenticated as `Alex-Alternative`.
- **User is on regular speakers now** (not Jabra). Default audio devices may have changed.

## Migration Status
None — no database involved.

## Test Status
- `test_stress.py` — still references "Voice-to-Claude", needs Koda rename
- `test_wakeword.py` — new, interactive wake word test, works
- No automated CI
