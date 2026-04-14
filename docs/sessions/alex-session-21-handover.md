# Alex Session 21 Handover — 2026-04-13

## Branch
`master` — fully pushed to origin. Clean except for two intentionally uncommitted local files.

---

## What Was Built This Session

### 1. Keyboard Blocking Fix — `hotkey_service.py`
**Problem:** On startup via the Windows startup shortcut (Koda.lnk → start.bat → pythonw voice.py), there was a race window between the WH_KEYBOARD_LL hook being installed in the hotkey service subprocess and its GetMessageW loop starting. During that window, Windows routes ALL keyboard input through the hook owner thread. If the thread isn't pumping messages, keyboard input blocks system-wide.

**Fix:** Removed the WH_KEYBOARD_LL hook entirely. Hold-mode key-up detection is now done by a background daemon thread that polls `GetAsyncKeyState(vk) & 0x8000` every 10ms. When a WM_HOTKEY fires (key-down), the VK code is added to `_active_press_vks`; the poller thread watches until the key goes up and sends the `_release` event. No hooks = nothing can block keyboard input under any circumstances.

**Files:** `hotkey_service.py` — removed `SetWindowsHookExW`, `_KBDLLHOOKSTRUCT`, `_HOOKPROC`, `WM_KEYUP`, `WM_SYSKEYUP`, `WH_KEYBOARD_LL` constants. Added `_poll_key_release()` thread and `_active_press_vks` set.

### 2. Keyboard Hook Regression Guard — `test_features.py`
Added `TestNoKeyboardHooks` class (2 tests). Scans all source files (`hotkey_service.py`, `voice.py`, `settings_gui.py`, `overlay.py`, `text_processing.py`, `updater.py`, `hardware.py`, `stats.py`, `history.py`, `plugin_manager.py`, `profiles.py`) for `SetWindowsHookEx` calls in non-comment lines. Test suite fails immediately if anyone re-introduces a keyboard hook. The tests only check live code lines (strips comments and blank lines before scanning).

### 3. Installer Branding — `installer/koda.iss`, `installer/wizard_banner.bmp`, `installer/wizard_small.bmp`
The Inno Setup installer wizard had zero custom branding — generic default Inno chrome.

**Added:**
- `wizard_banner.bmp` (164×314px): Shown on left side of Welcome/Finish pages. Teal gradient background, Koda icon, "KODA" title, "Voice to Text" tagline, "Push-to-talk transcription", "by Alex Concepcion", "v4.2.0". Generated with Pillow from `koda.ico`.
- `wizard_small.bmp` (55×55px): Shown top-right on all inner wizard pages. Koda icon on teal background.
- `koda.iss` additions: `WizardImageFile`, `WizardSmallImageFile`, `LicenseFile=..\LICENSE`, `AppCopyright`, `AppVerName`, `VersionInfoCompany`, `VersionInfoCopyright`, `VersionInfoDescription`, `VersionInfoVersion`, `VersionInfoProductName`, `VersionInfoProductVersion` — full metadata embedded in the installer exe itself (visible in Properties → Details).

### 4. VK Map Fix — `hotkey_service.py`
`ctrl+shift+.` is the DEFAULT config (`config.py` line 18) for `hotkey_command`. The period key (`.`) was missing from the VK map, so every fresh install silently had no command hotkey. The error `[ERROR] Cannot parse hotkey 'ctrl+shift+.' — skipping` was in the log but invisible to users.

**Fix:** Added full OEM punctuation keys to `_VK_MAP`:
- `.` → 0xBE (VK_OEM_PERIOD)
- `,` → 0xBC, `;` → 0xBA, `-` → 0xBD, `=` → 0xBB, `/` → 0xBF
- `` ` `` → 0xC0, `[` → 0xDB, `\` → 0xDC, `]` → 0xDD, `'` → 0xDE
- Numpad 0-9 (0x60–0x69)
- Navigation: insert, delete, home, end, pageup, pagedown, arrows, tab, enter, esc, backspace

### 5. Hotkey Parser Tests — `test_features.py`
Added `TestHotkeyParser` class (9 tests):
- `test_ctrl_space`, `test_f8`, `test_ctrl_shift_period` (the bug that was broken), `test_ctrl_shift_z`, `test_ctrl_alt_r`
- `test_trigger_vk_period`, `test_trigger_vk_space`, `test_trigger_vk_f9`
- `test_all_default_hotkeys_parseable` — iterates every hotkey in `DEFAULT_CONFIG` and asserts VK ≠ 0. Will catch any future default that can't parse.

### 6. Koda.exe Rebuilt — `dist/Koda.exe`
529MB. Includes all fixes from sessions 20-21: RegisterHotKey hotkey service, hallucination fix, GetAsyncKeyState keyboard fix, VK map fix. Verified it started cleanly (log: "Koda v4.2.0 fully initialized").

### 7. Stale Comment Cleanup — `voice.py`
Lines 1250-1253: watchdog comment still referenced the old `keyboard.on_press` / WH_KEYBOARD_LL approach. Updated to describe the current RegisterHotKey + pong-tuple staleness check.

### 8. STATUS.md + Memory Updated
- Test count: 208 (187 test_features.py + 21 test_e2e.py)
- Phase 13 marked IN PROGRESS
- Next session priorities updated

---

## Decisions Made

### "Never install WH_KEYBOARD_LL hooks" is now a hard rule enforced by tests
**Why:** A WH_KEYBOARD_LL hook installed in a process not pumping its message queue blocks ALL keyboard input system-wide. This happened on startup via the autostart shortcut — system was busy on cold boot, the hook was installed before the GetMessageW loop started, keyboard froze. RegisterHotKey + GetAsyncKeyState polling eliminates any hook-related risk permanently.

