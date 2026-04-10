# Alex Session 6 Handover — 2026-04-10

## Branch
`master` — 1 unpushed commit (`479e3df`). Run `git push origin master` to sync.

## Repo
**https://github.com/Alex-Alternative/koda** — Working dir: `C:\Users\alex\Projects\koda`

## What Was Built This Session

### Phase 4 Completion
1. **Plugin/extension system** (`plugin_manager.py`, `plugins/`) — drop .py files in plugins/ to extend Koda with custom text processors, voice commands, and tray menu items. Example plugin included (.disabled).
2. **Koda.exe rebuilt** — 576MB with small model + all Phase 1-4 features + reliability fixes

### Phase 5 — Reliability & Testing (mostly complete)
3. **Email formatting bug fixed** (`text_processing.py`) — root cause: `format_spoken_emails` did exact `== "dot"` comparison without stripping trailing punctuation. Whisper's small model adds commas/periods (`"dot,"`, `"dot."`), causing match failure. Fixed with `_strip_punct()` helper.
4. **Health watchdog thread** — checks every 15 seconds: audio stream alive? keyboard hooks alive? Auto-recovers both. Logs heartbeat every 5 minutes with hook count, stream status, memory.
5. **Exception logging** — replaced ~15 bare `except: pass` with logged exceptions. Failures now visible in debug.log.
6. **Error notifications** — `error_notify()` shows Windows tray balloons for: transcription failures, mic disconnect, model load failure, hotkey loss + recovery.
7. **Hotkey robustness** — try/except around registration, clear hooks before re-registering, track state, log each registration.
8. **Robust single-instance mutex** — uses WMIC to find stale Koda by command line (`voice.py`), not just any pythonw.exe. Auto-kills stale instances.
9. **Debug logging** — Koda logger at DEBUG, library noise at WARNING. Captures Whisper raw output, pipeline stages, hotkey registration, watchdog heartbeats.
10. **98 tests** — 77 unit tests (`test_features.py`) + 21 e2e tests (`test_e2e.py`) including memory baselines and real Whisper model tests.
11. **Inno Setup installer** (`installer/koda.iss`, `installer/build_installer.py`) — ready to compile when Inno Setup 6 is installed. Creates proper Windows installer with Start Menu, desktop shortcut, auto-start, uninstaller.
12. **README rewrite** — complete documentation of all Phase 2-4 features.
13. **Version bumped to 4.0.0**

### Critical Bugfixes
14. **Email auto-formatting** — punctuation-tolerant keyword matching (the main bug from session 5)
15. **Readback hotkeys** — fixed default to `ctrl+alt+r` / `ctrl+alt+t` (was still `ctrl+shift+r` in some places)
16. **Logging noise** — fixed basicConfig level so PIL debug spam doesn't flood debug.log

## Known Issue — Hotkey Drops

**The biggest unresolved issue**: Koda's keyboard hooks sometimes die silently mid-session. The watchdog detects and recovers, but the root cause is likely the **GIL + Windows hook timeout** problem:

- Windows low-level keyboard hooks (WH_KEYBOARD_LL) have a strict message response timeout
- When Whisper transcribes (CPU-intensive), it holds Python's GIL
- The keyboard library's hook thread can't respond to Windows messages fast enough
- Windows silently removes the hooks

**Current mitigation**: Watchdog checks every 15 seconds and re-registers hooks if lost. User sees a tray notification "Hotkeys recovered."

**Permanent fix options** (for next session):
1. Run the keyboard hook in a separate **process** (not thread) — immune to GIL
2. Use `ctypes` to create a native Windows hook that doesn't go through Python
3. Use `pynput` instead of `keyboard` — different hook implementation
4. Add `keyboard._listener.start()` re-init after each transcription

## Decisions Made

1. **Plugin system**: simple file-based discovery, no class inheritance needed. Hooks: process_text, get_commands, get_menu_items, on_load/on_unload.
2. **Watchdog interval**: 15 seconds (was 30). Balance between responsiveness and CPU.
3. **Error notifications**: always shown (not gated by config.notifications). Users need to see errors.
4. **Inno Setup** over NSIS/WiX — industry standard for Windows apps, free, well-documented.
5. **No Product Hunt yet** — needs the hotkey drop issue fully resolved first.

