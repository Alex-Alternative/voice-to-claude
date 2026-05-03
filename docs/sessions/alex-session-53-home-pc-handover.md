---
session: 53
date: 2026-05-02
scope: koda
resumes-from: alex-session-52-home-pc-handover.md
continues-work-from: null
projects-touched: [koda]
skills-activated: [forge-resume, brainstorming, writing-plans, forge-handover]
---

# Home-PC Session 53 Handover — 2026-05-02

Saturday late afternoon → near midnight, home PC. Picked up Phase 3 + Phase 4 of
the hardware tier system (Phases 1+2 had merged in session 52 earlier the same
day). Shipped 12 commits across 2 stacked branches and opened both PRs (#39 +
#40) without merging. The session shipped almost the full plan but exposed two
real bugs in production validation — both tracked back to the same root cause
(installer didn't write `compute_type` to config + PyInstaller didn't bundle
cuDNN), and got fixed in-flight.

The most important non-code artifact of this session: a durable feedback memory
captured mid-session (`feedback_push_harder_on_design.md`) — Alex called out
that the early banner iterations were brochure-grade and that "this will be a
full deliverable app across the world if this works we need to better." Bar
for any user-facing visual is now top-shelf product-design quality by default.

## Branch
`feat/hardware-tier-system-phase-4` at `647d797` (pushed). 12 commits ahead of
master (6 from Phase 3 commits inherited + 6 from Phase 4). Working tree dirty:
`M config.json` (carried local state per session 45 rule, intentionally NOT
committed) + `?? dev_test_overlay.py` (decision still deferred from session
47). PR #39 open (Phase 3 → master). PR #40 open (Phase 4 → phase-3 base, will
re-target to master before merge per session 52's stacked-PR pattern).

`master` advanced one commit (`1ea6e4a`) — docs polish (CLAUDE.md hardware note
update + .claude/next.md tick-off). Pushed.

## TL;DR

1. **Resumed via `/forge-resume`** — read session 52 handover, confirmed master
   was clean post-PR-#37+#38 merges. Loaded full hardware tier system context
   into the prompt cache.
2. **Updated CLAUDE.md hardware note** — replaced stale "No NVIDIA GPU — Intel
   UHD 770 only" with a per-machine guidance line pointing future sessions at
   `system_check.classify()`, called out home PC's verified POWER-tier specs.
   Committed directly to master (commit `1ea6e4a`).
3. **Phase 3 shipped** — 6 commits on `feat/hardware-tier-system-phase-3`.
   Banner went through five iterations (v1 stock-photo → v2 too minimalist →
   v3 OK → v4 conservative → v5 monumental with bloom + light beam + UNLOCKED
   kicker label). Final v5 was Alex's "thats what I am fucking talking about"
   moment. Composite carries POWER MODE + Hardware acceleration active +
   green operational dot baked into the bitmap; Inno page chrome is dim GPU
   label + radio buttons. PR #39 opened.
4. **Phase 4 shipped + extended** — 6 commits on
   `feat/hardware-tier-system-phase-4`. Beyond the original plan tasks (config
   migration + startup re-detection), added: (a) turbo model mirror on our own
   GH release because faster-whisper's default name resolution maps
   `large-v3-turbo` to `Systran/faster-whisper-large-v3-turbo` which doesn't
   exist on HF, (b) the cuDNN bundling fix that finally made POWER tier
   actually use the GPU, (c) updater fix to filter to semver tags so the new
   `whisper-models-v1` asset release doesn't masquerade as a Koda version. PR
   #40 opened, stacked on phase-3.
5. **Validation found two production bugs** — both fixed mid-session:
   - **Bug A:** installer's Pascal `BuildTierAwareConfigJson` never wrote
     `compute_type`, so POWER tier silently ran at int8/CPU. First Ctrl+Space
     test took ~70 seconds for a 12-word sentence (~5 sec/word). Fixed by
     writing `compute_type: float16` for POWER tier in the installer + syncing
     `compute_type` in `_refresh_tier_on_startup` so existing configs auto-
     correct.
   - **Bug B:** PyInstaller bundled `ctranslate2.dll` and `libiomp5md.dll` but
     missed `cudnn64_9.dll` because cuDNN is `LoadLibrary`'d at CUDA-init time,
     not statically referenced. The moment we forced `compute_type=float16`,
     ctranslate2 tried to load cuDNN, failed, and the bootloader killed the
     process before our try/except could catch it ("Failed to execute script
     voice due to unhandled exception"). Fixed by adding
     `--collect-binaries=ctranslate2` to `build_exe.py`.
6. **Pre-push gate skipped tonight** — Skill Forge has uncommitted local
   changes blocking the currency check. Alex authorized push without
   forge-deslop + forge-review. Both gates are tomorrow's first task before
   either PR can merge.
7. **Whisper supply-chain framing** — mid-session Alex realised "we are using
   someone elses build for our Koda" and got alarmed. Talked through it: every
   serious speech app on the market uses OpenAI's Whisper (MIT-licensed),
   Koda's moat is the product layer (push-to-talk hotkey, prompt-assist,
   Atlas Navy, install flow, brand) not the model. Captured as a memory entry
   for the next time the question comes up.

## What Was Built This Session

### A. CLAUDE.md hardware note refresh (commit `1ea6e4a` — master)

Replaced the stale "No NVIDIA GPU — Intel UHD 770 only. CUDA not available."
with a per-machine guidance line that points future sessions at
`system_check.classify()` and calls out the home PC's verified specs
(i7-13650HX / 20 cores / 15.7GB / RTX 4060 Laptop / CUDA usable / POWER tier).
Also updated the "Power Mode untestable" line to point at `classify()` over
any hardcoded assumption. Marked the corresponding `.claude/next.md` todo as
done. Docs-only commit, pre-push gate exempt per scope rule. Pushed directly
to master.

### B. Phase 3 — Power Mode celebration (PR #39, branch `feat/hardware-tier-system-phase-3`, 6 commits)

`828751a` — assets(installer): AI-generated Atlas Navy background v1
- ChatGPT-generated 1024×1024 PNG saved as `installer/power_banner_bg.png`
- Re-saved via PIL on import to strip OpenAI's C2PA Content Credentials
  manifest (the `caBX` chunk DALL-E embeds in every export — cryptographically-
  signed "made by ChatGPT" provenance that would otherwise be inspectable in
  the public-ish repo)

`4b24871` — feat(installer): build script composites K-mark on AI background
- `installer/build_power_banner.py` — PIL one-shot that resizes the AI
  background to 600×300, centres the koda.ico K-mark at 96×96, writes
  `installer/power_banner.bmp` for ISCC consumption

`42d460b` — feat(installer): Power Mode celebration wizard page
- `installer/koda.iss` `[Code]` — `PowerPage` created in `InitializeWizard`
  when `DetectedTier='POWER'`. `CreatePowerPageContent` adds the banner
  bitmap, body labels, and Continue/Standard radio choice. `CurPageChanged`
  plays `success.wav` once when the page activates (moved out of
  `CreatePowerPageContent` which the plan suggested but which would have
  fired the cue at wizard init, far before the user reached the page).
  `CurStepChanged` honours the user's Power Mode choice — picking Standard
  downgrades `TierFromJson` to RECOMMENDED before the model-size dispatch.
- `[Files]` entries for `power_banner.bmp` + `success.wav` with `dontcopy`
  flags so they ride in the installer but only materialise to the wizard
  temp dir on demand
- Pascal `(* ... *)` comments used for the GPU-name helper docstring; PascalScript would otherwise close the comment early on the first
  `{tmp}` reference (per `feedback_pascalscript_restrictions.md`)
- `mciSendStringW@winmm.dll stdcall` external for Win32 audio playback

`def43ba` — feat(in-app): Power Mode tray tooltip + settings badge
- `voice.py update_tray()` — prepends ` — Power Mode` to the `Koda` prefix
  when `system_check_tier == "POWER"` and mode is auto-detect/power. Every
  state tooltip ("Loading...", "Ready", "Recording...") gets the suffix
- `settings_gui.py _build_performance_section()` — Atlas Navy `#1c5fb8`
  `Power Mode: Active` badge under the status line (tk.Label so the bg
  paints directly; ttk styles can't carry raw bg) plus a CUDA explainer
  in the dimmed text colour

`7e57ae5` — feat(voice): one-time tray balloon when a new GPU appears
- `voice.py _maybe_show_power_unlock_balloon` — runs once at end of
  `run_setup`, fires balloon when flag unset + auto-detect + tier was not
  POWER before refresh + tier is POWER now. Stamps flag + tier so it never
  re-fires
- `config.py DEFAULT_CONFIG` — `power_mode_balloon_shown: False`

`a2d2541` — assets(installer): swap to v3 banner background
- Alex generated v1 → v2 → v3 backgrounds in ChatGPT. Picked v3 over v1
  for cleaner accent placement and less stock-photo-eclipse feel. v2 was
  too minimalist (rejected after generation). Re-saved with C2PA strip,
  regenerated `power_banner.bmp`

`4b3bb39` — feat(installer): redesign Power Mode banner — monumental hero
- This is the v5 design — the one that earned "thats what I am fucking
  talking about !!!!!!!!!!!!!!!!!!!!"
- `installer/build_power_banner.py` — full rewrite of the composition.
  K-mark grows 96px → 170px with three-pass bloom (outer atmospheric haze
  + mid bloom + hot core, fused with 48px gaussian) so it reads as
  genuinely energised. Horizontal Atlas Navy light beam emanates from the
  K-mark across the banner. Right column gets a tracked-out 'UNLOCKED'
  kicker label above an auto-fit 'POWER MODE' headline in white at the
  largest size that fits (~48pt for the canonical canvas), with a green
  operational dot + 'Hardware acceleration active' status row below
- `installer/koda.iss CreatePowerPageContent` simplified — drops the now-
  redundant 'Near-instant transcription' BodyLabel since the banner says
  it. Keeps the dim machine-specific 'Detected: <GPU name>' label

PR #39 body covers the test plan: install on POWER tier → celebration page
+ success.wav + correct config writes; no-banner / no-badge / no-tooltip-
suffix on non-POWER tiers.

### C. Phase 4 — Backward-compat + extensions (PR #40, branch `feat/hardware-tier-system-phase-4`, 6 commits)

`129a373` — feat(config): backward-compat first-launch detection-without-overwrite
- `config.py load_config` — when existing config lacks `system_check_tier`,
  runs classify(), stamps tier without overwriting user values. Customised
  values flip mode to "custom" so re-detection leaves them alone
- `+4 TestConfigMigration tests` — covers customised-flips-to-custom,
  matching-flips-to-auto-detect, already-stamped-skips-migration, and
  classify-failure-falls-back-to-RECOMMENDED. 432→448 tests on master,
  448→452 on this branch

`cc33b57` — feat(voice,installer): re-detect tier on startup, fix balloon interaction
- Three coupled changes — splitting them would leave broken interim states
- `voice.py _refresh_tier_on_startup` — runs in `main()` after
  `load_config`. Auto-detect users get tier silently re-classified every
  launch
- `voice.py _maybe_show_power_unlock_balloon` — refactored to take an
  `old_tier` snapshot argument and trust the `power_mode_balloon_shown`
  flag as the single source of truth. The Phase 3 implementation tried
  to detect transitions by re-running classify() and comparing, which
  broke the moment Task 22's silent refresh started stamping POWER ahead
  of it. Snapshot pattern fixes this
- `installer/koda.iss BuildTierAwareConfigJson` — gains `BalloonShown` param,
  emits `power_mode_balloon_shown` field. `'true'` whenever final tier
  is POWER (the celebration page already fired). `'false'` otherwise

`2fe6b7b` — fix(voice): mirror large-v3-turbo on our own GH release, download on-demand
- POWER tier was writing `model_size=large-v3-turbo` to config but the
  model never reached the user. faster-whisper's default name resolution
  maps `large-v3-turbo` to `Systran/faster-whisper-large-v3-turbo` which
  does not exist on HF as of 2026-05-02 (the working community port lives
  at `mobiuslabsgmbh/faster-whisper-large-v3-turbo`, but we shouldn't
  depend on a community namespace at runtime for a paid product)
- `model_downloader.py` (NEW) — module mirrors models on `Moonhawk80/koda`'s
  `whisper-models-v1` release. `download_and_extract()` streams the
  tarball to a temp file, extracts to a staging dir, then atomically
  renames to `CONFIG_DIR/models/<size>/`. Progress callback fires per-MB
- `voice.py load_whisper_model._load` — three-tier search:
  (1) PyInstaller-bundled snapshot, (2) previously-mirrored snapshot in
  `CONFIG_DIR/models/<size>/`, (3) download from our GH mirror with tray
  progress UI throttled to 5% increments. Falls through to faster-whisper's
  HF resolution for non-mirrored sizes (small / base / tiny)
- `.gitignore` — `models/` excluded so dev runs don't accidentally commit
  the 1.4 GB snapshot dir
- Mirror release URL:
  `https://github.com/Moonhawk80/koda/releases/download/whisper-models-v1/whisper-large-v3-turbo.tar.gz`
  (1.49 GB, SHA256 in release manifest)

`6d6adf6` — fix(updater): filter to semver-shaped tags, skip pre-releases
- The auto-updater was hitting `/releases/latest`, which returns the most-
  recently-created non-pre-release. The moment we shipped `whisper-models-v1`,
  that became "latest" — auto-updater saw `whisper-models-v1` as a version,
  fell back to its non-Version string-equality path, decided that wasn't
  equal to `4.4.0-beta1`, and notified every running Koda that an update
  was available
- New approach: list ALL releases (`/releases?per_page=30`), skip drafts +
  pre-releases, filter to tags matching `^v?\d+\.\d+\.\d+(?:[-.][...])?$`,
  sort by Version() and pick the highest. Falls back to (None, None) on
  any failure
- Smoke-tested against the live API: returns `4.3.1`, correctly skipping
  the prerelease `whisper-models-v1`

`647d797` — fix(power-mode): write compute_type, bundle cuDNN, sync drift on startup
- Three coupled root causes for "POWER tier ran at 5 sec/word + crashed
  the moment we forced float16"
- (1) `installer/koda.iss BuildTierAwareConfigJson` never wrote
  `compute_type`. Python loader's default ('int8') took effect → device=cpu
  even on POWER tier. Now writes 'float16' for POWER, 'int8' for
  MINIMUM/RECOMMENDED
- (2) `build_exe.py` PyInstaller bundle shipped ctranslate2.dll and
  libiomp5md.dll but NOT cudnn64_9.dll. PyInstaller's static analyzer
  doesn't see cuDNN because ctranslate2 LoadLibrary's it by name at
  CUDA-init time. Adding `--collect-binaries=ctranslate2` pulls the
  whole package's binaries
- (3) `voice.py _refresh_tier_on_startup` only synced model_size /
  cpu_threads / process_priority — and only when tier changed. So existing
  installs whose config was written before fix (1) would never self-
  correct. Now syncs all four tier-bound fields (compute_type included)
  every startup when on auto-detect
- Diagnostic flow: dev-venv ctranslate2 reports CUDA 1 device + supports
  float16 + WhisperModel(device='cuda') loads cleanly. So CUDA hardware
  works. Yet bundled exe crashed on the same call. `find` on the running
  `_MEI` extraction confirmed cudnn64_9.dll absent from bundle but present
  in venv/Lib/site-packages/ctranslate2/

### D. Mirror infrastructure (one-time)

- Created GitHub release `whisper-models-v1` on `Moonhawk80/koda`, marked
  pre-release after the updater bug surfaced
- Tarred local cached `mobiuslabsgmbh--faster-whisper-large-v3-turbo`
  snapshot (1.4 GB) and uploaded as the only asset
- Asset URL pinned in `model_downloader.py:MIRRORED_MODELS`. Adding new
  models is one new dict entry + a tarball upload to the same release

### E. Banner design iterations (the longer arc — 5 versions)

The banner alone consumed maybe 90 minutes and produced the most important
durable feedback of the session.

- **v1** — first ChatGPT generation, horizon-arc accent, K-mark composited
  centre. Alex called it off but couldn't articulate what was wrong
- **v2** — sharpened prompt that banned the horizon arc. Result was too
  empty, "just a dark banner with a glow in the corner"
- **v3** — third generation, picked over v1 for cleaner accent + subtle
  dot texture. Composited cleanly. Briefly the working version
- **v3+typography** — added "POWER MODE" headline + green dot to the
  banner via PIL. Alex said "no excitement just words on the banner"
- **v4** — bigger K-mark + heavier bloom + accent stripe. Headline got
  smaller from autofit constraint. Alex said "do better please!"
- **v5** — went big in one shot: 170px K-mark, three-pass bloom,
  horizontal light beam, "UNLOCKED" tracked-out kicker label, "POWER MODE"
  white at 48pt, dropped the stat line. **"thats what I am fucking talking
  about !!!!!!!!!!!!!!!!!!!!"** Shipped

### F. Live-validation discoveries

- Alex deleted `%APPDATA%\Koda\config.json` and ran the new installer
- Walked the wizard, saw the celebration page with the v5 banner,
  success.wav played, picked Continue with Power Mode
- Ctrl+Space test → 70-second transcription for a 12-word sentence,
  pasted into the wrong window because Alex switched contexts during the
  wait
- Debug.log diagnosis revealed `device=cpu, compute=int8` — not GPU. Root
  cause traced through to bugs A and B (above)
- Live config edit `compute_type: float16` → next launch crashed with
  PyInstaller bootloader error → cuDNN bundling bug discovered
- Reverted to int8 to keep Koda usable overnight; fix for the rebuild
  scheduled for tomorrow's first install

## Decisions Made

### Mirror Whisper models on our own GH release, not HF at runtime

Started with faster-whisper's default `WhisperModel("large-v3-turbo")` which
hits HF's name resolution. That maps to `Systran/faster-whisper-large-v3-turbo`,
which doesn't exist. The community port at `mobiuslabsgmbh/...` is where the
weights actually live but we shouldn't depend on a community namespace at
runtime for a paid product. Locked: mirror models on `Moonhawk80/koda`'s
`whisper-models-v1` GH release. We control the URL, can pin versions, and
never depend on third-party hosts at runtime. ~1.5 GB asset hosted free under
GitHub's release storage limits. Single point of trust for code auditors.

Considered hosting on S3 / Cloudflare R2 — rejected for ongoing cost without
meaningful added benefit. GH Release storage is free, has CDN, and is already
where we host installer binaries.

### Banner v5 — dropped variant sheets, ship the boldest swing

Through v3 + v4 iterations I was generating 3-variant comparison sheets and
asking Alex to pick between A/B/C. Slow. The push-harder-on-design rule made
explicit (see Memory Updates) that this approach averages down to "safe."
v5 was a single bold version, no variants, and it landed first try. Pattern
captured: when uncertain, variant sheets help with direction; when polishing,
just ship the bolder swing and let the user dial back.

### Compute_type belongs in config writes for every tier, not just POWER

The original Pascal `BuildTierAwareConfigJson` omitted `compute_type` entirely
because `int8` was the universal default. POWER tier was supposed to be the
exception. By writing the field for every tier (including the int8 cases),
the config self-documents the intent and `_refresh_tier_on_startup` has
something concrete to compare against. Field appears in every fresh config
now, not just POWER.

### Updater filters by semver pattern, not GitHub's "latest" endpoint

GitHub's `/releases/latest` returns the most-recently-created non-pre-release.
The moment we shipped a non-Koda-version release (`whisper-models-v1` for
model assets), that became "latest" — every running Koda saw an update
notification. Pre-release flag fixes the immediate symptom (after cache
settles) but is a band-aid. Real fix: list ALL releases, filter to tags
matching `^v?\d+\.\d+\.\d+(?:[-.][...])?$`, skip drafts + pre-releases,
sort by Version() and pick the highest. Future asset releases, dev tags,
documentation releases — all silently ignored.

### Skipped the pre-push gate tonight

CLAUDE.md gate rule (sessions 43+): before every push, verify Skill Forge
currency → forge-deslop → forge-review → push. Skill Forge had uncommitted
local changes blocking the currency check (a separate repo at
`~/Projects/skillforge`, modified hook + 5 untracked test files). Alex was
exhausted near midnight and explicitly authorized "commit push and handover"
without the gate. Both PRs (#39, #40) are open as drafts-of-intent — gate
runs tomorrow before either can merge.

### Whisper supply-chain is fine; Koda's moat is the product layer

Mid-session Alex realised "we are using someone elses build for our Koda"
and got alarmed. Talked through it: Whisper is open-sourced by OpenAI under
MIT (irrevocable for already-released versions, explicitly designed for
commercial reuse). Every serious dictation app uses it — Wispr Flow, Otter,
Apple's transcription features. CTranslate2 + faster-whisper are both MIT.
Systran's converted weights are derivative MIT. Building our own would cost
$10-100M + 5+ ML researchers + 1-2 years; OpenAI made Whisper specifically
so we don't have to. Koda's moat is the product layer (push-to-talk hotkey,
Windows integration, prompt-assist, Atlas Navy, install flow, brand) — not
the model. Future paid release should add a polite "Powered by Whisper
(OpenAI, MIT)" attribution in an About dialog.

### Banner size capped at 600×300

Inno's modern wizard surface is roughly 497×312 actual area; our 600×300
banner is sized for the inside-banner-region. Earlier iterations of the
plan implied wider banners but those would clip on narrow wizard themes.
600×300 is the locked working canvas.

## User Feedback & Corrections

### "thats what I am fucking talking about !!!!!!!!!!!!!!!!!!!!"

The v5 banner reaction. Eleven exclamation points. Captured as the canonical
visual benchmark for any future user-facing celebration moment. The pattern
that earned it: monumental K-mark + three-pass bloom + light beam + tracked-
out kicker label + 48pt headline in white + green operational dot. Earlier
versions had the same elements at smaller scale and got "bored" / "lackluster"
reactions. The fix wasn't different elements — it was bigger commitment to
the same elements.

### "at one point you told me you can push harder on design I need you to do this all the time this will be a full deliverable app across the world if this works we need to better"

The single most decision-shaping message of the session. Saved as
`feedback_push_harder_on_design.md` mid-session. Default for any user-facing
visual artifact is now top-shelf product-design quality — Apple keynote,
Steam achievement unlock, Tesla welcome screen tier. Don't deliver "fine"
and wait to be told to do better.

### "do better please!"

Reaction to v4 banner. The shorter version of the rule above. Confirmed that
incremental iterations wasn't going to get us to "good enough" — needed a
bold leap. v5 was the response.

### "well the speed sucks took like 3 minutes and it pasted in a different session we made wayyyyyy slower this is trash"

The trigger for the cuDNN diagnosis. Tonally raw but factually correct —
70 seconds for 12 words on POWER tier was catastrophic. Two real bugs underneath:
(a) compute_type wasn't being written, (b) cuDNN wasn't bundled. Both fixed.

### "we are using someone elses build for our Koda!!!!!!"

Triggered the Whisper supply-chain conversation. Captured as
`project_whisper_dependency_framing.md` so the next time the question comes
up (paid-tier prep, customer-facing copy, legal review) we have a tight
framing ready.

### "preview is where????"

After I rendered images inline with the Read tool, Alex didn't see them in
his UI. Lesson: when generating preview artifacts for visual review, always
also surface the file path so Alex can open the file directly.

### "we need to find a stoping point I am exhausted and its almost midnight"

Capped the session. Authorized the commit + push without the pre-push gate
because we'd hit the natural Phase 3+4 ship moment and gating perfection
would push past midnight on a Saturday.

### "commit push and handover"

Final session-end authorization. Translated as: push both branches, open both
PRs, run forge-handover, write everything down for tomorrow. Skipped the gate
deliberately.

### "i was in the other session when it pasted I got tired of waiting"

Confirmed the paste-into-wrong-window behaviour was a symptom of the 70-
second transcription wait, not a separate bug. Fix the speed, the symptom
goes away. No separate work item needed.

## Dead Ends Explored

### Variant-sheet banner iteration approach

Through v3 + v4 I was generating 3-variant comparison sheets (A: glow only,
B: kicker text, C: combined) and asking Alex to pick. Each sheet took a few
minutes, generated mediocre options because the "safe middle" averaged
down, and ate iterations. Rejected pattern: variant sheets are for
direction-finding (when the design space is ambiguous), not polish (when
the user knows what they want). v5 was a single bold version and landed.
Captured in `feedback_push_harder_on_design.md`.

### "POWER MODE UNLOCKED" as the headline string

v3 attempt rendered "POWER MODE UNLOCKED" as a single 30pt headline that
fit the available width. Alex liked the wording but the banner felt
deflated because the headline was small. Refactored: "UNLOCKED" became a
small tracked-out kicker label above the headline, "POWER MODE" stayed as
the big bold focal point. Better hierarchy, both elements survived.

### Pre-release flag as the updater fix

First instinct after the auto-updater bug: mark `whisper-models-v1` as a
pre-release so `/releases/latest` excludes it. Did that, but the API caches
for 5+ minutes — couldn't see immediate effect. Pivoted to the proper fix
(list-all-and-filter-by-semver) which works regardless of cache state and
handles all future non-version releases (model assets, dev tags, etc).
Pre-release flag is still set on the model release, just not load-bearing.

### Pre-downloading large-v3-turbo in the Inno installer

Considered for option 1 of the model-availability fix: download the 1.5 GB
model from the installer post-step instead of from Koda runtime. Rejected
because Inno doesn't have a clean HTTP download primitive (idp.iss is
third-party with its own bugs; Pascal `WinHttpRequest` is gnarly), HF cache
path has a per-user hash that changes (faster-whisper resolves
automatically; reimplementing in Pascal is brittle), McAfee just choked on
a 535 MB local file copy and a 1.5 GB download from huggingface.co would be
a much bigger AV target, installer would visibly hang for 1-3 min, and
non-POWER users would waste bandwidth. Going with download-on-demand from
Koda runtime instead — Python handles all the edge cases.

### Reframing POWER tier away from large-v3-turbo

Briefly considered: drop large-v3-turbo entirely, use `small` + CUDA +
float16 for POWER tier (just GPU acceleration, no model size penalty).
Easier to ship — no download needed. Rejected because the celebration page
explicitly promises "Larger, more accurate model" — backing off the model
size would mean the wizard copy lies. Instead built the proper download
flow + cuDNN bundling so POWER tier actually delivers what it promises.

### Hosting model mirror on S3 / Cloudflare R2

Considered as alternatives to GH Release storage. Rejected — ongoing cost
without meaningful added benefit. GH Release is free, has CDN, gives us
control over the URL, and is already where we host installer binaries.

### Bumping Koda version to make `/releases/latest` work

If we'd shipped a 4.5.0 release on the same day as `whisper-models-v1`, it
would've become "latest" again. Considered as a band-aid. Rejected because
it doesn't fix the underlying class of bug (next non-version release would
break it again). Filtering by semver pattern is the proper fix.

## Skills Activated This Session

| Skill | Ask | Outcome | Report path |
|---|---|---|---|
| forge-resume | session-start orientation | Read session 52 handover, confirmed master clean post PR-#37+#38 merges, warmed cache with hardware tier system source files (system_check.py, koda.iss, the spec doc, key memory entries). Recommended Phase 3 Power Mode as next priority. | n/a |
| brainstorming | (implicit — banner design exploration) | 5 banner iterations, settled on v5 monumental composition. The structured exploration informed the v5 design even though we didn't run the canonical brainstorming flow | n/a |
| writing-plans | (implicit — session 52 plan was already written) | Followed the existing plan tasks 15-24; extended scope mid-session to handle the model mirror + cuDNN bug | n/a |
| forge-handover | session wrap-up (this) | This handover file + .claude/next.md sync + 4 new memory entries + commit + push | (this file) |

No forge-deslop, forge-review, forge-clean, forge-test, forge-migrate,
forge-organize, forge-secrets, forge-checklist, update-config this session.
**Pre-push gate intentionally skipped** — Skill Forge currency check blocked
by uncommitted local changes in the other repo; Alex authorized push without
the gate at session end.

## Memory Updates

Memory directory: `~/.claude/projects/C--Users-alexi-Projects-koda/memory/`
(canonical path — note that session 52 wrote 4 new memory entries to a
different path `C--Users-alexi/memory/` due to a path-construction bug;
those entries are still there and accessible but not in the canonical
index. Migration deferred — not auto-fixed this session.)

**CREATED this session:**

- `feedback_push_harder_on_design.md` — already saved mid-session, before
  Alex picked option 1 at the handover plan gate. Default for any user-facing
  visual artifact is top-shelf product-design quality. Don't deliver "fine"
  and wait to be told to do better. Anchor to Apple keynote / Steam
  achievement / Tesla welcome bar before generating, not after.

- `project_power_mode_implementation.md` — captures the v5 banner design
  recipe + cuDNN bundling lesson + model mirror architecture. Future
  Power-Mode-related work should reference this for the canonical
  composition + the supply chain (mobiuslabsgmbh source → our GH mirror →
  Koda runtime download).

- `feedback_pyinstaller_hidden_dlls.md` — PyInstaller's static analyzer
  doesn't see DLLs that packages LoadLibrary at runtime (cuDNN, CUDA
  runtime libs, anything with delayed loading). Use
  `--collect-binaries=<package>` to pull the whole package's DLLs. Came up
  with ctranslate2/cudnn64_9.dll; will recur with any GPU/ML package.

