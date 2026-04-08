# Voice-to-Claude

Push-to-talk voice input for [Claude Code](https://claude.ai/claude-code). Speak into your microphone and your words get transcribed and pasted directly into Claude Code (or any active window).

Runs locally using [OpenAI Whisper](https://github.com/openai/whisper) — no cloud API, no cost, fully offline after initial setup.

---

## Features

- **Two modes** — F9 for dictation (raw speech), F10 for commands (cleaned up for coding)
- **Hold-to-talk or Toggle** — Hold the key, or press once and it auto-stops when you stop speaking
- **Smart cleanup** — Removes filler words ("um", "uh", "you know"), fixes capitalization
- **Code vocabulary** — Say "open paren" and get `(`, say "camel case user name" and get `userName`
- **Sound effects** — Audio beeps confirm when recording starts, stops, and text is pasted
- **Notifications** — Windows toast popup shows what was transcribed
- **Noise reduction** — Optional background noise filtering for open offices
- **System tray app** — Runs silently in the background with a color-coded status icon
- **VAD auto-stop** — Voice Activity Detection automatically stops recording when you stop talking
- **Settings menu** — Right-click the tray icon to toggle features on/off
- **Offline** — All processing happens locally on your machine
- **Auto-start** — Optional Windows startup integration

---

## Requirements

- **Windows 10 or 11**
- **Python 3.10 or newer** — [Download here](https://www.python.org/downloads/)
  - During installation, **check "Add Python to PATH"**
- **A microphone** (built-in, USB, or headset)
- **~500MB disk space** (for Python packages + Whisper model)

---

## Installation

### Step 1: Download

Clone this repository or download and extract the ZIP:

```
git clone https://github.com/Alex-Alternative/voice-to-claude.git
cd voice-to-claude
```

Or click the green **Code** button on GitHub → **Download ZIP** → extract to a folder like `C:\voice-to-claude`.

### Step 2: Run the installer

1. Open the folder in File Explorer
2. **Double-click `install.bat`**
3. Wait for it to finish (installs dependencies + downloads the Whisper model)

That's it. You'll see "Installation complete!" when done.

### Step 3: Verify (optional)

Double-click **`test.bat`** to run the stress test. It checks your mic, audio capture, Whisper model, clipboard, keyboard hooks, and runs a full end-to-end test. All tests should show `[PASS]`.

---

## Usage

### Starting Voice-to-Claude

**Double-click `start.bat`**

A microphone icon will appear in your system tray (bottom-right of your screen, near the clock). You may need to click the **^** arrow to see it.

| Icon Color | Status |
|---|---|
| Gray | Loading model (wait ~10 seconds) |
| Green | Ready — press a hotkey to talk |
| Red | Recording your voice |
| Orange | Transcribing your speech |

### Hotkey Reference

| Key | Mode | What it does |
|---|---|---|
| **F9** | Dictation | Light cleanup — filler removal + capitalization |
| **F10** | Command | Full cleanup — fillers + code vocabulary + formatting |

**Default behavior is hold-to-talk:** hold the key while speaking, release to transcribe.

You can switch to **toggle mode** via the tray menu — press once to start, recording auto-stops when you stop speaking (VAD).

### Speaking a command

1. Open Claude Code (or any terminal/app where you want the text)
2. Make sure the target window is focused
3. **Hold `F9`** (or `F10` for command mode) and speak your message
4. **Release** — your speech is transcribed, cleaned up, and pasted

### Right-click tray menu

Right-click the tray icon to access:

- **Toggle sound effects** on/off
- **Toggle notifications** on/off
- **Toggle filler word removal** on/off
- **Toggle code vocabulary** on/off (for command mode)
- **Toggle noise reduction** on/off
- **Switch between Hold and Toggle mode**
- **Open settings file** (config.json for advanced options)
- **Quit**

---

## Configuration

All settings are stored in `config.json` (created automatically on first run). You can edit it directly or use the tray menu for common toggles.

```json
{
  "model_size": "base",
  "language": "en",
  "hotkey_dictation": "f9",
  "hotkey_command": "f10",
  "hotkey_mode": "hold",
  "mic_device": null,
  "sound_effects": true,
  "notifications": true,
  "noise_reduction": false,
  "post_processing": {
    "remove_filler_words": true,
    "code_vocabulary": false,
    "auto_capitalize": true
  },
  "vad": {
    "enabled": true,
    "silence_timeout_ms": 1500
  }
}
```

### Config options explained

| Setting | Default | Description |
|---|---|---|
| `model_size` | `"base"` | Whisper model: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `language` | `"en"` | Speech language ([supported languages](https://github.com/openai/whisper#available-models-and-languages)) |
| `hotkey_dictation` | `"f9"` | Hotkey for dictation mode |
| `hotkey_command` | `"f10"` | Hotkey for command mode |
| `hotkey_mode` | `"hold"` | `"hold"` (hold-to-talk) or `"toggle"` (press to start, auto-stops) |
| `mic_device` | `null` | Microphone device index or `null` for system default |
| `sound_effects` | `true` | Play beeps on record/stop/paste |
| `notifications` | `true` | Show Windows toast with transcribed text |
| `noise_reduction` | `false` | Filter background noise (slower, enable for noisy offices) |
| `remove_filler_words` | `true` | Strip "um", "uh", "you know", etc. |
| `code_vocabulary` | `false` | Expand "open paren" → `(`, case formatting commands |
| `auto_capitalize` | `true` | Fix sentence capitalization |
| `vad.enabled` | `true` | Voice Activity Detection for auto-stop in toggle mode |
| `vad.silence_timeout_ms` | `1500` | How long to wait after silence before auto-stopping (ms) |

### Changing hotkeys

Edit `config.json` and change `hotkey_dictation` or `hotkey_command`:

```json
"hotkey_dictation": "f8",
"hotkey_command": "f9"
```

Examples: `"f8"`, `"scroll lock"`, `"ctrl+shift+space"`

Save and restart Voice-to-Claude.

### Whisper model sizes

| Model | Size | Speed | Accuracy | Best for |
|---|---|---|---|---|
| `tiny` | ~75MB | Fastest | Lower | Quick commands, fast machine |
| `base` | ~150MB | Fast | Good | **Recommended default** |
| `small` | ~500MB | Medium | Better | Detailed dictation |
| `medium` | ~1.5GB | Slower | High | Long-form speech |
| `large-v3` | ~3GB | Slowest | Highest | Maximum accuracy (needs good CPU/GPU) |

---

## Code Vocabulary (Command Mode)

When code vocabulary is enabled (via tray menu or config), these spoken words get expanded in **command mode (F10)**:

| You say | You get |
|---|---|
| "open paren" | `(` |
| "close paren" | `)` |
| "open bracket" | `[` |
| "close bracket" | `]` |
| "open brace" | `{` |
| "close brace" | `}` |
| "semicolon" | `;` |
| "equals" | `=` |
| "double equals" | `==` |
| "arrow" | `->` |
| "fat arrow" | `=>` |
| "new line" | actual line break |
| "hash" | `#` |
| "pipe" | `\|` |

### Case formatting

| You say | You get |
|---|---|
| "camel case user name" | `userName` |
| "snake case get user data" | `get_user_data` |
| "pascal case my component" | `MyComponent` |
| "kebab case page title" | `page-title` |
| "screaming snake max retries" | `MAX_RETRIES` |

---

## Auto-Start with Windows

To launch Voice-to-Claude automatically when you log in:

1. Double-click **`install_startup.bat`**

To remove it from startup:

1. Double-click **`uninstall_startup.bat`**

---

## Troubleshooting

### "No speech detected"
- Check your microphone is set as the default input device in Windows Sound Settings
- Speak closer to the mic or louder
- Run `test.bat` to verify your mic is capturing audio

### Tray icon doesn't appear
- Check the **^** arrow in the system tray for hidden icons
- Make sure no error window popped up behind other windows
- Try running from a terminal to see errors:
  ```
  cd C:\voice-to-claude
  venv\Scripts\activate
  python voice.py
  ```

### F9/F10 doesn't trigger recording
- Some apps may intercept these keys — change the hotkey in `config.json`
- The `keyboard` library may need Administrator privileges on some systems. Try right-clicking `start.bat` → **Run as administrator**

### Transcription is slow
- Switch to the `tiny` model in `config.json`
- Close other CPU-heavy applications
- The first transcription after startup is always slower (model warm-up)

### Wrong microphone is being used
- Open Windows **Settings → System → Sound → Input** and set your preferred microphone as default
- Or set `mic_device` in `config.json` to the device index number

### Toggle mode doesn't auto-stop
- Make sure `vad.enabled` is `true` in `config.json`
- Try increasing `vad.silence_timeout_ms` if it stops too early
- Try decreasing it if it takes too long to stop

---

## Files

| File | Purpose |
|---|---|
| `voice.py` | Main application |
| `config.py` | Configuration management |
| `text_processing.py` | Post-transcription text cleanup |
| `config.json` | Your settings (auto-created on first run) |
| `install.bat` | One-time installer |
| `start.bat` | Launches Voice-to-Claude |
| `test.bat` | Runs the stress test suite |
| `test_stress.py` | Stress test script |
| `install_startup.bat` | Adds to Windows startup |
| `uninstall_startup.bat` | Removes from Windows startup |
| `requirements.txt` | Python package list |

---

## License

MIT
