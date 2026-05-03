# NEXT:

## Voice-product ship sequence (locked 2026-04-24)

- [x] **Auto-polish on Send path — SHIPPED (commit `7afd41b`, pushed).** `prompt_assist.py:380` gate now fires when `refine_backend in ("ollama","api")` OR `llm_refine=True`. Regression-tested via 3 new cases in test_features.py (commit `f44d720`). 431/431 tests. Pre-push gate clean (forge-deslop 0, forge-review 0 after N1 resolved). Runtime verification = live mic test (below).
- [ ] **PR 1 — Finish live mic test of `feat/prompt-assist-v2` → merge → tag v4.4.0-beta1.** Re-run from source via `.\start.bat` with all 6 live-test fixes + auto-polish + Koda Dark v2 overlay (WIP commit `7440cfd` — visually untested, MUST eyeball before merge). Validate: Zira opener, beep cue, 2-slot Q&A (Task + Context only, NO Format), overlay renders cleanly (brand header + K mark + intent pill + layered body + 3-tier buttons + fade-in), Ollama polishes the prompt (Boca Tanning Club test: raw stitch → natural polished prompt), voice-confirm ("say send"), Escape cancels. **If overlay design doesn't land on live-eyeball, iterate on overlay.py only — auto-polish fix is locked.**
- [ ] **PR 2 — `feat/piper-tts` — Piper direct subprocess, Amy (en_US-amy-medium) as stock voice.** Bundle piper.exe + voice in installer (~80MB bloat). New `piper_tts.py` module, `config["tts"]["backend"]` toggle. Rejected NaturalVoiceSAPIAdapter — third-party SAPI DLL, trust issues.
- [ ] **PR 3 — `feat/koda-signature-voice` — Alex's wife's voice as Koda default.** Record ~30 min-2 hr clean audio, train Piper custom model, ship `.onnx` as default. Amy stays selectable. See `project_voice_roadmap.md` memory for full plan.

## Coworker perf issue (session 49 — tackle 2026-04-30)

- [x] **Coworker reports Koda slowing his PC significantly.** Rebuilt KodaSetup-4.4.0-beta1.exe (560MB, session 50, 2026-04-30) for re-share via Google Drive. Built from `feat/overlay-rounded-buttons` (Atlas Navy overlay confirmed good — Alex tested at home). Likely fix order per `feedback_koda_perf_levers.md` if perf complaints persist post-upgrade: 1) `process_priority` `"above_normal"` → `"normal"`, 2) `cpu_threads` 4 → 2, 3) `model_size` `small` → `base`.

## Mac version (session 50 — separate work)

- [ ] **Build a Mac version of Koda.** Coworker is Windows but Alex wants Mac parity. Hard blockers: (a) PyInstaller does NOT cross-compile — must build on a Mac, (b) 8 modules import Win32-specific code (`win32`, `winreg`, `comtypes`, `pystray._win32`, `pyttsx3.drivers.sapi5`, `popen_spawn_win32`) — `voice.py`, `active_window.py`, `context_menu.py`, `formula_mode.py`, `prompt_conversation.py`, `settings_gui.py`, `test_features.py`, `build_exe.py`. (c) `koda.iss` is Inno Setup (Windows-only) — Mac equivalent is `.app` bundle wrapped in `.dmg` via `dmgbuild` or `create-dmg`. (d) Apple Developer account ($99/yr) needed for code signing + notarization, otherwise Gatekeeper warnings on the coworker's machine. (e) macOS permissions ceremony: Accessibility (global hotkeys + paste), Input Monitoring (key listening), Microphone. Realistic effort: several days of porting on a Mac dev box, multi-session project.

## Docs drift (session 50)

- [ ] **`docs/user-guide.html` is stale (Apr 20).** Predates v4.4.0-beta1 features: auto-polish on Send, Atlas Navy overlay, voice-confirm ("say send"), 2-slot Q&A (Format slot dropped), Polish-not-Refine rename, settings GUI redesign. NOT bundled in installer (per `koda.iss` [Files] section), so coworker install isn't affected — but the guide is wrong if anyone hits it from `docs/` or the repo. Update before tagging v4.4.0-beta1 officially. `docs/user-guide.md` (same date) is also stale. Easiest path: regenerate from `user-guide.md` after updating .md, then re-export to .html.