- `reference_koda_model_mirror.md` — Moonhawk80/koda `whisper-models-v1`
  release URL + procedure for adding new model mirrors (download HF
  snapshot, tar with `tar -czf`, `gh release upload`, add a row to
  MIRRORED_MODELS in model_downloader.py).

- `project_whisper_dependency_framing.md` — Why Koda uses OpenAI's Whisper
  rather than building our own model (impossible at our scale; everyone
  uses Whisper; MIT licence is irrevocable; Koda's moat is the product
  layer not the model). Useful framing for paid-release prep, About dialog
  attribution copy, customer-facing FAQ, legal review.

**UPDATED:** `MEMORY.md` index — appended 4 new entries (the
push-harder-on-design entry was already added mid-session).

No deletions. Existing memory entries (40+) all current and load-bearing.

## Waiting On

- **Validate POWER tier works on home PC with the cuDNN-bundled rebuild**
  — installer rebuilt at end of session (commit `647d797`). Tomorrow:
  delete config.json, install fresh, hit Ctrl+Space, confirm sub-second
  to few-second transcription on RTX 4060.
- **Skill Forge cleanup** — `~/Projects/skillforge` has uncommitted local
  changes (`forge-harness/hooks/h1-pre-push-gate.sh` + 5 untracked
  `forge-harness/tests/` files). Resolve before running pre-push gate.
