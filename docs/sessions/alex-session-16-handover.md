# Alex Session 16 Handover — 2026-04-12

## Branch
`master` — all Phase 12 work was already committed. Session 16 changes are **uncommitted**:
- `voice.py` — mic disconnect detection rewrite
- `settings_gui.py` — scrollable settings window
- `STATUS.md` — new compact session-start file (untracked)
- `filler_words.json` — created by Alexi saving Settings (untracked)
- `config.json` — minor changes (untracked)

**Nothing pushed this session.** Commit before next session.

---

## What Was Built This Session

### 1. STATUS.md — Compact Session Start File (NEW)
`STATUS.md` created in project root. ~50 lines. Replaces reading the full handover doc at session start.
Contains: phase status table, next session actions, non-obvious reminders, key file sizes.
Memory updated: `MEMORY.md` now points to STATUS.md as the session start document.
Memory file created: `project_koda.md` in `.claude/projects/.../memory/`.

### 2. Settings Window — Scrollable Canvas (settings_gui.py)
**Problem:** Settings window was fixed at 1750px tall with no scrollbar. On 1080p screens, the bottom half
(Filler Words, Snippets, Per-App Profiles) was cut off and unreachable.

**Fix:**
- Removed `self.geometry("520x1750")` and `self.resizable(False, False)`
- Added a `tk.Canvas` + `ttk.Scrollbar` wrapping the content frame
- Window now sizes to `min(screen_height - 80, 900)` at startup
- Mouse wheel scrolling bound via `canvas.bind_all("<MouseWheel>", ...)`
- Content frame width tracks canvas width via `<Configure>` event

**Result:** Settings window is now scrollable, fits any screen, all sections accessible.
Window opens slightly narrow — Alexi noted it and said we'll fix sizing in a later session.

### 3. Exe Build — dist/Koda.exe (525 MB)
Built `dist/Koda.exe` using existing `build_exe.py`. Bundles:
- All Python modules (voice.py, settings_gui.py, text_processing.py, etc.)
- Whisper small model (~150MB)
- sounds/ and plugins/ directories
- koda.ico

**PyInstaller** was not previously installed — installed it in venv first.
Build took ~80 seconds. Output: `C:\Users\alexi\Projects\koda\dist\Koda.exe` — 525 MB.

Files to bring to work PC (all in same folder):
- `dist/Koda.exe`
- `config.json`
- `filler_words.json`

No Python, no install, no internet required at work. First launch may take 5–10 seconds to unpack.
Windows Defender may require "More info → Run anyway" (unsigned exe).

### 4. Mic Disconnect Detection — Phase 9 Test 1 (voice.py)
**Problem:** When USB mic unplugged, sounddevice's stream would die briefly, then immediately "recover"
using Windows' fallback audio device (built-in mic, HDMI audio, etc.). Koda showed "Microphone recovered
automatically" even though the USB mic was still unplugged — a false recovery.

**Root cause:** `mic_device = null` means sounddevice uses whatever Windows considers the default input
device. When USB mic is unplugged, Windows switches default to another device, and the stream restart
succeeds on the wrong device.

**Fix implemented:**
- Added `_mic_disconnected` (bool) and `_input_device_count` (int) globals
- Added `_count_input_devices()` — uses `ctypes.windll.winmm.waveInGetNumDevs()` (Windows WinMM API)
  to count input devices WITHOUT touching PortAudio or the running stream
- Watchdog initializes baseline count at startup: `_input_device_count = _count_input_devices()`
- Fast path: when stream dies, compare current device count to baseline:
  - Count dropped → physical disconnect → show "Microphone disconnected. Plug it back in." once,
    set `_mic_disconnected = True`, do NOT restart (avoid false recovery on wrong device)
  - Count same/higher → safe to restart (non-disconnect failure or mic came back) → restart,
    show "Microphone recovered automatically." only if `_mic_disconnected` was True
- Tray goes red on disconnect, green on recovery

