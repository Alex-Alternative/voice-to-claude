# Alex Session 17 Handover — 2026-04-13

## Branch
`master` — all changes committed. Nothing unpushed.

---

## What Was Built This Session

### 1. Phase 9 Test 2 — Sleep/Wake PASS (`voice.py`)
Committed `c43114d`. Put PC to actual Sleep (Power → Sleep, 45 seconds), woke it.
Debug log confirmed:
- `Sleep/wake detected (expected 15s, got 37s) — full recovery`
- `Full recovery triggered: sleep/wake, gap=37s`
- `Full recovery complete (sleep/wake, gap=37s)`
- Hotkey service restarted, all hotkeys re-registered
- Ctrl+Space fired immediately after wake

**Phase 9 Test 3 (RDP) still NOT run** — requires second machine.

### 2. Settings GUI — Save & Restart Bug: 5 Commits to Fix
`settings_gui.py` had a broken Save & Restart Koda button. Took 5 commits to fully fix:

**Root cause:** `settings_gui.py` is launched by `voice.py` via `sys.executable` which is `pythonw.exe`.
So the settings GUI itself runs as `pythonw.exe` — killing all `pythonw` processes killed itself
before it could relaunch Koda.

**Fix chain:**
- `e73d8d2` — Kill only `pythonw`, not `python` (wrong — settings GUI IS pythonw)
- `021a2c3` — Remove "Settings saved, restart Koda" popup that appeared when clicking Save & Restart
- `540873e` — Use `DETACHED_PROCESS` flag (still failing — self-kill happening first)
- `ef66bcf` — Launch `venv/Scripts/pythonw.exe` directly instead of `start.bat` (bat unreliable without console)
- `5be7a52` — **Final fix:** Kill only `os.getppid()` (the parent Koda PID) instead of all pythonw.
  Settings GUI is its own pythonw process; parent is a different PID.

**Final working sequence in `save_and_restart()`:**
1. `self.save(notify=False)` — save config silently
2. `taskkill /f /pid {parent_pid}` — kill only the Koda parent process by PID
3. Sleep 0.5s
4. `Popen([pythonw, "voice.py"], DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)` — relaunch
5. `self.destroy()` — close settings GUI

### 3. Phase 12 Smoke Test — Snippets Fix (`voice.py`)
Commit `8b878e1`. Snippets saved fine but didn't expand when spoken.

**Root cause:** In normal dictation mode, `voice.py` builds a `light_config` dict that was
missing the `"snippets"` key. `process_text()` saw an empty snippets dict and skipped expansion.
Command mode passed full `config` (had snippets), dictation mode did not.

**Fix:** Added `"snippets": config.get("snippets", {})` to `light_config` in `voice.py:661–670`.

Phase 12 smoke test: **PASS** — snippets save, reload on restart, and expand when trigger spoken.

### 4. Settings Window — Tabbed Redesign (`settings_gui.py`)
Commit `f72a1cc`. Replaced single 1750px scroll wall with a 5-tab notebook:

| Tab | Contents |
|-----|----------|
| General | Recording mode (hold/toggle), Output mode, all feature toggles |
| Hotkeys | All 6 hotkey assignments |
| Speech | Whisper model size + language |
| Words | Sub-tabs: Custom Words, Filler Words, Snippets, App Profiles |
| Advanced | Translation, Read-back voice, Performance (GPU), History |

Window: 620×540px fixed. No more scrolling. All sections visible at a glance.

### 5. Color Palette Overhaul (`settings_gui.py`)
Commit `f72a1cc`. Replaced dark purple Catppuccin theme with clean light theme:
- Background: `#f4f4f4` (light gray)
- Text: `#1a1a1a` (near-black)
- Headers: `#1a56db` (blue accent)
- Separators: `#d0d0d0`

Alexi said the old dark purple was "off-putting."

### 6. Tray Menu Cleanup (`voice.py`)
Commit `f72a1cc`. Cut from 22 items to 10:

**Kept in tray:**
- Status label (version + hotkeys + mode in one line)
- Sound effects toggle
- Remove filler words toggle
- Switch mode (hold/toggle)
- Floating overlay toggle
- Settings (opens settings window)
- Tools submenu (Transcribe audio file, Install Explorer right-click, Usage stats)
- Check for updates
- Quit

**Removed from tray** (all accessible via Settings window):
- Code vocabulary, voice commands, auto-format, noise reduction, LLM polish,
  translation, wake word, output mode, read-back voice/speed, per-app profiles,
  edit custom words, edit app profiles, open config file

---

## Decisions Made