- **forge-deslop + forge-review on PRs #39 + #40** — gate still owed before
  either can merge.
- **Re-target PR #40 base** from `feat/hardware-tier-system-phase-3` to
  `master` after PR #39 merges (per session 52's stacked-PR pattern).
- **Live mic test of master overlay v2** (carried from sessions 47/51,
  still pending v4.4.0-beta1 tag).
- **`koda.iss` friction-free upgrade hardening** — `CloseApplications`,
  `RestartApplications`, `AppMutex` (carried from session 51, surfaced
  again this session when Alex hit the "Setup was not able to automatically
  close all applications" prompt).
- **Decide `dev_test_overlay.py` fate** — still untracked at project root,
  decision deferred from session 47.
- **Bundle Hubot Sans + JetBrains Mono in installer** (carried from session
  47).
- **Coworker re-test of v4.3.1 mic-hotplug + music-bleed** (carried from
  session 41).
- **Mirror additional Whisper models** (medium, large-v3) on
  `whisper-models-v1` release — only large-v3-turbo mirrored so far.
  Optional, on-demand based on user need.
- **Migrate session 52's stranded memory entries** from
  `C--Users-alexi/memory/` to canonical
  `C--Users-alexi-Projects-koda/memory/`. Optional cleanup, not load-bearing.

## Next Session Priorities

Per `.claude/next.md` after this session's check-offs:

1. **Validate POWER tier on home PC with the cuDNN-bundled installer.**
   `dist/KodaSetup-4.4.0-beta1.exe` rebuilt at session end. Delete
   `%APPDATA%\Koda\config.json`, install, walk wizard, hit Ctrl+Space,
   confirm sub-second to few-second transcription. If broken: investigate
   before merging PRs.
2. **Resolve Skill Forge uncommitted changes** — commit, stash, or
   complete that work in `~/Projects/skillforge`. Blocks the pre-push
   gate.
3. **Run forge-deslop on each branch's diff** (PR #39 first, then #40
   after re-target). Apply BLOCKING/HIGH findings.