## Waiting On

- **Inno Setup 6 installation** — needed to compile the .exe installer
- **Hotkey drop permanent fix** — GIL/hook timeout root cause
- **CUDA driver update** — would enable large-v3-turbo model
- **Dedicated microphone** — for wake word testing

## Next Session Priorities

### CRITICAL — Hotkey reliability
1. **Fix GIL/hook timeout issue** — permanent solution, not just watchdog recovery
2. **Test the watchdog recovery** — let Koda run, check debug.log for heartbeats and any hook recovery events

### Phase 5 Remaining
3. **Install Inno Setup** and compile the actual installer
4. **More e2e testing** — test with real speech WAV files

### Phase 6 — GPU & Performance
5. **CUDA driver update** → enable large-v3-turbo
6. **Benchmark model sizes**
7. **Reduce exe size** (576MB is large)

### Phase 7 — Polish & Distribution
8. **Landing page / screenshots / demo video**
9. **Auto-update mechanism**
10. **First-run wizard improvements**

## Files Changed This Session

| File | What changed |
|---|---|
| `text_processing.py` | Email formatting bug fix — `_strip_punct()` helper for punctuation-tolerant keyword matching |
| `voice.py` | v4.0.0: debug logging, plugin integration, watchdog, error notifications, robust mutex, hotkey improvements, PyInstaller model loading |
| `voice_commands.py` | `register_extra_commands()` for plugin voice commands |
| `build_exe.py` | Small model path, added stats/plugin modules, plugins dir |
| `README.md` | Complete rewrite with all Phase 2-4 features |
| `.gitignore` | Added `_model_*/` |
| `plugin_manager.py` | **NEW** — Plugin discovery, loading, hook dispatch |
| `plugins/__init__.py` | **NEW** — Plugin directory marker |
| `plugins/example_plugin.py.disabled` | **NEW** — Example plugin template |
| `test_features.py` | **NEW** — 77 unit tests for Phase 2-4 |
| `test_e2e.py` | **NEW** — 21 e2e tests + memory baselines |
| `installer/koda.iss` | **NEW** — Inno Setup installer script |
| `installer/build_installer.py` | **NEW** — Installer build automation |

## Current Config State
```json
{
  "model_size": "small",
  "language": "en",
  "hotkey_dictation": "ctrl+space",
  "hotkey_command": "ctrl+shift+.",
  "hotkey_correction": "ctrl+shift+z",
  "hotkey_readback": "ctrl+alt+r",
  "hotkey_readback_selected": "ctrl+alt+t",
  "hotkey_mode": "hold",
  "mic_device": null,
  "sound_effects": true,
  "overlay_enabled": true,
  "profiles_enabled": true,
  "voice_commands": true,
  "translation": { "enabled": false, "target_language": "English" },
  "post_processing": { "remove_filler_words": true, "code_vocabulary": false, "auto_capitalize": true, "auto_format": true }
}
```

## Key Reminders

- **Venv** at `C:\Users\alex\Projects\koda\venv` — all deps installed
- **Desktop** is at `C:\Users\alex\OneDrive\Desktop` (OneDrive sync)
- **GitHub CLI** at `"C:\Program Files\GitHub CLI\gh.exe"`, auth as `Alex-Alternative`
- **Python 3.14** — tflite-runtime has no wheels, openwakeword uses ONNX
- **mic_device = null** — don't hardcode indices, they shift
- **pyttsx3 COM threading** — must init lazily in the thread that uses it
- **Paste uses `keyboard.send("ctrl+v")`** NOT pyautogui
- **Sound uses winsound** NOT sounddevice
- **Kill ALL python processes before restart** — `taskkill //f //im pythonw.exe` AND `taskkill //f //im python.exe`
- **1 unpushed commit** — `git push origin master`
- **Koda.exe stale again** — watchdog improvements not in exe, needs rebuild after hotkey fix
- **Flag overdue items loudly**
- **DO NOT suggest Product Hunt** — needs hotkey fix first

## Test Status
- 77 unit tests (test_features.py) — all passing
- 21 e2e tests (test_e2e.py) — all passing, includes real Whisper model tests
- Memory baseline tests included — no leaks detected
- Live testing: email formatting confirmed working, hotkey drops still occur
