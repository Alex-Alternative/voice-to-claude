# Alex Session 3 Handover — 2026-04-09

## Branch
`master` — pushed to `origin/master`, up to date.

## Repo
**https://github.com/Alex-Alternative/koda** — Working dir: `C:\Users\alex\Projects\koda` (moved from whisper-setup this session)

## What Was Built This Session

### Session 2 carryover (morning)
- **Wake word (openwakeword)** — Replaced broken Whisper-based approach with proper neural network. Works but disabled due to false triggers from ambient noise. Needs dedicated mic.
- **Read-back TTS** — Ctrl+Shift+R reads last transcription, Ctrl+Shift+T reads selected text
- **Koda.exe** — 276MB standalone with bundled Whisper model
- **Settings GUI** — Dark-themed tkinter window, desktop shortcut
- **Bug fixes** — TTS lazy init (COM threading), VAD filter disabled for short phrases, sound routing via sounddevice

### Session 3 features (afternoon)
1. **TTS speed control** — Slow/Normal/Fast in tray menu and settings GUI
2. **Multi-language support** — 15 languages + auto-detect in settings
3. **Custom vocabulary / hot words** — `custom_words.json` for word replacements, Whisper initial_prompt bias
4. **Clipboard mode** — Toggle between auto-paste and clipboard-only output
5. **Transcript history** — SQLite database (`history.py`), saves all transcriptions with timestamps
6. **Faster model options** — Added distil-large-v3, large-v3-turbo, distil-medium.en
7. **Installer updates** — All branded Koda, mentions settings GUI
8. **Stress test updates** — TTS and sound file tests added
9. **README updates** — Settings GUI, streaming, speed control, .exe distribution docs
10. **Desktop shortcuts** — "Koda" (launches app) + "Koda Settings" (opens GUI)

### Market Research
- Full competitor analysis saved in agent output (Dragon, Otter, Whisper-writer, Windows Dictation, Talon, etc.)
- Koda's unique position: only tool combining local/private + push-to-talk + code-aware + LLM polish + free
- Top recommended pitch: "Free, private, AI-powered voice input for developers and power users"

## Venv Recreated
**IMPORTANT:** The venv was recreated after moving from whisper-setup to Projects/koda. All deps are installed. The `start.bat` and shortcuts point to the new location. If anything breaks, run:
```
cd C:\Users\alex\Projects\koda
python -m venv venv --clear
venv\Scripts\activate
pip install -r requirements.txt
pip install pyttsx3 openwakeword pyinstaller
```

## Current Config State
```json
{
  "hotkey_dictation": "ctrl+space",
  "hotkey_command": "ctrl+shift+.",
  "hotkey_correction": "ctrl+shift+z",
  "hotkey_readback": "ctrl+shift+r",
  "hotkey_readback_selected": "ctrl+shift+t",
  "mic_device": null,
  "output_mode": "auto_paste",
  "streaming": true,
  "wake_word": { "enabled": false },
  "llm_polish": { "enabled": false }
}
```

## Phased Roadmap (from market research)

### Phase 2 — Medium effort (next)
- Floating status widget / mini overlay
- Per-app profiles (auto-switch by active window)
- Auto-formatting rules (numbers, dates, smart punctuation)
- Audio file transcription (drag-and-drop)

### Phase 3 — Bigger builds
- Voice editing commands ("select all", "delete that", "undo")
- Real-time translation (speak Spanish → type English)
- Wake word via Porcupine (proper engine)
- Windows context menu ("Transcribe with Koda")

### Phase 4 — Polish & Growth
- Usage stats dashboard
- Plugin/extension system
- Product Hunt launch prep
- MSI installer for enterprise

## Key Reminders
- **Venv was recreated** — all deps installed at `C:\Users\alex\Projects\koda\venv`
- **Desktop is at** `C:\Users\alex\OneDrive\Desktop`
- **GitHub CLI** at `"C:\Program Files\GitHub CLI\gh.exe"`, auth as `Alex-Alternative`
- **Ollama** at `C:\Users\alex\AppData\Local\Programs\Ollama\ollama.exe`, phi3:mini pulled
- **Python 3.14** — tflite-runtime has no wheels, openwakeword uses ONNX
- **mic_device = null** — don't hardcode indices, they shift
- **pyttsx3 COM threading** — must init lazily in the thread that uses it
- **LLM polish** — disable by default, Ollama must be running or paste silently fails
- **Dedicated mic** ordered but not arrived — wake word blocked on this
- **Koda.exe** at `dist/Koda.exe` (276MB) — needs rebuild after today's 5 new features

## Files Changed This Session
| File | What changed |
|---|---|
| `voice.py` | Streaming transcription, wake word (openwakeword), TTS speed, custom vocab, clipboard mode, history integration, multi-language auto-detect |
| `config.py` | Added output_mode, streaming, tts defaults, custom_words_file |
| `text_processing.py` | Added apply_custom_vocabulary() |
| `settings_gui.py` | TTS speed dropdown, voice selection, output mode, language expansion, custom words button, model options |
| `configure.py` | Updated model choices, Koda branding, settings GUI mention |
| `history.py` | NEW — SQLite transcript history module |
| `custom_words.json` | NEW — user-editable word replacements |
| `build_exe.py` | Bundle Whisper model into .exe |
| `test_stress.py` | TTS and sound file tests |
| `install.bat` | Koda branding, settings GUI tip |
| `.gitignore` | Added koda_history.db |
| `README.md` | Settings GUI, streaming, speed control, .exe distribution |
| `settings.bat` | NEW — launcher for settings GUI |
| `settings_gui.py` | NEW — tkinter settings window |
| `sounds/wakeword.wav` | NEW — wake word confirmation chime |
| `test_wakeword.py` | NEW — interactive wake word test |

## Test Status
- Push-to-talk working (Ctrl+Space)
- Streaming preview in tray tooltip
- Settings GUI opens from desktop shortcut
- voice.py launches cleanly after venv rebuild
- Koda.exe needs rebuild to include today's features