4. **Run forge-review on each branch's diff.** Resolve BLOCKING /
   NEEDS-FIX findings.
5. **Merge PR #39** to master.
6. **Re-target PR #40 base to master**, then merge.
7. **Tag v4.4.0-beta1** after live mic test passes (still owed from
   session 51).
8. **`koda.iss` friction-free upgrades** — 4-line `[Setup]` change +
   `AppMutex`. Trivial. Surfaced again this session.
9. **Decide `dev_test_overlay.py` fate** — commit / delete / gitignore.
10. **Phase 16 licensing** — blocks paywall wrap.

## Files Changed

### Commits merged this session

#### `master` (1 commit, pushed)

- `1ea6e4a` docs: refresh CLAUDE.md hardware note + check off completed items in next.md
  - `CLAUDE.md` (+2 lines, -2 lines)
  - `.claude/next.md` (+1 line, -1 line)

#### PR #39 (`feat/hardware-tier-system-phase-3` → master, 6 commits, pushed)

- `828751a` assets(installer): AI-generated Atlas Navy background for Power Mode banner
  - `installer/power_banner_bg.png` (NEW, 1.05 MB → re-saved via PIL strip)
- `4b24871` feat(installer): build script composites K-mark on AI background
  - `installer/build_power_banner.py` (NEW, ~60 lines initial — replaced in `4b3bb39`)
  - `installer/power_banner.bmp` (NEW)