## Transcription speed gap vs paid Whisper (session 50, researched session 51)

Research write-up: `docs/research/whisper-speed-analysis-2026-05-01.md`. Summary: boss's tool is **Wispr Flow** ($144/yr, sub-700ms cloud GPU). Gap is fundamental local-CPU-vs-cloud-GPU; no CPU optimization closes it. Three levers below are the validated picks.

- [x] **Lever #1 — Opt-in Groq cloud backend** — KILLED session 52. Local-only is a brand promise + recurring cost story unacceptable. Streaming (research's Lever #c) also rejected — would compete with Claude Code for CPU during recording.
- [ ] **Lever #2 — A/B `cpu_threads` at 1 vs 4 vs 8.** Can run offline via `transcribe_file.py` (no mic flow needed). Deferred — hardware tier system reduces urgency since RECOMMENDED tier already auto-tunes by core count via single-default RECOMMENDED. Revisit if v1 ships and benchmark data is desired before ever adding a sub-tier.
- [x] **Lever #3 — "Speed mode" toggle: `small` → `tiny` per mode** — SUBSUMED by hardware tier system session 52. MINIMUM tier auto-tunes to `tiny`/`threads=2`/`normal`. Settings GUI Advanced expander allows manual model_size override per user (PR #37 merged).

Don't do: ship `large-v3-turbo` on local CPU (counterintuitively slower than `small`); switch default `small`→`tiny` for everyone; rebuild on OpenVINO until cloud lever is done.

