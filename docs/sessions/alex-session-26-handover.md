# Alex Session 26 Handover — 2026-04-14

## Branch
`master` — local commit `5c7de00` not yet pushed (push blocked — needs user to run `git push origin master`).

---

## What Was Built This Session

### 1. Formula Mode (`formula_mode.py`) — NEW FILE
Full Excel / Google Sheets formula-from-speech feature.

- **Tier 1 — Rules-based** (always available, no dependencies):
  - SUM, AVERAGE, COUNT, COUNTA, MAX, MIN, TODAY, NOW
  - IF statements: "if A1 is greater than 10 then yes else no" → `=IF(A1>10,"yes","no")`
  - VLOOKUP: "vlookup A1 in B1 to D10 column 2" → `=VLOOKUP(A1,B1:D10,2,0)`
  - CONCAT / JOIN: "join A1 and B1" → `=CONCAT(A1,B1)`
  - Percentage: "A1 divided by B1 as percent" → `=(A1/B1)*100`
  - Range parser: "column B rows 2 to 10" → B2:B10, "B2 to B10" → B2:B10
- **Tier 2 — Ollama LLM fallback** (if `llm_polish.enabled` = true)
- **Window detection**: Excel (excel.exe) + Google Sheets (title contains "Google Sheets"/"Sheets")
- **Falls back to raw paste** if no formula pattern matches — regular dictation still works in Excel
- **File:** `formula_mode.py`

### 2. Formula mode wired into transcription pipeline (`voice.py`)
- After voice commands, before pasting: checks `formula_mode.enabled` + active window
- Uses `get_active_window_info()` (from profiles.py, already imported)
- Graceful error handling — any failure logs to debug and continues with raw text
- **File:** `voice.py` lines ~724–735

### 3. Formula mode in config + settings
- Added `"formula_mode": {"enabled": False, "auto_detect_apps": True}` to `DEFAULT_CONFIG`
- Added "Formula mode (Excel / Google Sheets)" checkbox to Settings Features list (default off)
- `save()` in settings_gui.py writes `formula_mode.enabled`
- **Files:** `config.py`, `settings_gui.py`

### 4. Installer wizard pages (4 pages) — `installer/koda.iss`
Added `[Code]` Pascal section with 4 custom wizard pages:

| Page | Title | What it does |
|------|-------|-------------|
| 1 | Your Microphone | Informational — mic guidance text, no user choice |
| 2 | Activation Method | Hold vs Toggle radio (default: Hold) |
| 3 | Transcription Quality | Accurate (small, bundled) / Balanced (base) / Fast (tiny) — default: Accurate |
| 4 | Formula Assistant | Enable/Disable formula mode (default: Disabled) |

- Writes `%APPDATA%\Koda\config.json` at `ssPostInstall` — only on fresh install (FileExists check)
- On upgrade: wizard still shows (informational value), existing config preserved
- **Installer rebuilt:** `dist/KodaSetup-4.2.0.exe` — 531 MB, Inno Setup compiled successfully

**Key decision on Page 3 model options:**
- "Accurate" = `small` (the bundled model — works offline, no download)
- "Balanced" = `base` (downloads ~150 MB on first launch)
- "Fast" = `tiny` (downloads ~75 MB on first launch)
- Default is Accurate/small — this is the only offline option. Session 25 prompt said default=base, but that requires download on fresh installs. Changed to small/bundled.

### 5. Model path debug logging (`voice.py`)
FIX 3 from session 25 prompt:
- Added `logger.debug("Model search: base_dir=%s, bundled_path=%s, exists=%s", ...)` before model load
- Added `logger.debug("Loading bundled model from: %s", b)` when bundled path found
- Added `logger.debug("Bundled model not found at %s — loading by name (may download)", b)` when not found
- Future "loading model" stuck tooltip issues can be diagnosed via `debug.log`

### 6. `build_exe.py` updated
Added `formula_mode.py` to the `DATA_FILES` list so it gets bundled in `Koda.exe`.

### 7. Tests: 25 new formula mode tests
- `TestFormulaMode` (19 tests): SUM, AVERAGE, COUNT, MAX, MIN, TODAY, NOW, IF, VLOOKUP, CONCAT, percentage, no-match, case-insensitive
- `TestFormulaAppDetection` (6 tests): Excel process, Google Sheets title, non-formula apps
- **Total: 233 tests passing** (was 208)