- `42d460b` feat(installer): Power Mode celebration wizard page
  - `installer/koda.iss` (+133 lines: PowerPage block, helper procs,
    mciSendString external, [Files] entries with dontcopy, CurStepChanged
    radio handling, CurPageChanged for sound)
- `def43ba` feat(in-app): Power Mode tray tooltip + settings badge
  - `voice.py` (+5 lines: update_tray prefix substitution)
  - `settings_gui.py` (+19 lines: badge in Performance section)
- `7e57ae5` feat(voice): one-time tray balloon when a new GPU appears
  - `voice.py` (+30 lines: `_maybe_show_power_unlock_balloon` + run_setup wiring)
  - `config.py` (+3 lines: power_mode_balloon_shown default)
- `a2d2541` assets(installer): swap to v3 banner background, strip C2PA manifest
  - `installer/power_banner_bg.png` (REPLACE, v3 with C2PA stripped)
  - `installer/power_banner.bmp` (REGEN)
- `4b3bb39` feat(installer): redesign Power Mode banner — monumental hero composition
  - `installer/build_power_banner.py` (full rewrite, ~155 lines: v5 design)
  - `installer/power_banner.bmp` (REGEN)
  - `installer/koda.iss` (-21 +0 lines: simplified `CreatePowerPageContent`)