### 1. Kill parent by PID, not by process name
`os.getppid()` gives the specific PID of the Koda process that launched settings_gui.
Killing all `pythonw` processes was self-destructive. PID-targeted kill is the only safe approach.

### 2. Launch pythonw.exe directly, not via start.bat
`start.bat` calls `venv\Scripts\activate` then `start /min pythonw voice.py`.
When launched without a console (from DETACHED_PROCESS parent), the `start` command inside
the bat file may not behave correctly. Directly calling `venv/Scripts/pythonw.exe voice.py`
is simpler and always works.

### 3. Snippets must be in light_config
Dictation mode uses a stripped-down `light_config` to avoid applying code vocabulary and
other heavy processing. Snippets need to be in it explicitly — they're a user-facing feature,
not a pipeline detail.

### 4. Tabbed settings instead of scrollable
User said "love tabs and dropdowns, menus and things that can make all these menus shorter
and more user-friendly." Tabs eliminate the scroll entirely. Words tab uses sub-tabs to keep
4 sections (Custom Words, Filler Words, Snippets, App Profiles) out of the main nav.

### 5. Light theme for settings
User said dark purple color palette is "off-putting." Switched to `#f4f4f4` light gray
background with `#1a56db` blue accent. More Windows-native, less gamer aesthetic.

### 6. Tray menu: quick toggles only
Everything that needs configuration lives in Settings. Tray keeps only the two most-used
toggles (sound, filler words) plus mode switch and overlay. Everything else is clutter.

---

## User Feedback & Corrections

1. **"Save and restart Koda did not work"** — multiple rounds. Root cause was settings GUI
   running as `pythonw.exe` and killing itself. Took 5 commits across the session.
2. **"The snippets don't work lol"** — missing snippets in light_config. Fixed in one commit.
3. **"Love tabs and drops, menus and things like that"** — informed settings redesign.
4. **"Color palette is a little off-putting"** — the dark purple theme. Switched to light theme.
5. **"It did not restart"** — multiple times during save_and_restart debugging. Each time
   we dug deeper into why.
6. **"When you finish I need you to run the handover skill. I need to go to bed"** — end of session.

---

## Waiting On

### Manual Tests Still Pending
1. **Phase 9 Test 3 — RDP** — connect via RDP, verify Ctrl+Space fires. Requires second machine.

### Pending Work
2. **Phase 13 — Installer/Distribution** — unblocked now that Phase 9 (partial) and Phase 12 smoke test pass.
   Exe needs rebuilding (current dist/Koda.exe was built before the save_and_restart/snippets fixes).
3. **Verify new Settings UI visually** — session ended before Alexi confirmed the new tabbed Settings
   window looked good. Verify on next session start.
4. **Phase 9 VAD gap** — SileroVADModel uses wrong API, wastes RAM. Still on backlog.
5. **dist/Koda.exe needs rebuild** — current exe predates several session 17 fixes.

---

## Next Session Priorities

1. **Verify Settings UI looks correct** — open Settings from tray, confirm tabs + light theme display properly
2. **Phase 9 Test 3** — RDP hotkey test (requires second machine)
3. **Rebuild dist/Koda.exe** — current exe predates snippets fix + save_and_restart fix
4. **Phase 13** — installer/exe distribution for work PC (exe + config.json + filler_words.json)
5. **Update STATUS.md** — reflect completed Phase 12, phase 9 partial, phase 13 status

---


---
<!-- Additional content from home PC sessions -->

`master` — all work committed and pushed to https://github.com/Moonhawk80/koda
0 unpushed commits.

## Repo
**https://github.com/Moonhawk80/koda** (transferred from Alex-Alternative in session 16)

## Context
Cross-PC continuation. Work PC session focused on fixing the broken installer that
session 16 produced, and clarifying the dev-vs-distribution workflow. User will
continue at home PC.

## What Was Built This Session

### 1. Diagnosed and Fixed Broken .exe Install
- **Symptom**: User installed `KodaSetup-4.2.0.exe`, saw overlay green but tray
  icon missing and hotkeys not working