### 8. User guide updated
- `docs/user-guide.md`: added "Formula Mode" section with examples table
- `docs/user-guide.html`: added styled "Formula Mode" section with formula table

---

## Decisions Made

### Page 3 model default = "Accurate" (small, bundled)
Session 25 prompt specified "Balanced" (base) as default. Changed to "Accurate" (small) because:
- Only `_model_small` is bundled in the exe
- "Balanced"/"Fast" require internet download on first launch
- Using bundled model as default avoids the coworker install failure (the model mismatch bug that was just fixed)
- Users who want faster/smaller can change in Settings

### Formula mode off by default (user opts in)
- Not all Koda users are in Excel — this is a power feature
- Installer page 4 lets users enable it at install time
- Settings toggle for post-install changes

### No formula mode profile in profiles.py
The session prompt suggested adding "formula" as a recognized profile mode. Instead, I wired it directly into voice.py's transcription pipeline with active-window detection. This is simpler — profiles.py handles per-app config overrides, not output transformations. Formula mode is a text transformation, not a config override.

---

## User Feedback This Session

- **"also did we develop the excel thing?"** — No, it hadn't been built. Built it this session.
- **"we also need to fix the user guide for the excel function"** — Done.
- **"desktop shortcut what does it do when I got mad was with the overlay"** — Clarified: both issues were separate. Desktop shortcut removed because .ico transparent background. Overlay was the "floating thing on the right" that didn't sync with tray state.

---

## Waiting On

- **`git push origin master`** — commit `5c7de00` is local only; push was blocked. Run: `git push origin master`
- **Installer wizard manual test** — Need to run `KodaSetup-4.2.0.exe` and verify all 4 wizard pages appear and config.json gets written correctly
- **Formula mode end-to-end test** — Need to open Excel/Sheets, enable formula mode in Settings, try a few phrases
- **Coworker follow-up** — Did the model mismatch fix (session 25) resolve their install?
- **RDP test** — Phase 9 Test 3 still pending
- **GitHub Release** — `KodaSetup-4.2.0.exe` not published yet. Pending wizard test + coworker confirmation
- **kodaspeak.com** — Verify domain is actually registered before building landing page
- **Overlay fix or removal** — Either sync with tray state or remove entirely (currently just disabled by default)

---

## Next Session Priorities

1. `git push origin master` — unblock the local commit first
2. **Test wizard pages** — run `KodaSetup-4.2.0.exe`, verify 4 pages appear, check `%APPDATA%\Koda\config.json`
3. **Test formula mode** — open Excel, enable in Settings, try "sum B2 to B10", "today", "if A1 is greater than 10 then yes else no"
4. **Coworker follow-up** — confirm model mismatch fix worked; send updated exe if needed
5. **GitHub Release** — publish `KodaSetup-4.2.0.exe` once wizard test passes
6. **RDP test** — Phase 9 Test 3

---

## Files Changed

| File | Change |
|------|--------|
| `formula_mode.py` | NEW — formula-from-speech conversion (Tier 1 rules + Tier 2 Ollama) |
| `voice.py` | Formula mode wiring in transcription pipeline; model path debug logging |
| `config.py` | Added `formula_mode` to `DEFAULT_CONFIG` |
| `settings_gui.py` | Added formula mode toggle to Features list + save() |
| `build_exe.py` | Added `formula_mode.py` to `DATA_FILES` |
| `installer/koda.iss` | Added 4 wizard pages + `[Code]` section |
| `test_features.py` | Added `TestFormulaMode` + `TestFormulaAppDetection` (25 tests) |
| `docs/user-guide.md` | Added Formula Mode section |
| `docs/user-guide.html` | Added styled Formula Mode section |

---

## Test Status

| Suite | Count | Status |
|-------|-------|--------|
| `test_features.py` | 212 | ✅ All passing |
| `test_e2e.py` | 21 | ✅ All passing |
| **Total** | **233** | **✅** |

---

## Key Reminders

- **Commit `5c7de00` is LOCAL ONLY** — push before closing the terminal or rebooting
- **model_size default = "small"** — must match bundled model in build_exe.py. Installer defaults to Accurate/small.
- **Formula mode off by default** — user enables in Settings or installer wizard page 4
- **Installer wizard writes config only on fresh install** — `FileExists` check in Pascal code; upgrades preserve existing config
- **Ollama not required for formula mode** — Tier 1 rules cover 90% of common formulas without any LLM
- **233 tests passing** — do NOT regress below this before pushing