#### PR #40 (`feat/hardware-tier-system-phase-4` → phase-3, 6 commits, pushed)

- `129a373` feat(config): backward-compat first-launch detection-without-overwrite
  - `config.py` (+30 lines: load_config migration block)
  - `test_features.py` (+89 lines: TestConfigMigration × 4)
- `cc33b57` feat(voice,installer): re-detect tier on startup, fix balloon interaction
  - `voice.py` (+62, -16 lines)
  - `installer/koda.iss` (+21, -5 lines: BalloonShown param + CurStepChanged update)
- `2fe6b7b` fix(voice): mirror large-v3-turbo on our own GH release, download on-demand
  - `model_downloader.py` (NEW, ~110 lines)
  - `voice.py` (+40 lines: three-tier search in `_load`)
  - `.gitignore` (+1 line: models/)
- `6d6adf6` fix(updater): filter to semver-shaped tags
  - `updater.py` (+37, -14 lines)
- `4b3bb39` (already in Phase 3 — see above)
- `647d797` fix(power-mode): write compute_type, bundle cuDNN, sync drift on startup
  - `build_exe.py` (+8 lines: `--collect-binaries=ctranslate2`)
  - `installer/koda.iss` (+15, -5 lines: ComputeType param + writeback)
  - `voice.py` (+11, -5 lines: refresh syncs compute_type unconditionally)

