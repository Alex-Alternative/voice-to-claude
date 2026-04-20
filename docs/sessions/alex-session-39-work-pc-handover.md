# Work-PC Session 39 Handover — 2026-04-20

Written from work PC for home-PC Claude to pick up. Parallel to home-PC's session 38 (which happened 2026-04-18 and shipped the settings redesign + DPI fix + minimal-modern icon).

## TL;DR — what the work-PC install test found

1. **Installer works** (after fixing stale AppData config mismatch). Koda installs to `C:\Program Files\Koda\`, shortcuts land correctly, model loads, dictation works.
2. **Two real bugs surfaced on the installer path.** Both fixed + merged this session:
   - **PR #16 (merged)** — `_model_base` in stale config vs `_model_small` bundled in exe → "Failed to load speech model — try reinstalling" crash. Now falls back to whatever's bundled and self-heals config.
   - **PR #17 (merged)** — Settings Save killed Koda, never relaunched on installed machines. Replaced `save_and_restart` with `save_and_close` (no taskkill, just save + info dialog if hotkey/model changed).
3. **Three other PRs merged** along the way (user did bulk merge): **#14** (GitHub Actions release workflow), **#15** (phase planning doc).
4. **One UX gap remains** — theme toggle in Settings Appearance tab still looks like it needs a restart per the email test plan; actual live re-theme via `_apply_theme` already works on toggle, but `save_and_close` dialog is shown even for theme-only changes if user also touched hotkeys. Not critical.
5. **One memory anomaly to investigate** — current running Koda.exe at 1.04 GB (normal is ~370 MB for loaded small model). Might be a zombie / double-load. See below.

## What got merged to master this session

```
8b706b8 Merge pull request #14 (GitHub Actions release workflow)
1bbee45 Merge pull request #15 (phase planning doc + work-PC session 36 handover)
113ca16 Merge pull request #16 (model-load bundled fallback)
#17 (merged before #16/#15/#14) — settings save/close refactor
```

Plus 3 rename commits to disambiguate work-PC session handovers from home-PC ones. See "Naming collision" below.

## Detailed bug reports

### Bug 1: model-load crash on stale config (fixed in PR #16)

**Repro:**
- Machine has old Koda install with `AppData\Roaming\Koda\config.json` containing `"model_size": "base"` (from an earlier build that bundled `_model_base`).
- Install the new v4.2.0 build which only bundles `_model_small`.
- Koda starts → reads stale config → tries `_model_base` → not there → falls back to HF Hub cache → cache has broken symlinks or wrong blobs → `RuntimeError: Unable to open file 'model.bin'` → popup "Failed to load speech model 'base'. Try reinstalling Koda."

**Fix:** `voice._discover_bundled_models()` enumerates `_model_*` dirs in `_MEIPASS`. On primary load failure, tries any other bundled model and persists the corrected size to config. 6 new tests in `test_features.py`. Fail-then-pass proven.

### Bug 2: settings Save killed Koda (fixed in PR #17)

**Repro (on the old installer):**
- Open Settings from tray → flip theme → click Save
- Old `save_and_restart` ran `taskkill /f /pid <parent_pid>` then `Popen(["pythonw.exe", "voice.py"])`
- On installed frozen exe, there's no `venv/Scripts/pythonw.exe` → Popen fails silently → Koda dies forever
- Also leaves `_MEI*` temp dir behind (because `taskkill /f` denies PyInstaller bootloader cleanup) → "failed to remove temporary directory" popup on subsequent launches

**Fix:** Replaced `save_and_restart` with `save_and_close`. No more taskkill on Save. Diffs `RESTART_REQUIRED_KEYS` (hotkeys, model_size, compute_type, mic_device, streaming, hotkey_mode) before/after save; shows a `messagebox.showinfo` listing changed keys only if any actually need a relaunch. Closes window either way. 5 new tests. Fail-then-pass proven.

## What needs to happen next at home

**In rough priority order:**

1. **Pull master** — `git pull origin master` at home. Should fast-forward cleanly.
2. **Rebuild the installer** — `build_exe.py` then `installer/build_installer.py`. The two bug fixes need a rebuilt installer to take effect on installed machines.
3. **Cut `v4.3.0` tag** — PR #14 is now merged, so tagging `v4.3.0` will auto-build and upload via GitHub Actions. First real test of the CI workflow. `git tag v4.3.0 && git push origin v4.3.0`.
4. **Investigate 1 GB Koda memory anomaly** — on the work PC, main Koda.exe idled at 1,041,392 K after relaunch. Normal is ~371 MB. Could be:
   - Double-load (two WhisperModel instances, one from old session, one from new)
   - Hotkey_service subprocess leaked file handles during the multiple kill/relaunch cycles today
   - Actual regression in the current build
   Reproducing: fresh install, leave idle for 5 min, check memory.
5. **Consider live-applying theme in Settings without even the info dialog** — the code already live-themes via `_apply_theme` on toggle, so the current behavior is OK, but a user toggling theme + hitting Save will still see the hotkey/model info dialog only if they ALSO touched those keys. If they only touched theme, Save is silent. So this is actually working correctly.
6. **Stress-testing Blocks 4 and 5 still pending** — from session 34/35. Correction mode (Ctrl+Alt+C / Ctrl+Shift+Z per user config), readback (Ctrl+Alt+R), readback-selected (Ctrl+Alt+T per user config). Did not run today — the Save bug eat the budget.

## Smoke test results from today (work PC, installer path)

Email plan had 6 tests. Results:

| Test | Result |
|---|---|
| 1. Dictation (Ctrl+Space in Notepad) | ✅ PASS |
| 2. Settings window size + rounded buttons + theme | ✅ PASS |
| 3. Theme toggle live re-theme | ⚠️ PARTIAL — theme saves fine, but the full-process restart that old Save triggered was broken; fixed in PR #17 |
| 4. Words tab (treeview rows, Export button, 2-row buttons) | ✅ PASS |
| 5. Persistence (tray Quit + desktop-shortcut relaunch) | ✅ PASS |
| 6. Phase 9 RDP test | ⏭️ NOT RUN — did not get to it |

## Naming collision handled

Home-PC Claude and work-PC Claude both wrote session handovers with `alex-session-NN-handover.md` filenames in parallel. Today's conflicts: home had session 35 + session 36; work PC also wrote session 35 and session 36 on its branches. Resolved by renaming the work-PC versions to `-work-pc-handover.md` suffix. Both sessions' records now survive. Files now on master:

- `alex-session-35-handover.md` (home, forge-test / track 3 / HP1 work)
- `alex-session-35-work-pc-handover.md` (work, GitHub Actions workflow PR)
- `alex-session-36-handover.md` (home, context)
- `alex-session-36-work-pc-handover.md` (work, phase planning PR)
- `alex-session-37-handover.md` (home, frozen-exe parity)
- `alex-session-38-handover.md` (home, settings redesign + icon + DPI)
- `alex-session-39-work-pc-handover.md` (THIS FILE — work, install test + two bug fixes)

**Suggestion:** future work-PC sessions use `-work-pc-` suffix from the start. Home-PC sessions keep plain `-handover.md`. Avoids the rebase pain we hit today.

## Current state on the work PC

- Branch: `feat/github-actions-release-build` (will clean up after handover commit)
- Working tree: dirty (this handover file about to be committed)
- Koda installed at `C:\Program Files\Koda\` — the OLD v4.2.0 build (before today's fixes merged). Running but has 1 GB memory anomaly flagged above.
- `AppData\Roaming\Koda\config.json`: hand-patched `model_size` from `base` to `small` (the manual fix before PR #16 was in); otherwise user's own settings intact.

## Open questions for home-PC Claude

1. Do you want me to push a handover commit to a fresh branch + PR, or merge directly to master? (Last PR #15 merged via squash, so small doc commits to master are fine.)
2. The phase planning doc PR #15 merged with the strawman tier matrix. User still needs to make 3 decisions: subscription vs one-time, offline activation, tier count. Don't start Phase 16 code until those are made.
3. Should `save_and_close` also offer a "Quit & relaunch" button in the restart-required dialog, so user doesn't have to quit-from-tray manually? Small UX win, not blocking.

## Reminders (from earlier sessions, still relevant)

- Kill ALL python before restart: `taskkill //f //im pythonw.exe && taskkill //f //im Koda.exe`
- Work PC work is **PR-only** — no direct pushes to master on Moonhawk80 repos
- Test suite: `venv/Scripts/python -m pytest test_features.py` (or `unittest test_features`). 353 tests after today's merge.
- Hotkey rules: `ctrl+alt+letter` or F-keys only.