- **Investigation**: Found two zombie `Koda.exe` processes (PIDs 61728, 9460)
  in `C:\Users\alex\AppData\Local\Programs\Koda\`. Found PyInstaller temp dir
  `_MEI617282/debug.log` showing the actual error
- **Root cause**: Whisper model load failed at startup
  - Bundled config.json had `model_size: "base"` (default) at install time
  - Whisper tried to load `base` from `~/.cache/huggingface/hub/...base` — file corrupt/missing
  - Process zombied: overlay started BEFORE model load (so showed green/ready),
    but tray icon, watchdog, hotkey service all came AFTER and never initialized
- **Fix**: User uninstalled the .exe, switched back to running from source. Confirmed working.

### 2. Publisher Name Fix
- Installer publisher was `"Alex Alternative"` (the work brand)
- Changed to `"Alex Concepcion"` (real name from git config) for personal project
- Commit `1c3abdf`. User can change to "Moonhawk80" or other label if preferred.

### 3. Reinforced Dev Workflow
- Confirmed: **run from source** (`pythonw voice.py`) for active development
- The installer is for END-USER distribution, not the developer
- Every code change → no rebuild needed → just kill+restart pythonw

## Decisions Made

1. **Source > installer for the developer** — installer is for shipping to others.
   Saves rebuild/reinstall cycle on every change. Documented in updated home PC prompt.
2. **Publisher = "Alex Concepcion"** (real name from git) — chose over "Moonhawk80" handle
   because installer publisher field shows to end users; real name reads more professional.
   Reversible if user prefers handle.
3. **Don't auto-modify the handover skill** to add commit/push — safety system blocked it
   in session 16. Pending explicit user approval. Still a real pain point that costs work.

## User Feedback & Corrections

1. **"Why is my Koda off on the tray but the desktop icon shows green?"** — Confused
   tray icon (system notification area) with floating overlay (KodaOverlay window).
   They're independent; overlay started before crash, tray died with crash.
2. **"Would it make better sense to uninstall and run it like before from my personal git?"** —
   YES, exactly right. The installer is for distribution, not development. User got there
   intuitively, which is the right instinct.
3. **"The author of the app when installed it says Alex Alternative we need to fix that"** —
   Done. Now reads "Alex Concepcion" in the installer publisher field.
4. **"I uninstalled and it and its working now"** — Confirmed source-mode is healthy.

## Waiting On

- **Home PC needs to pull** (`git pull origin master`) to get tkinter fix + publisher name fix
- **Soak test sleep/wake recovery** from session 8 — still not verified through real cycles
- **User approval to update handover skill** to auto-commit/push (safety system blocked this
  in session 16)
- **Upload `KodaSetup-4.2.0.exe` to GitHub Release v4.2.0** — for end users, not needed
  for personal use

## Next Session Priorities

### Immediate (home PC)
1. **`git pull origin master`** — get tkinter fix + publisher name change
2. **Run from source** for active dev: `pythonw voice.py` (DON'T install the .exe)
3. **Check `git status`** for any uncommitted Sunday-night work and commit if found

### Phase 8 — Hardening (still pending)
4. **Soak test sleep/wake recovery** — sleep machine, wake, verify auto-recovery
5. **Edge cases** — RDP, multi-monitor, Bluetooth/USB mic hot-swap
6. **Extended runtime stability** — hours-long sessions, memory profile

### Polish & Distribution
7. **Decide publisher name finally** — Alex Concepcion vs Moonhawk80 vs other
8. **Upload installer to GitHub Release** when ready to share with others
9. **Real-world daily use** for a week before declaring "done"

### Backlog
10. **Update handover skill to auto-commit/push** when user says "yes"
11. **Mac version** — separate milestone, ~30% of code is Windows-specific

## Files Changed This Session

| File | Change | Commit |
|------|--------|--------|
| `voice.py` | mic fix committed, snippets in light_config, tray menu cleanup | `c43114d`, `8b878e1`, `f72a1cc` |
| `settings_gui.py` | scroll fix, save_and_restart (5 fix commits), tabbed redesign, light theme | `c43114d` through `f72a1cc` |
| `config.json` | new keys added (committed) | `c43114d` |

Untracked (not committed):
- `STATUS.md` — needs update + commit
- `filler_words.json` — user-created, should be committed
- `docs/sessions/alex-session-17-handover.md` — this file

---

## Key Reminders

- **Kill ALL python before restart:** `taskkill //f //im pythonw.exe` AND `taskkill //f //im python.exe`
- **Run from source:** `cmd //c "C:\Users\alexi\Projects\koda\start.bat"`
- **Tests:** `venv/Scripts/python -m pytest test_features.py` — 176 passing (no new tests this session)
- **settings_gui runs as pythonw** (launched via sys.executable from voice.py) — never kill all pythonw from within settings_gui
- **Sleep ≠ Lock screen** — Phase 9 Test 2 requires actual Sleep (Power → Sleep) ✅ DONE
- **Snippets live in light_config now** — already fixed, don't revert
- **Domain chosen:** kodaspeak.com
- **DO NOT re-run market research** — saved in memory
- **DO NOT suggest Product Hunt**
- **DO NOT build exe during dev** — Phase 13 will formalize
- **No mid-task confirmation prompts**
- **GitHub CLI:** `"C:\Program Files\GitHub CLI\gh.exe"`, auth as `Moonhawk80`
- **Repo:** github.com/Moonhawk80/koda
- **No NVIDIA GPU** — Intel UHD 770 only
- **Run /handover at ~40% context**