### Not committed (intentional carries)

- `config.json` — modified pre-session, intentionally NOT committed per
  session 45 rule (carried local state)
- `dev_test_overlay.py` — untracked dev tool, decision deferred from session
  47. Still pending.

### Memory files (outside git)

5 files in `~/.claude/projects/C--Users-alexi-Projects-koda/memory/`:
- `feedback_push_harder_on_design.md` (NEW — saved mid-session)
- `project_power_mode_implementation.md` (NEW — this handover)
- `feedback_pyinstaller_hidden_dlls.md` (NEW — this handover)
- `reference_koda_model_mirror.md` (NEW — this handover)
- `project_whisper_dependency_framing.md` (NEW — this handover)
- `MEMORY.md` (UPDATE — 5 new index entries appended)

### External infrastructure

- GitHub release `whisper-models-v1` created on `Moonhawk80/koda`
  (pre-release flag set). One asset: `whisper-large-v3-turbo.tar.gz`
  (1.49 GB, SHA256 `f84bf13c9df0106d4fc25d3fb0846ba4ed642b3382d8f4e6c3fc72c206513350`)

### Open PRs

- **#39** — Power Mode celebration + in-app indicators (Phase 3 of 4)
- **#40** — backward-compat + turbo model mirror + Power Mode crash fix
  (Phase 4 of 4) — base is phase-3, must re-target to master before merge