### GetAsyncKeyState polling at 10ms for hold-mode key-up
**Why:** Alternative was keeping the WH_KEYBOARD_LL hook but trying to guarantee the message loop starts first. That's a timing guarantee that's inherently fragile. Polling at 10ms is ≤10ms release latency, which is imperceptible for voice recording. No tradeoff worth worrying about.

### Installer images generated via Pillow from koda.ico
**Why:** Inno Setup needs BMP images. We have Pillow in the venv and koda.ico already. Generating programmatically means the images can be regenerated/updated in future without needing separate design assets.

### Inno Setup not installed — installer compilation skipped
**Why:** Not installed on this machine. The .iss script and images are ready. User needs to install Inno Setup 6 (free, ~5MB) then run `python installer/build_installer.py`.

---

## User Feedback & Corrections

- **"for the love of all that is holy fix whatever you did to disable my keyboard"** — User came in upset about keyboard being disabled on startup after the previous session's hotkey rewrite. Treated as P0.
- **"when done tell me wtf happened"** + **"how did you disable the keyboard"** — User wanted a clear explanation of root cause. Explanation given: WH_KEYBOARD_LL startup race window.
- **"we need to fix that start file it doesnt show logo or author or anything"** — User meant the Inno Setup installer (koda.iss). Wanted branding on the wizard.
- **"make sure we never ever disable keyboard"** — Led to the regression guard tests.
- **"did we push to git"** — Yes, all commits pushed to origin/master.
- **"where is my context bar"** — Claude Code status line was not configured. Configured via statusline-setup agent. Now loads on every session automatically (global settings.json).

---

## Waiting On

- **Inno Setup 6** — must be installed to compile KodaSetup-4.2.0.exe. URL: https://jrsoftware.org/isdl.php
- **RDP test** — Phase 9 Test 3. Needs a second machine to connect via RDP and verify Ctrl+Space fires.

---

## Next Session Priorities

1. **Install Inno Setup 6** → run `python installer/build_installer.py` → get KodaSetup-4.2.0.exe
2. **Test KodaSetup.exe** — install it on work PC, verify wizard shows Koda logo + "by Alex Concepcion", hotkeys work after install
3. **RDP test** — connect to this PC via RDP from another machine, verify Ctrl+Space fires and transcription works
4. **Settings UI smoke test** — open Settings from tray, confirm tabs + light theme look correct

---

## Files Changed This Session

| File | Change |
|------|--------|
| `hotkey_service.py` | Removed WH_KEYBOARD_LL hook; added GetAsyncKeyState poll thread; expanded VK map with OEM/numpad/nav keys |
| `voice.py` | Stale watchdog comment updated |
| `test_features.py` | +11 tests: TestHotkeyParser (9) + TestNoKeyboardHooks (2). Total: 187 |
| `installer/koda.iss` | Added wizard images, LicenseFile, VersionInfo metadata block |
| `installer/wizard_banner.bmp` | New — 164×314 branded installer banner |
| `installer/wizard_small.bmp` | New — 55×55 installer header image |
| `STATUS.md` | Updated phase status, test count, next actions |

**Uncommitted (intentional — local only):**
- `CLAUDE.md` — session notes added
- `config.json` — test snippets from dev ("orange", "red", "purple"), TTS voice changed to Zira

---

## Key Reminders

- **Kill ALL python before restart:** `taskkill //f //im pythonw.exe` AND `taskkill //f //im python.exe`
- **Run from source:** `cmd //c "C:\Users\alexi\Projects\koda\start.bat"` — DO NOT build/install exe during dev
- **Full test suite:** `venv/Scripts/python -m pytest test_features.py test_e2e.py -q` (208 tests)
- **test_stress.py** — standalone only, NOT via pytest
- **Hotkeys use RegisterHotKey** — no WH_KEYBOARD_LL anywhere. Adding one will fail the TestNoKeyboardHooks tests.
- **debug.log from exe** — when running dist/Koda.exe, log is written to temp dir (`C:/Users/alexi/AppData/Local/Temp/_MEIxxxxxx/debug.log`), NOT the project root
- **ctrl+shift+.** is the DEFAULT command hotkey (in config.py DEFAULT_CONFIG). User's personal config.json has `f8` — don't confuse the two.
- **Inno Setup images** — `installer/wizard_banner.bmp` and `installer/wizard_small.bmp` are generated by a Python snippet using Pillow. To regenerate, re-run the generation script from this session's context.
- **config.json is gitignored** — a fresh install will use DEFAULT_CONFIG values
- **No CUDA** — Intel UHD 770 only; GPU Power Mode feature built but untestable here
- **settings_gui runs as pythonw** — save_and_restart kills parent by os.getppid(), NOT all pythonw
- **GitHub CLI:** `"C:\Program Files\GitHub CLI\gh.exe"`, auth as `Moonhawk80`
- **Domain:** kodaspeak.com

---

## Migration Status

None. No database changes this session.

---

## Test Status

| Suite | Count | Status |
|-------|-------|--------|
| `test_features.py` | 187 | ✅ All passing |
| `test_e2e.py` | 21 | ✅ All passing |
| `test_stress.py` | 17/17 | ✅ Passing, 2 pre-existing warnings (no mic speech, keyboard.send needs admin for synthetic presses) |
| **Total** | **208** | **✅** |