**Failed approaches tried this session (don't retry):**
- `sd._terminate()` + `sd._initialize()` inside watchdog — kills the running stream (PaErrorCode -9988)
- `_mic_disconnected` flag without device count check — false recoveries still happened

**Test result: PASS** — Alexi confirmed:
- Unplug → "Microphone disconnected. Plug it back in — Koda will recover."
- Replug → "Microphone recovered automatically." + tray goes green

---

## Decisions Made

### 1. STATUS.md as session start document
Handover docs are verbose archives. STATUS.md is the compact (~50 line) live state file.
At session start: read STATUS.md only. Handover docs only for investigating past decisions.
How to apply: update STATUS.md at end of every session during /handover.

### 2. Windows WinMM API for device count
`ctypes.windll.winmm.waveInGetNumDevs()` — Windows-only but Koda is Windows-only.
Does not touch PortAudio session. Safe to call while stream is running.
Returns count of wave input devices; drops by 1+ when USB mic unplugged.

### 3. Don't restart stream on device-count drop
When a physical device is removed, attempting restart with `device=None` succeeds on wrong device.
Decision: detect count drop → show disconnect notification → wait for count to recover → then restart.
This prevents false "recovered" notifications.

### 4. Exe build uses existing build_exe.py
`build_exe.py` was already in the repo and fully configured. Not a new file.
Bundles Whisper model, all modules, sounds. Result: 525 MB single exe.
Distribution to work PC = exe + config.json + filler_words.json in same folder.

### 5. Domain: kodaspeak.com
User decided on `kodaspeak.com` after `koda.com` and `kodavoice.com` were both taken.
`getkoda.com` and `kodaapp.com` were also rejected by Alexi.

### 6. Settings window opens narrow
The `540x{win_h}` geometry fix works but the window opens slightly too narrow — user had to
move it to reach Save button. Deferred fix to a later session.

---

## User Feedback & Corrections

1. **"Mic test did not pass"** — Alexi correctly identified that "Microphone recovered automatically"
   appearing WITHOUT replugging = false recovery. This was a real bug. Fix implemented and confirmed.

2. **Settings window opens narrow** — noted but deferred. "I don't like the layout much but we can
   work on that on a later session."

3. **Too many tray menu options** — Alexi noted the right-click tray menu has too many items and
   "I can see how this can become confusing for an end user." Logged for Phase 13 UX cleanup.

4. **"I don't need Llama"** — confirmed. Ollama/LLM polish is off by default, not required.

5. **Domain preferences** — rejected: koda.com (taken), kodavoice.com (taken), getkoda.com,
   kodaapp.com. Chose: kodaspeak.com.

6. **Run /handover at 40% context** — Alexi called it at 50% again. Try to call it earlier.

---

## Waiting On

### Manual Tests Still Pending

1. **Phase 9 Test 2 — Sleep/wake** (NOT run this session)
   - Put PC to sleep (Start → Power → Sleep — NOT lock screen)
   - Wake it up
   - Verify Ctrl+Space still fires
   - Check debug.log for "Sleep/wake detected" + "Full recovery complete"

2. **Phase 9 Test 3 — RDP hotkey** (NOT run this session)
   - Connect to home PC via RDP
   - Verify Ctrl+Space fires inside RDP session

3. **Phase 12 smoke test** (NOT fully done)
   - Open Settings → scroll to Snippets → add a test snippet → Save → say trigger → confirm expansion pastes
   - Filler Words section was opened and Save was hit (creating filler_words.json) but snippet expansion was not verified

### Pending Items

4. **Uncommitted changes** — `voice.py`, `settings_gui.py` not committed. Commit at start of next session.

5. **Rebuild exe** — `dist/Koda.exe` was built BEFORE the mic disconnect fix. The exe at work will
   not have the correct mic behavior. Rebuild after committing the voice.py changes.

6. **Phase 13** — installer/distribution. Blocked until Phase 9 tests + Phase 12 smoke test pass.

7. **Settings window width** — opens narrow, user had to move window to reach Save. Fix sizing.

8. **Tray menu cleanup** — too many options for end users. Phase 13 UX item.

9. **Phase 9 VAD gap** — SileroVADModel uses wrong API, wastes RAM. Still on backlog.

---

## Next Session Priorities

1. **Commit session 16 changes** — voice.py + settings_gui.py (mic fix + scroll fix)
2. **Rebuild exe** — current dist/Koda.exe is missing the mic disconnect fix
3. **Phase 9 Test 2** — sleep/wake test (put PC to sleep, not lock screen)
4. **Phase 9 Test 3** — RDP hotkey test
5. **Phase 12 smoke test** — add snippet, save, say trigger, verify expansion pastes
6. **Phase 13** — installer/exe build for distribution (after above tests pass)

---

## Files Changed This Session

| File | Change | Status |
|------|--------|--------|
| `voice.py` | Mic disconnect detection: `_count_input_devices()`, `_mic_disconnected` flag, `_input_device_count` baseline, watchdog fast path rewrite | **UNCOMMITTED** |
| `settings_gui.py` | Scrollable canvas wrapping settings content; window sized to screen height | **UNCOMMITTED** |
| `STATUS.md` | New compact session-start file (created this session) | **UNTRACKED** |
| `filler_words.json` | Created by Alexi saving Settings | **UNTRACKED** |
| `dist/Koda.exe` | Built from source (525 MB, Whisper bundled) — does NOT include mic fix | **UNTRACKED** |
| `docs/sessions/alex-session-16-handover.md` | This file | **UNTRACKED** |
| `.claude/projects/.../memory/project_koda.md` | New memory: read STATUS.md at session start | **SAVED** |
| `.claude/projects/.../memory/MEMORY.md` | Updated index | **SAVED** |

---

## Key Reminders

- **Kill ALL python before restart:** `taskkill //f //im pythonw.exe` AND `taskkill //f //im python.exe`
- **Run from source:** `cmd //c "C:\Users\alexi\Projects\koda\start.bat"`
- **Tests:** `venv/Scripts/python -m pytest test_features.py` — 176 passing
- **Exe rebuild needed** — current dist/Koda.exe predates mic disconnect fix
- **Sleep ≠ Lock screen** — Phase 9 Test 2 requires actual Sleep (Power → Sleep)
- **Domain chosen:** kodaspeak.com
- **Settings window opens narrow** — known issue, deferred
- **Tray menu has too many options** — noted by Alexi, Phase 13 UX item
- **DO NOT re-run market research** — saved in memory
- **DO NOT suggest Product Hunt**
- **DO NOT build exe during dev** — Phase 13 will formalize
- **No mid-task confirmation prompts**
- **GitHub CLI:** `"C:\Program Files\GitHub CLI\gh.exe"`, auth as `Moonhawk80`
- **Repo:** github.com/Moonhawk80/koda
- **Hotkeys:** ONLY `ctrl+alt+letter` or F-keys
- **Paste:** `keyboard.send("ctrl+v")` — NOT pyautogui
- **Sound:** `winsound` — NOT sounddevice
- **No NVIDIA GPU** — Intel UHD 770 only
- **Run /handover at ~40% context** — 50% is too late

---

## Migration Status
None — no database in this project.

---

## Test Status
- **176 tests passing** (`test_features.py`) — unchanged from session 15
- No new tests added this session (mic fix is in watchdog runtime, not unit-testable)
- `test_stress.py` — 17/17 standalone (unchanged)

---

## Current Config State
```json
{
  "model_size": "small",
  "language": "en",
  "hotkey_dictation": "ctrl+space",
  "hotkey_command": "f8",
  "hotkey_prompt": "f9",
  "hotkey_correction": "f7",
  "hotkey_readback": "f6",
  "hotkey_readback_selected": "f5",
  "hotkey_mode": "hold",
  "mic_device": null,
  "sound_effects": true,
  "notifications": false,
  "noise_reduction": false,
  "post_processing": {
    "remove_filler_words": true,
    "code_vocabulary": false,
    "auto_capitalize": true,
    "auto_format": true
  },
  "vad": {
    "enabled": true,
    "silence_timeout_ms": 1000
  },
  "wake_word": {
    "enabled": false,
    "phrase": "hey koda"
  },
  "llm_polish": {
    "enabled": false,
    "model": "phi3:mini"
  },
  "overlay_enabled": true,
  "snippets": {}
}


---
<!-- Additional content from home PC sessions -->

# Alex Session 16 Handover — 2026-04-13

## Branch
`master` — all work committed and pushed to origin (https://github.com/Moonhawk80/koda).
0 unpushed commits.

## Repo
**https://github.com/Moonhawk80/koda** (transferred this session from Alex-Alternative/koda)

## Context
Cross-PC session. Alex is splitting work between two machines:
- **Work PC**: `C:\Users\alex\Projects\koda` — where this session ran
- **Home PC**: `~/Projects/koda` — where session 15 ran (Phases 11 & 12)

Work was synced via git pull/rebase mid-session. Both PCs now in sync.

## What Was Built This Session

### 1. Repo Transfer (Alex-Alternative → Moonhawk80)
- User initiated GitHub repo transfer to personal account
- Updated repo URL references in: `updater.py` (line 16), `README.md`, `installer/koda.iss`
- Old session handover docs left as historical record (still reference Alex-Alternative)
- GitHub now redirects old URL → new URL automatically

### 2. Sound Files Committed
- `sounds/start.wav`, `stop.wav`, `success.wav`, `error.wav` were previously gitignored
- Force-added to repo so a fresh clone has everything to run Koda
- Only `wakeword.wav` was in git before
- Eliminates need to run `generate_sounds.py` after clone

### 3. Critical Build Fix — tkinter Missing in Koda.exe
- **Bug**: User installed v4.2.0 from `KodaSetup-4.2.0.exe`, got crash on launch:
  `ModuleNotFoundError: No module named 'tkinter'` (overlay.py:10)
- **Root cause**: `build_exe.py` had `--exclude-module=tkinter` and `--exclude-module=_tkinter`
  to save space, but `overlay.py`, `settings_gui.py`, and `stats_gui.py` ALL require it
- **Fix**: Removed the excludes, added explicit hidden imports for tkinter, tkinter.ttk,
  tkinter.messagebox, tkinter.filedialog
- **Rebuilt**: `dist/Koda.exe` (529MB, was 526MB) and `dist/KodaSetup-4.2.0.exe` (530MB)
- Commit `25cffaa`

### 4. Cross-PC Sync via Git
- Work PC pulled in 4 commits from home PC: Phase 11 (per-app profile GUI),
  Phase 12 (snippets + filler words GUI), session 14 + 15 handovers
- Test count went from 117 → 176 (59 new tests from home PC work)
- Rebased work PC's tkinter fix on top of home PC commits — clean fast-forward

## Decisions Made

1. **Use git pull/rebase for cross-PC sync** — not file copying. The repo on GitHub is
   the single source of truth. Both PCs sync through it.
2. **Sound files now in git** — small (<100KB total), worth the cleaner clone experience.
3. **Don't auto-modify the handover skill** — user mentioned wanting it to auto-commit/push,
   but safety system blocked the edit. User needs to explicitly approve the change.
4. **Don't install Vercel plugin on home PC for Koda** — it's a Python desktop app, not a
   web app. Vercel false-positives on keywords like "deploy" and "phase".
5. **Personal GitHub: Moonhawk80** — repo permanently lives there now. Old Alex-Alternative
   URL redirects automatically but should be updated in tools/configs.

## User Feedback & Corrections

1. **"Why is Koda not working again!"** — Old v4.1.0 was still running, needed kill+restart
   to pick up v4.2.0 code. Common pattern when running from source.
2. **"Why is she off again I have been using the PC but not Koda"** — Hooks died silently
   while subprocess stayed alive. Led to hook-level health check fix in session 8.
3. **"I always forget committing maybe it is a point to add to handover skill"** — Confirmed
   pain point. Skill update was attempted but blocked by safety system. Pending user approval.
4. **"Are you sure you have all the files for everything I built at home?"** — Yes, after
   git pull. The .exe is irrelevant — source code on GitHub is the truth.
5. **"It is on my personal github now silly goose"** — User playful but real point: don't
   reference old URLs.

## Waiting On

- **User approval to update handover skill** to auto-commit/push (safety system blocked
  the edit; user needs to explicitly say "yes update it")
- **Home PC needs to pull** to get the tkinter fix and updated repo URLs
- **Home PC needs to rebuild Koda.exe and reinstall** — broken installer is what user has now
- **Soak test the sleep/wake recovery + hook hardening** from session 8 — not yet verified
  through real sleep cycles
- **Upload `KodaSetup-4.2.0.exe` to GitHub Release v4.2.0** — would let auto-update flow
  work end-to-end and home PC could just download instead of rebuild

## Next Session Priorities

### Immediate (home PC)
1. **Pull latest from origin** — get tkinter fix + repo URL updates
2. **Commit any uncommitted Sunday night work** if `git status` shows changes
3. **Rebuild Koda.exe and installer** with the tkinter fix
4. **Uninstall broken Koda, install fixed v4.2.0**, verify launch works

### Phase 8 — Hardening (still pending)
5. **Soak test sleep/wake recovery** — let Koda run, sleep machine, verify auto-recovery
6. **Edge cases** — RDP, multi-monitor, Bluetooth/USB mic hot-swap
7. **Extended runtime stability** — hours-long sessions, memory profile

### Ship It
8. **Upload installer to GitHub Release** — `gh release upload v4.2.0 dist/KodaSetup-4.2.0.exe`
9. **Real-world daily use** for a week before declaring "done"

### Backlog
10. **Update handover skill to auto-commit/push** (when user approves)
11. **Update GitHub CLI auth on home PC** if needed
12. **Mac version** — separate milestone, ~30% of code is Windows-specific

## Files Changed This Session

| File | Change |
|---|---|
| `build_exe.py` | Removed tkinter excludes, added tkinter hidden imports |
| `updater.py` | GITHUB_REPO updated to Moonhawk80/koda |
| `README.md` | Repo URL references updated to Moonhawk80 |
| `installer/koda.iss` | Repo URL updated |
| `sounds/start.wav` | Added to git (was gitignored) |
| `sounds/stop.wav` | Added to git |
| `sounds/success.wav` | Added to git |
| `sounds/error.wav` | Added to git |
| `dist/Koda.exe` | Rebuilt with tkinter (529MB) — not in git |
| `dist/KodaSetup-4.2.0.exe` | Rebuilt installer (530MB) — not in git |

## Current Test Status
- **176 tests passing** (from session 15)
- No new tests this session (build/transfer work only)

## Key Reminders

- **GitHub URL is now https://github.com/Moonhawk80/koda** — old Alex-Alternative URL redirects
- **Always commit + push at end of session** — handover skill should do this but doesn't yet
- **Always pull at start of session on either PC** — keeps both machines in sync
- **Kill ALL python/pythonw processes before restarting Koda** — `taskkill //f //im pythonw.exe`
- **Hotkey rules**: ONLY use `ctrl+alt+letter` or F-keys. Backtick, space combos, Ctrl+Shift+P all fail.
- **Test hotkeys with physical keypresses** — `keyboard.send()` simulation doesn't work
- **`keyboard._hooks` count is USELESS** for detecting dead hooks
- **Venv** at `C:\Users\alex\Projects\koda\venv` (work) or `~/Projects/koda/venv` (home)
- **GitHub CLI** at `"C:\Program Files\GitHub CLI\gh.exe"` on work PC
- **Python 3.14** — tflite-runtime has no wheels, openwakeword uses ONNX
- **mic_device = null** — don't hardcode indices
- **pyttsx3 COM threading** — must init lazily in the thread that uses it
- **Paste uses `keyboard.send("ctrl+v")`** NOT pyautogui
- **No NVIDIA GPU** — Intel UHD 770 only, CUDA not available
- **DO NOT suggest Product Hunt** — needs thorough testing first
- **tkinter is REQUIRED in build_exe.py** — overlay/settings/stats GUIs depend on it. Don't exclude it again.
- **Vercel plugin auto-suggests for Koda — ignore it.** Koda is a Python desktop app, not a web app.

## Cross-PC Workflow

**Before stopping work on either PC:**
```
git add -A
git commit -m "wip" (or descriptive message)
git push
```

**Starting work on either PC:**
```
git pull
```

**If you get a merge/rebase conflict on pull**: STOP and ask Claude to help. Don't force anything.

## Quick Resume Block

Copy this into a new session to pick up where we left off:

```
cd ~/Projects/koda  (home) OR C:\Users\alex\Projects\koda (work)

git pull origin master

Read docs/sessions/alex-session-16-handover.md for full context. Koda — push-to-talk
voice-to-text Windows tray app. Repo: github.com/Moonhawk80/koda.

Continue from session 16. v4.2.0 source is current. 176 tests passing.

Session 16 shipped: tkinter build fix (was crashing v4.2.0 .exe), repo transfer to
Moonhawk80, sound files committed to repo, cross-PC sync via git pull/rebase.

Next up:
1. (Home PC) Rebuild Koda.exe + installer with tkinter fix, reinstall fixed v4.2.0
2. Phase 8 hardening: soak test sleep/wake recovery, edge cases (RDP, multi-monitor, mic hot-swap)
3. Upload KodaSetup-4.2.0.exe to GitHub Release v4.2.0 (`gh release upload v4.2.0 dist/KodaSetup-4.2.0.exe`)
4. Update handover skill to auto-commit/push (pending explicit user approval)

Key context:
- Hotkeys: Ctrl+Space=dictation, F5-F9=everything else.
- ALWAYS git pull at start, git push at end. Cross-PC sync depends on it.
- Kill ALL python/pythonw processes before restarting Koda.
- 176 tests passing.
- DO NOT suggest Product Hunt.
- tkinter is REQUIRED in build_exe.py — don't re-exclude it.
- Repo is at Moonhawk80/koda, not Alex-Alternative anymore.
```