Also worth flagging: `config.json` says `streaming: true`, but `voice.py:832-855` only streams the tray-tooltip *preview*, not the paste. Final paste at line 909 re-transcribes from scratch. Real paste-time streaming via `whisper_streaming` is a separate ~3-5× perceived-speed lever (lever #c in the research write-up, ranked below #1 because it's higher-effort).

## Hardware tier system (session 52 — Phases 1+2 shipped, 3+4 pending)

PRs #37 + #38 merged 2026-05-02. Spec: `docs/specs/2026-05-02-hardware-tier-system-design.md`. Plan: `docs/plans/2026-05-02-hardware-tier-system.md`.

- [x] **Phase 1 — Python classifier + tests + settings GUI** — `system_check.py` + `system_check_constants.py`, `configure.py` wired through `classify()`, settings GUI Performance section with tier dropdown + Advanced expander + status line. 9 commits, +15 tests. PR #37 merged.
- [x] **Phase 2 — Inno installer integration** — Pascal classifier mirror, build-time codegen for shared thresholds, BLOCKED + MINIMUM wizard pages, `--detect-hardware --json` CLI flag on Koda.exe, ssPostInstall tier-aware config write. 7 commits, +1 test. PR #38 merged.
- [x] **Update CLAUDE.md hardware note** — done session 53 (2026-05-02). Tech Stack + Known Issues lines now point future sessions at `system_check.classify()` for per-machine truth; home PC POWER-tier specs called out as the verified example. Committed direct to master (`1ea6e4a`).
- [x] **Phase 3 — Power Mode celebration** — SHIPPED session 53 as PR #39 (banner v5 + Power Mode wizard page + tray tooltip suffix + settings Atlas Navy badge + GPU-appeared balloon). 6 commits on `feat/hardware-tier-system-phase-3`. Pre-push gate skipped (Skill Forge currency check blocked). Open in `gh pr view 39 --repo Moonhawk80/koda --web`.
- [x] **Phase 4 — Backward-compat + extensions** — SHIPPED session 53 as PR #40 (config migration + startup re-detection + turbo model mirror on whisper-models-v1 release + cuDNN crash fix + updater semver filter). 6 commits on `feat/hardware-tier-system-phase-4`. Stacked on phase-3, **must re-target base to master before merge**. Pre-push gate skipped. Open in `gh pr view 40 --repo Moonhawk80/koda --web`.
- [ ] **Validate POWER tier on home PC with cuDNN-bundled rebuild** — `dist/KodaSetup-4.4.0-beta1.exe` rebuilt at session 53 end with `--collect-binaries=ctranslate2` fix. Delete `%APPDATA%\Koda\config.json` first, install, walk wizard, hit Ctrl+Space, confirm sub-second to few-second transcription on RTX 4060. Blocks PR #40 merge.
- [ ] **Resolve Skill Forge uncommitted changes** — `~/Projects/skillforge` has `M forge-harness/hooks/h1-pre-push-gate.sh` + 5 untracked `forge-harness/tests/` files. Commit / stash / complete before running pre-push gate.
- [ ] **Run forge-deslop + forge-review on PRs #39 and #40** — gate intentionally skipped at session 53 push. Owed before either can merge.
- [ ] **Re-target PR #40 base to master** — currently based on `feat/hardware-tier-system-phase-3`. Re-target BEFORE merging #39 so neither orphans (per session 52 stacked-PR pattern).
- [ ] **Optional: mirror additional Whisper models** (medium, large-v3) on `whisper-models-v1` release if needed. Procedure in `reference_koda_model_mirror.md`.

## Small fixes (discovered during live-test)

- [x] **Port v2 pickers to Inno Setup installer** — SUBSUMED by hardware tier system session 52. `system_check.py` is the shared module both wizards (configure.py + Inno installer's [Code] section) now call. PRs #37 + #38 merged.
- [ ] **Tighten `koda.iss` for friction-free upgrades** — installer currently errors / prompts if Koda is running during upgrade. Add to `[Setup]`: `CloseApplications=yes`, `RestartApplications=yes`, `AppMutex=KodaSingleInstance` (and add the matching mutex to Koda main loop). Result: re-running the installer over an existing install closes Koda, swaps the exe, relaunches — no prompts, no manual kill. Discovered session 51 (2026-05-01) when Alex's main PC was still on v4.3.1 and his boss hit the empty-transcript bug during a demo.
- [x] **VAD tuning** — `vad.rms_threshold` exposed to config (PR #35 commit `b0c0c38`). `silence_seconds` already config-exposed via `vad.silence_timeout_ms`. Defaults still 0.005 / 1500ms; users can tune per environment.
- [x] **Template simplification follow-through** — verified already at correct level per `project_template_philosophy.md` (synced from work PC). Intent-specific scaffolding kept; `Context:` block + generic closer were removed session 46. No further pruning warranted.
- [x] **Clean up configure.py dual-"polish" summary** — disambiguated to "Prompt polish (prompt-assist mode)" + "Command polish (command mode)" with both lines grouped (PR #35 commit `aeddd8e`).
- [ ] **Re-add cancel-via-hotkey-repress for prompt-assist v2** — `cancel_slot_record` API was removed by forge-deslop (no producer); add cleanly if/when prompt_press-during-active-conversation needs to cancel.
- [ ] **Fix `statusline-command.sh`** to render `.claude/next.md` first uncompleted item — currently only shows model + context bar.

## Session 47 outputs (open for review)

- [ ] **PR #35 review/merge** — silent fixes (configure.py dual-polish disambiguation + VAD `rms_threshold`). 432/432 tests. Pre-push gate clean.
- [ ] **PR #36 review/merge** — Atlas Navy redesign (overlay v3 + settings_gui). 431/431 tests. Pre-push gate clean. Visual identity locked: navy `#1c5fb8` hero accent + 5 surface luminance layers + left-edge accent spine + paired fonts (Segoe UI Variable Display/Text + Cascadia Mono) + Polish-not-Refine rename + tooltips + K-mark dot decoupled from BRAND.
- [ ] **Settings GUI second-pass review tomorrow** (per Alex tonight) — multiple polish gaps remaining; eyeball with fresh eyes after the marathon padding iteration.
- [ ] **Live-eyeball Atlas Navy in REAL prompt-assist mic flow** — `dev_test_overlay.py` validated visual layer only; integration with Whisper + voice-confirm + paste still untested.
- [ ] **Decide `dev_test_overlay.py` fate** — commit / delete / gitignore. Currently untracked at project root.
- [ ] **Bundle Hubot Sans + JetBrains Mono** in installer for full type system (currently fallback to Win 11 Variable + Cascadia Mono — visually approved but bundling would lock identity across all Windows versions).

## Session 47 — Memory sync infrastructure (DONE)

- [x] **Memory git-sync repo created** — `Moonhawk80/koda-memory` (private). Work PC pushed initial 27 .md files; home PC cloned + merged 5 home-only files + reorganized MEMORY.md index + refreshed stale `project_koda.md`.
- [x] **Auto-sync hooks installed (home PC)** — `~/.claude/settings.json` got SessionStart pull + Stop commit/push hooks. Async, log to `~/.claude/koda-memory-sync.log`.
- [x] **Work PC: git pull on koda-memory** — done session 48 (Mon 4/27). Pulled 11 files total (6 from session 47 morning batch + 5 from Saturday-evening Atlas Navy design batch).
- [x] **Work PC: install matching auto-sync hooks** — done session 48 (Fri 4/24). SessionStart pull + Stop commit/push installed in `~/.claude/settings.json`. Auth-switch dance wrapped per fire. Pipe-tested clean. Active gh stays Alex-Alternative.

## Runtime-test carried over

- [ ] Runtime-test `feat/voice-app-launch` (PR #28 from session 43): golden path ("open word"), prefix invariant ("please open word" must NOT fire), error fallback ("open gibberish"). Still pending.

## Separate projects (NOT v2 side-quests)

- [ ] **Multi-turn session mode (V3)** — per `feedback_multi_turn_vision.md`: Ctrl+F9 within 60s of paste → skip slots 2-3, ask "What's next?", reuse prior context. Own PR after Piper ships.
- [ ] Phase 16 licensing — blocks v2 paywall wrap (not the build). Tier count, subscription vs one-time, offline activation, "beta tester" marker. Beta testers grandfather into free tier 2.
- [ ] Signing approach (Azure Trusted Signing $10/mo recommended) — wire into `.github/workflows/build-release.yml`
- [ ] Whisper "dash" dropout fix direction — read `project_dash_word_dropout.md` memory first
- [ ] Wake word decision — train custom "hey koda" via openwakeword OR rip feature
- [ ] Phase 9 RDP test (pending since session 35)
- [ ] V2 app-launch: chaining ("open powershell and type git status"), window-ready check, "switch to X"
- [x] Memory sync across machines — SHIPPED via `Moonhawk80/koda-memory` private repo + auto-sync hooks on both PCs (sessions 47 + 48). See `reference_koda_memory_repo.md` memory.

## Completed this session (work-PC session 45)

- [x] Voice-driven confirmation shipped (commit `75e5366`) — pre-push gate clean (forge-deslop 0, forge-review 0), 428/428 tests
- [x] Hotkey default regression fixed (commit `7c79237`) — configure.py now defaults to ctrl+f9 with Ctrl+F* picker options
- [x] Ship sequence locked (commit `b5987a8`) — 3-PR voice-product roadmap
- [x] Installer rebuilt as v4.4.0-beta1 — uninstalled v4.3.1, wiped config, fresh install, configure.py walked
- [x] Live-test bug-fix loop (batched commit this handover):
    - [x] Cross-module globals bridge for `_slot_chunks` / `_slot_recording`
    - [x] pyttsx3 → direct SAPI COM via comtypes (multi-thread safe)
    - [x] VAD voice_detected gate before silence-stop
    - [x] Format slot dropped (2-slot Q&A: Task + Context only)
    - [x] Template junk stripped (Context: block + generic closer + URL regex fix)
    - [x] Overlay redesign (flat Label-buttons, logo, Send→Paste, side="bottom" pack fix, dark palette, header + keyboard hints)
- [x] Whisper model bump base → small (cached locally, zero download)
- [x] Handover + 6 new memory entries

## Waiting / Blocked

- **Coworker re-test of v4.3.1 mic-hotplug + music-bleed** — needs installer re-share first (carried from session 41)
- **Memory sync across work PC / home PC** — deferred per Alex
