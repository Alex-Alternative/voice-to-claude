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

- [ ] **Lever #1 — Opt-in Groq cloud backend (`whisper-large-v3-turbo`).** ~150 LOC + a settings GUI toggle + key in `keyring`. 216× real-time, $0.04/hr, free tier covers personal use. Local CPU stays the privacy default; cloud is the speed mode. Only lever that actually closes the gap to Wispr Flow. Use forge-brainstorm before coding — multi-file, new dependency, privacy-sensitive (audio leaves the machine).
- [ ] **Lever #2 — A/B `cpu_threads` at 1 vs 4 vs 8 on UHD-770 host.** Five-minute test: change `config.json`, dictate the same 60s clip three times per setting, compare `Transcribe timings` lines in `debug.log`. faster-whisper issue #526 documents 4 as pessimal on Intel parts. Possibly free 1.5–2×. Do FIRST — pins the local-CPU ceiling honestly before deciding how aggressively to push the cloud rollout.
- [ ] **Lever #3 — "Speed mode" toggle: `small` → `tiny` per mode.** Per-mode (chat dictation = OK to use tiny; prompt-assist = NOT OK, LLM amplifies misheard words). PyInstaller bundle already supports multi-model fallback via `voice.py:392`. Trivial wiring + a settings checkbox.

Don't do: ship `large-v3-turbo` on local CPU (counterintuitively slower than `small`); switch default `small`→`tiny` for everyone; rebuild on OpenVINO until cloud lever is done.

Also worth flagging: `config.json` says `streaming: true`, but `voice.py:832-855` only streams the tray-tooltip *preview*, not the paste. Final paste at line 909 re-transcribes from scratch. Real paste-time streaming via `whisper_streaming` is a separate ~3-5× perceived-speed lever (lever #c in the research write-up, ranked below #1 because it's higher-effort).

## Small fixes (discovered during live-test)

- [ ] **Port v2 pickers to Inno Setup installer** — `configure.py` has `setup_prompt_voice` + `setup_prompt_backend` (Step 9 + Step 10 of Python wizard) but Inno installer bypasses configure.py entirely. End users never see the v2 pickers unless they manually run `venv\Scripts\python configure.py` post-install. Port to Pascal `[Code]` pages in `installer/koda.iss`.
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
