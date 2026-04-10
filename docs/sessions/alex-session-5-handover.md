# Alex Session 5 Handover — 2026-04-09

## Branch
`master` — pushed to `origin/master`, up to date. No uncommitted changes.

## Repo
**https://github.com/Alex-Alternative/koda** — Working dir: `C:\Users\alex\Projects\koda`

## What Was Built This Session

### Phase 2 — Complete (commit 4620f7f)
1. **Floating status overlay** (`overlay.py`) — always-on-top widget
2. **Auto-formatting** (`text_processing.py`) — numbers, dates, smart punctuation, email addresses
3. **Per-app profiles** (`profiles.py`, `profiles.json`) — auto-switch by active window
4. **Audio file transcription** (`transcribe_file.py`) — GUI with browse/timestamps/save

### Phase 3 — Complete minus wake word (commits 1f75dad, 745aacb)
5. **Voice editing commands** (`voice_commands.py`) — 30+ commands (select all, undo, new line, etc.)
6. **Real-time translation** — Whisper native (→English) or Ollama LLM (→any language)
7. **Windows Explorer context menu** (`context_menu.py`) — right-click audio files → transcribe
8. **Koda.exe rebuilt** — 276MB with all Phase 1-3 features (NOTE: stale again, needs rebuild with small model)

### Phase 4 — Partial
9. **Usage stats dashboard** (`stats.py`, `stats_gui.py`) — words dictated, time saved, commands used, per-app breakdown, 7-day chart. Accessible from tray menu.
10. **Tray icon redesign** — multiple iterations, landed on: dark rounded square with Bahnschrift font "K" + colored status dot
11. **Floating overlay redesign** — same branded K icon, 48px, 85% opacity, transparent background for true rounded corners, draggable

### Critical Bugfixes
12. **Double/triple paste fix** — root cause was multiple Koda instances (python.exe from debug runs + pythonw.exe). Fixed with Windows mutex (`CreateMutexW`), also switched paste from `pyautogui.hotkey("ctrl","v")` to `keyboard.send("ctrl+v")` to avoid hook conflicts
13. **Sound playback fix** — switched from sounddevice (conflicts with mic stream) to winsound, removed SND_ASYNC flag (daemon thread killed sound before it played)
14. **Readback hotkey fix** — changed from Ctrl+Shift+R (conflicts with browser hard refresh) to Ctrl+Alt+R
15. **Whisper repetition fix** — enabled vad_filter, added segment deduplication
16. **Model upgrade** — switched from `base` to `small` for better accuracy (tried `large-v3-turbo` but too slow on CPU)
17. **Single-instance mutex** — prevents duplicate Koda processes
18. **Email auto-formatting** — "alex at gmail dot com" → "alex@gmail.com" (works in tests, BUG: not applying in live Koda — needs debugging)

## Decisions Made

1. **Model: `small` not `large-v3-turbo`** — large-v3-turbo was too slow on CPU (~4s for short phrases). Small is 4x better than base, fast enough. User has a GPU but CUDA driver is outdated.
2. **beam_size: 1** — fastest decoding, minimal accuracy loss with small model.
3. **Product Hunt launch moved to Phase 5+** — Alex wants thorough testing before any public launch. Multiple bugs found during first live testing session.
4. **Overlay: branded K icon** — went through 6+ iterations (text pill → mascot → mic+dot → branded K). Final design: dark rounded square, Bahnschrift "K", colored status dot. Same design for tray and floating overlay.
5. **Phone app: not now** — Koda's moat is desktop. iOS/Android dictation is too integrated to compete with. Maybe companion app later.
6. **Multi-user deployment** — Koda will be used by multiple people, accuracy matters more than speed.
7. **paste via `keyboard.send("ctrl+v")`** — pyautogui's synthetic Ctrl conflicts with keyboard library hooks, causing literal "v" character + separate paste.

## User Feedback & Corrections

1. **"Make it a big deal next time we have something overdue"** — don't bury stale builds in lists
2. **"Are we overcomplicating things?"** — user pushed back on excessive Whisper params (repetition_penalty etc.), wanted simplification
3. **"That's terrifying"** — mascot character overlay was rejected immediately
4. **"The K is too blocky"** — Segoe UI Bold K was too thick, switched to Bahnschrift (geometric, modern)
5. **"It's too see through" / "not rounded"** — overlay needed multiple fixes for opacity and true rounded corners
6. **Tray icon iterations** — user couldn't see K+soundwave at tray size, preferred simple bold color block initially, then settled on dark square with font-rendered K
7. **"It sits too low/high"** — overlay position went from 80px → 160px → 120px → 120px from bottom
8. **Readback hotkey conflict** — Ctrl+Shift+R triggers browser hard refresh, changed to Ctrl+Alt+R