## Key Reminders

- **Push harder on design — every iteration, by default.** New durable rule
  this session. Top-shelf product-design quality on any user-facing visual.
  Anchor to Apple / Steam / Tesla bar, not "internal tool" bar. Don't ship
  variant sheets when polishing — ship the bolder swing and let Alex dial
  back. See `feedback_push_harder_on_design.md`.
- **PyInstaller misses LoadLibrary'd DLLs.** When bundling any package
  with GPU/CUDA/dynamic-load behaviour, default to `--collect-binaries=<pkg>`
  rather than relying on static analysis. cudnn64_9.dll case captured in
  `feedback_pyinstaller_hidden_dlls.md`.
- **POWER tier defaults must include `compute_type: float16`.** Omitting the
  field means the loader's int8 default takes effect → device=cpu → POWER
  tier silently runs on CPU. Installer writes it for every tier now;
  `_refresh_tier_on_startup` syncs it on every auto-detect launch.
- **Whisper models live on our GH release, not HF at runtime.** Mirror
  procedure in `reference_koda_model_mirror.md`. Adding a model = download
  HF snapshot + tar + `gh release upload` + add row to MIRRORED_MODELS in
  model_downloader.py.
- **Banner v5 is the canonical celebration moment.** Recipe in
  `project_power_mode_implementation.md`. Future celebrations (Phase 16
  paywall? new feature unlock?) should follow the same composition
  language: monumental scale + bloom + light beam + tracked-out kicker
  + bold headline + green operational dot.
- **Whisper supply-chain is fine.** If the question of "but the model is
  someone else's" comes up again, the answer is in
  `project_whisper_dependency_framing.md`. Add About-dialog attribution
  before paid release as a polite norm.
- **Updater filters by semver pattern.** Future non-version releases
  (model assets, dev tags, docs) won't trigger update notifications. If
  Koda's tag scheme ever changes, update the regex in `updater.py:_VERSION_TAG_RE`.
- **GitHub `/releases/latest` cache is ~5 minutes.** Surfaced when we
  marked `whisper-models-v1` as a pre-release and the API kept returning it.
  If you need an immediate "latest" change, expect to wait or use the
  list-and-filter pattern.
- **Pre-push gate is mandatory** for code pushes (per global CLAUDE.md
  rule from session 43). This session **intentionally skipped it** —
  Skill Forge currency check was blocked + Alex authorized at midnight.
  Tomorrow's first task before merge: resolve Skill Forge + run gate on
  both PRs.
- **`config.json` is tracked but treated as local runtime state.** Don't
  commit it (session 45 rule, still active).
- **PRs stack via base re-targeting.** PR #40 is currently based on
  `feat/hardware-tier-system-phase-3`; re-target to `master` BEFORE PR
  #39 merges so neither orphans (per session 52 lesson).
- **PascalScript `{tmp}` inside Pascal `{ ... }` comments closes the
  comment early.** Use `(* ... *)` for any helper-function docstring that
  references the wizard temp dir. Captured in
  `feedback_pascalscript_restrictions.md` (session 52, still load-bearing).
- **Memory dual-paths bug from session 52 still exists.** New entries
  this session land in the canonical
  `C--Users-alexi-Projects-koda/memory/`. Session 52's 4 entries are
  stranded at `C--Users-alexi/memory/`. Migration optional, not blocking.
- **Local-only is a brand promise, not a flag.** Do not propose cloud
  backends for transcription. Even opt-in cloud breaks the pitch (session
  52 lock, still active).

## Migration Status

n/a — koda is a desktop app, no DB migrations.

## Test Status

- **Master after both phase branches' commits**: 452/452 tests passing.
- **Phase 4 contribution**: +4 new tests (TestConfigMigration × 4).
- **Phase 3 contribution**: 0 new tests (UI / asset / Pascal — covered by
  manual validation in PR test plans).
- **Total**: 448 (start of session) → 452 (end). +4 tests.
- **Suite**: `venv/Scripts/python -m pytest test_features.py -q`.
- **Live functional validation**: POWER tier transcription end-to-end NOT
  YET CONFIRMED working (cuDNN-bundled rebuild ready in `dist/`, tomorrow's
  first task).

## Resume pointer

```
cd C:/Users/alexi/Projects/koda
# then in Claude Code:
/forge-resume
```
