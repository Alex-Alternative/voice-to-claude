# Alex Session 25 Handover — 2026-04-14

## Branch
`master` — clean, up to date with `origin/master`. All changes pushed.

---

## What Was Built This Session

### 1. Exe + Installer rebuilt on Work PC with staleness fix
- Built `dist/Koda.exe` (530 MB) via `build_exe.py` — includes the staleness fix from PR #3
- Built `dist/KodaSetup-4.2.0.exe` via `build_installer.py`
- Both built directly on work PC (`C:\Users\alex\`) — Whisper model and Inno Setup 6 were already present
- **Work PC formal install test: COMPLETE** — Koda installed and running from exe

### 2. Fixed: Model mismatch crash on fresh installs (PR #4, merged)
- **Bug:** `config.py` defaulted `model_size = "base"` but the exe only bundles `_model_small`. On a fresh machine with no HuggingFace cache, faster-whisper tried to download the "base" model, failed with no internet, and showed "Check internet connection" error.
- **Fix:** Changed `DEFAULT_CONFIG["model_size"]` from `"base"` to `"small"` in `config.py`
- **Also fixed:** Error message on model load failure — removed misleading "Check internet connection" hint, now says "Try reinstalling Koda"
- **File:** `config.py` line 27

### 3. Fixed: Desktop shortcut removed from installer (PR #4, merged)
- The `koda.ico` has a transparent background that looked broken/see-through on light desktops
- Removed `desktopicon` task from `installer/koda.iss` entirely
- Removed the `{autodesktop}` icon entry from `[Icons]` section
- Start Menu shortcut and auto-start task remain
- **File:** `installer/koda.iss`

### 4. Fixed: Overlay disabled by default
- The floating overlay (logo + green light) shown on screen did nothing useful and didn't sync with tray icon state
- Changed `DEFAULT_CONFIG["overlay_enabled"]` from `True` to `False` in `config.py`
- Existing installs: user can disable via Settings → overlay toggle, or right-click tray → Settings
- **File:** `config.py` line 64

### 5. Fixed: build_installer.py now cleans up intermediate Koda.exe
- `dist/` was accumulating both `Koda.exe` and `KodaSetup-4.2.0.exe` after every build
- Added cleanup step at end of `build_installer.py` to delete `Koda.exe` after installer compiles
- **File:** `installer/build_installer.py`

### 6. Deleted CLAUDE.md.bak
- Leftover from session 24 git pull conflict, no longer needed

### 7. Session 25 home PC prompt written
- Full prompt added to top of `docs/sessions/home-pc-session-prompt.md`
- Covers: installer wizard pages (3 pages), mic verification, formula mode, coworker install bug fixes

### 8. User guide created (`docs/user-guide.md` + `docs/user-guide.html`)
- Plain markdown version and a styled HTML version (dark header, tables, steps, mic quality badges)
- HTML can be printed to PDF from browser (Ctrl+P → Save as PDF)
- Covers: what Koda is, installation, hotkeys, mic guide, troubleshooting, uninstall

### 9. Video script prompt created (`docs/video-script-prompt.md` + `.txt`)
- 90-second 6-scene demo script for HeyGen/Synthesia/Loom
- `.txt` version for easy sharing/printing
- Narration-only version extracted for direct paste into HeyGen Quick Create

---

## Decisions Made

### Work PC can build exe (not just home PC)
Both the Whisper model (`~/.cache/huggingface/hub/models--Systran--faster-whisper-small/`) and Inno Setup 6 are installed on the work PC. No need to go to home PC for builds.

### Overlay is a dead feature for now
The floating overlay doesn't sync correctly with tray state and provides no value to end users. Disabled by default. Can be re-enabled in Settings if ever fixed properly.

### Desktop shortcut removed permanently
Koda is a tray app — the entry point is the tray icon. Desktop shortcuts with transparent icons cause confusion for new users. Removed from installer entirely, not just unchecked by default.

### model_size default must match bundled model
The build script bundles `_model_small`. The config default must be `"small"` to match. Any future change to which model is bundled must update both `build_exe.py` AND `DEFAULT_CONFIG["model_size"]`.

### Code signing deferred
~$100-200/yr for OV cert, ~$300-500/yr for EV (bypasses SmartScreen instantly). Not worth it until public launch. Coworkers told to click "More info → Run anyway".

### Coworker trial is OK, public release is not yet
The installer is stable enough for a friendly coworker test. Not ready for public/Product Hunt — wizard pages and GitHub Release still pending.

### Formula mode: rules-based + Ollama fallback
Formula mode (speak → Excel formula) will use rules-based conversion as tier 1 (covers 90% of common formulas, no dependencies), Ollama as tier 2 fallback if enabled. Installer will mention Ollama as optional.

---

## User Feedback & Corrections

- **"I wanted to add a feature like helping prompting, helping excel formula fill in"** — Led to Formula Mode feature plan added to session 25 prompt. This is a new direction for Koda beyond pure dictation.
- **"well im fucked and wasted my time claude has a / voice command that transcribes with the spacebar"** — Clarified: Claude's voice only works inside Claude's text box. Koda is system-wide (every app). Not the same thing.
- **"the floating thing on the right does nothing but show the logo and the green light that doesnt ever match the tray icon"** — Overlay disabled by default.
- **"you keep building two exe files"** — Fixed: `build_installer.py` now deletes `Koda.exe` after building the installer.
- **"I thought we fixed the SmartScreen warning"** — Clarified: SmartScreen fix only applies to locally built files. Files downloaded by others still get Mark of the Web and trigger SmartScreen. Only code signing cert fixes it permanently.
- **"not the desktop shortcut the floating thing on the right"** — User meant the overlay, not the desktop .lnk shortcut. Important distinction.

---

## Waiting On

- **Home PC session 25** — installer wizard pages (hold/toggle, model quality, mic verification), formula mode, bug fixes from coworker test
- **Coworker test results** — coworker installed fixed exe (model mismatch fixed); waiting to hear if it works now
- **RDP test** — Phase 9 Test 3 still pending
- **GitHub Release** — `KodaSetup-4.2.0.exe` not published; waiting on wizard pages + more testing
- **Phase 13 feature gates** — free/Personal/Pro tiers, license keys, LemonSqueezy still not started
- **kodaspeak.com** — domain chosen but not verified if actually purchased; check registrar

---

## Next Session Priorities

1. **Home PC — session 25 prompt** — pull master, run installer wizard task + formula mode + bug fixes
2. **Coworker follow-up** — confirm model mismatch fix resolved their issue; get feedback on Koda usage
3. **RDP test** — Phase 9 Test 3 (work PC → home PC via RDP, Ctrl+Space)
4. **GitHub Release** — publish `KodaSetup-4.2.0.exe` once wizard pages are done
5. **Overlay fix or removal** — either sync it properly with tray state or remove the feature entirely

---

## Files Changed

| File | Change |
|------|--------|
| `config.py` | `model_size` default: `"base"` → `"small"`; `overlay_enabled` default: `True` → `False` |
| `voice.py` | Improved model load error message (removed "Check internet connection") |
| `installer/koda.iss` | Removed desktop shortcut task and icon entry |
| `installer/build_installer.py` | Added cleanup — deletes `Koda.exe` from `dist/` after installer build |
| `docs/sessions/home-pc-session-prompt.md` | Session 25 prompt added at top (wizard pages + formula mode + bug fixes) |
| `docs/user-guide.md` | New — user guide for coworker distribution |
| `docs/user-guide.html` | New — styled HTML version of user guide (printable to PDF) |
| `docs/video-script-prompt.md` | New — 90-second AI video script prompt for HeyGen/Synthesia |
| `docs/video-script-prompt.txt` | New — plain text version of video script (untracked) |

**Deleted:**
- `CLAUDE.md.bak` — leftover from session 24 pull conflict

---

## Key Reminders

- **model_size default = "small"** — must always match what `build_exe.py` bundles. Currently bundles `_model_small`. If you change the bundled model, update `DEFAULT_CONFIG["model_size"]` too.
- **Overlay is off by default** — if a user reports missing overlay, it's a Settings toggle
- **dist/ only has KodaSetup-4.2.0.exe now** — `build_installer.py` auto-deletes `Koda.exe` after build
- **Desktop shortcut gone** — removed from installer entirely, not a regression
- **SmartScreen on shared files** — locally built exe is fine, downloaded exe triggers SmartScreen. Tell recipients "More info → Run anyway"
- **Coworker install** — had "no internet" error (model mismatch, now fixed) + overlay floating thing (now off by default). Send them the new `KodaSetup-4.2.0.exe` from `dist/`
- **kodaspeak.com** — verify it's actually registered before building a landing page
- **CLAUDE.md in repo has home PC paths (alexi)** — correct on home PC, misleading on work PC
- **Work PC exe path:** `C:\Users\alex\AppData\Local\Programs\Koda\Koda.exe`
- **taskkill on work PC bash:** `cmd //c "taskkill /F /IM Koda.exe /IM pythonw.exe /IM python.exe"`

---

## Migration Status

None this session.

---

## Test Status

| Suite | Count | Status |
|-------|-------|--------|
| `test_features.py` | 187 | ✅ Unchanged |
| `test_e2e.py` | 21 | ✅ Unchanged |
| **Total** | **208** | **✅** |

No new tests added. Config default changes and installer changes are not unit-testable.