## Waiting On

- **Dedicated microphone** — ordered, not arrived. Wake word (Porcupine) blocked on this.
- **CUDA driver update** — GPU exists but driver is outdated. Would enable large-v3-turbo at near-instant speed. User can run `nvidia-smi` to check GPU, update from NVIDIA site.
- **Email formatting bug** — works in direct Python tests but not in live Koda. Needs debugging (likely a code loading or pipeline issue).

## Next Session Priorities

### URGENT — Stale build artifacts
- **Koda.exe rebuild** — currently bundles base model + old code. Needs rebuild with small model + all Phase 2-4 features. Will be ~400MB+.

### Continue Phase 4
1. **Plugin/extension system** — not started
2. **MSI installer** — not started

### Bugs to fix
3. **Email auto-formatting** — not applying in live Koda (works in tests)
4. **Overlay drag** — user reported "can't drag it around like before" on one iteration. Verify drag works on current version.

### Polish
5. **README update** — doesn't mention any Phase 2-4 features
6. **Test coverage** — zero tests for new features this session

### Phase 5+ (after thorough testing)
7. Product Hunt launch prep
8. Landing page, screenshots, demo video
9. MSI installer for enterprise

## Files Changed This Session

| File | What changed |
|---|---|
| `overlay.py` | **6+ rewrites**: text pill → mascot → mic+dot → branded K with transparency |
| `voice.py` | Integrated stats, translation, voice commands, icon redesign (Bahnschrift K), single-instance mutex, paste fix (keyboard.send), sound fix (winsound), readback hotkey fix |
| `config.py` | Added: auto_format, overlay_enabled, profiles_enabled, voice_commands, translation, readback hotkeys changed to ctrl+alt+r/t |
| `config.json` | Model: small, readback hotkeys updated, overlay_enabled: true |
| `text_processing.py` | Added: format_spoken_numbers, format_spoken_dates, format_smart_punctuation, format_spoken_emails, fixed stutter removal |
| `stats.py` | **NEW** — Usage statistics tracking (SQLite) |
| `stats_gui.py` | **NEW** — Stats dashboard GUI (big numbers, 7-day chart, top apps/commands) |
| `voice_commands.py` | **NEW** — 30+ voice editing commands |
| `context_menu.py` | **NEW** — Windows Explorer right-click context menu |
| `profiles.py` | **NEW** — Per-app profile matching via ctypes window detection |
| `profiles.json` | **NEW** — Default app profiles |
| `transcribe_file.py` | **NEW** — Audio file transcription GUI |
| `custom_words.json` | Added Alt Funding, Flyland entries |
| `build_exe.py` | Updated to bundle all 11 modules |
| `.gitignore` | Added debug.log |

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
- **Ollama** at `C:\Users\alex\AppData\Local\Programs\Ollama\ollama.exe`, phi3:mini pulled
- **Python 3.14** — tflite-runtime has no wheels, openwakeword uses ONNX
- **mic_device = null** — don't hardcode indices, they shift
- **pyttsx3 COM threading** — must init lazily in the thread that uses it
- **Paste uses `keyboard.send("ctrl+v")`** NOT pyautogui — pyautogui conflicts with keyboard library hooks
- **Sound uses winsound** NOT sounddevice — sd conflicts with mic input stream
- **SND_ASYNC kills sound in daemon threads** — use synchronous play in thread instead
- **Single instance mutex** — `KodaVoiceAppMutex` via CreateMutexW. Handles stale mutexes.
- **Kill ALL python processes before restart** — `taskkill //f //im pythonw.exe` AND `taskkill //f //im python.exe`
- **Koda.exe stale** — needs rebuild with small model + all new features
- **GPU available but CUDA driver outdated** — could enable large-v3-turbo if updated
- **Product Hunt launch BLOCKED** — Alex wants thorough testing first, moved to Phase 5+
- **Flag overdue items loudly** — don't let stale builds slip between sessions
- **Tray icon: Bahnschrift K** on dark rounded square with colored status dot
- **Context menu installed** on this machine — right-click audio files works
- **Overlay: branded K icon**, 48px, 85% opacity, transparent corners, draggable

## Migration Status
None this session.

## Test Status
- Existing tests from session 3 unchanged
- Auto-formatting tested extensively inline (numbers, dates, punctuation, emails)
- Voice commands tested via mock (12 cases)
- Profile matching tested via mock
- **No new test files written** — coverage gap for all Phase 2-4 features
- **Live testing revealed:** double-paste bug, sound not playing, model too slow, email formatting not applying