---

## Migration Status
None — no database in this project.

---

## Test Status
- **176 tests passing** (`test_features.py`) — unchanged from session 16
- No new tests added this session
- `test_stress.py` — 17/17 standalone (unchanged)
- Save & Restart and snippet expansion are UI/runtime behaviors — not covered by unit tests


---
<!-- Additional content from home PC sessions -->

|---|---|---|
| `installer/koda.iss` | Publisher: "Alex Alternative" → "Alex Concepcion" | `1c3abdf` |
| `docs/sessions/alex-session-17-handover.md` | This file | (current) |

## Test Status
- **176 tests passing** (unchanged from session 16)
- No new tests this session (diagnosis + config work only)

## Key Reminders

- **GitHub URL is https://github.com/Moonhawk80/koda** — old Alex-Alternative redirects
- **The installer is for END USERS, not the developer** — run from source for dev work
- **If you install the .exe and it crashes**: check `%TEMP%\_MEIxxx\debug.log` for the real error
- **Always commit + push at end of session** — handover skill should do this but doesn't yet
- **Always pull at start of session on either PC** — keeps both machines in sync
- **Kill ALL python/pythonw/Koda processes before restarting** — `taskkill //f //im pythonw.exe`
  AND `taskkill //f //im Koda.exe`
- **Hotkey rules**: ONLY use `ctrl+alt+letter` or F-keys. Backtick, space combos all fail.
- **Test hotkeys with physical keypresses** — `keyboard.send()` simulation doesn't work
- **`keyboard._hooks` count is USELESS** for detecting dead hooks
- **Venv** at `~/Projects/koda/venv` (home) or `C:\Users\alex\Projects\koda\venv` (work)
- **Python 3.14** — tflite-runtime has no wheels, openwakeword uses ONNX
- **mic_device = null** — don't hardcode indices
- **pyttsx3 COM threading** — must init lazily in the thread that uses it
- **Paste uses `keyboard.send("ctrl+v")`** NOT pyautogui
- **No NVIDIA GPU** on work PC — Intel UHD 770 only, CUDA not available
- **DO NOT suggest Product Hunt** — needs thorough testing first
- **tkinter is REQUIRED in build_exe.py** — overlay/settings/stats GUIs depend on it (fixed in session 16)
- **Vercel plugin auto-suggests for Koda — ignore it.** Koda is a Python desktop app, not web.

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

If you get a merge/rebase conflict on pull: STOP and ask Claude to help.

## Quick Resume Block

Copy this into a new session on your HOME PC to pick up where we left off:

```
cd ~/Projects/koda

git pull origin master
git status

I need to continue work on Koda from session 17 (docs/sessions/alex-session-17-handover.md).

## Where we left off
Work PC fixed two issues this session:
1. The .exe install was crashing because Whisper couldn't find the bundled model
   when config defaulted to "base". Switched to running from source — works perfectly.
2. Installer publisher name changed from "Alex Alternative" to "Alex Concepcion".

## My setup at home
Run from source for development:
  ./venv/Scripts/activate
  pythonw voice.py

DO NOT install the .exe for personal use — it's only for distribution to others.

## Next up
1. Verify Koda runs from source on home PC (Ctrl+Space test)
2. Phase 8 hardening: soak test sleep/wake recovery, RDP/multi-monitor/mic edge cases
3. Decide on final publisher name (Alex Concepcion vs Moonhawk80 vs other)
4. Update handover skill to auto-commit/push (need to explicitly tell Claude "yes update it")

## Key context
- Koda = push-to-talk voice-to-text Windows tray app
- Repo: github.com/Moonhawk80/koda — 176 tests passing — v4.2.0
- Hotkeys: Ctrl+Space=dictation, F8=command, F9=prompt assist, F7=correction, F6=read back, F5=read selected
- ALWAYS git pull at start, git push at end. Cross-PC sync depends on it.
- Kill ALL pythonw + Koda.exe processes before restarting
- DO NOT suggest Product Hunt
- tkinter MUST be in build_exe.py — don't re-exclude it
- Repo is at Moonhawk80/koda, not Alex-Alternative anymore
```
