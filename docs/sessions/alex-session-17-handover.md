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
