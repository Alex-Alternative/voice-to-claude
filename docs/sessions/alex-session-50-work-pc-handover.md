---
session: 50
date: 2026-04-30
scope: koda
resumes-from: alex-session-49-work-pc-handover.md
continues-work-from: null
projects-touched: [koda]
skills-activated: [forge-resume, forge-handover]
---

# Work-PC Session 50 Handover — 2026-04-30

Tackled the coworker installer rebuild that session 49 parked. Built
`KodaSetup-4.4.0-beta1.exe` from `feat/overlay-rounded-buttons` (Atlas
Navy overlay confirmed visually good — Alex tested at home). Path
delivered for Google Drive upload + share with coworker. Mac-version
request raised mid-session and reframed as a separate multi-day
project (5 hard blockers documented). Three new items appended to
`.claude/next.md` and one item struck off (the parked coworker
perf-fix).

## Branch
`feat/overlay-rounded-buttons` at `6694a7b` (1 commit ahead of session
49's `0502f65`, pushed). Working tree dirty: `M config.json` (local
runtime tuning, carried since session 48 — ignore per session 45 rule).

## What Was Built This Session

### KodaSetup-4.4.0-beta1.exe rebuild
- Output: `C:\Users\alex\Projects\koda\dist\KodaSetup-4.4.0-beta1.exe`
- Size: 560 MB
- Built: 2026-04-30 ~20:16 local
- Source: `feat/overlay-rounded-buttons` HEAD (includes Atlas Navy
  overlay v3 — `13f35d5` rounded buttons, `63b4e04` Atlas Navy palette
  + tooltips + Polish rename + paired fonts + accent spine, `b4eff40`
  settings_gui matching treatment)
- Build command: `venv/Scripts/python installer/build_installer.py`
  after deleting the stale `dist/Koda.exe` from Apr 24
- Build time: ~95 sec for Inno Setup compile (PyInstaller stage was
  also part of the run — total ~3-5 min)

### `.claude/next.md` updates (commit `6694a7b`, pushed)
1. Coworker perf issue marked `[x]` — installer rebuild is the fix
   delivery; perf-tuning levers logged as "if it persists post-upgrade"
2. Mac version section added — 5 hard blockers + realistic effort
3. Speed gap vs paid Whisper section added — boss's tool is "lightning
   fast no matter the length"; likely Groq whisper-large-v3 on LPU
4. Docs drift section added — `docs/user-guide.html` stale since Apr
   20, NOT bundled in installer so coworker unaffected, but needs
   refresh before official v4.4.0-beta1 tag

## Decisions Made

### Build from `feat/overlay-rounded-buttons`, not `origin/master`
- I flagged the choice mid-session: current branch has Atlas Navy
  overlay that session 49's notes called "WIP — visually untested,
  MUST eyeball before merge." Pushing untested overlay to a coworker
  is a real "his first impression of v4.4.0 is broken UI" risk.
- Alex resolved it: "the overlay is good / I tested that at home
  already." Atlas Navy is visually approved.
- Outcome: built from `feat/overlay-rounded-buttons` HEAD as planned.
  No rebuild from master needed.

### Mac version — separate multi-day project, not same-day delivery
- Alex asked for a Mac version "as well, forget the slowdown" after
  picking option 1 (Windows installer + Mac-as-next-md-item).
- I held the position that a Mac build is not a same-day rebuild from
  this Windows PC. Reasoning was already in chat, now durable in
  memory at `project_mac_port_blockers.md`:
  1. PyInstaller does NOT cross-compile.
  2. 8 modules import Win32-locked code.
  3. `koda.iss` is Inno Setup (Windows-only).
  4. Apple Developer account ($99/yr) needed for clean distribution.
  5. macOS permission ceremony (Accessibility / Input Monitoring / Mic).
- Alex picked option 1 (Windows now, Mac as separate `.claude/next.md`
  item) — confirmed with bare digit "1." Mac is now a tracked item,
  not active work.

### Skip the perf-tuning config patch entirely
- Session 49's plan had two paths: (a) ship a `config.json` patch with
  3 keys (process_priority / cpu_threads / model_size), or (b) rebuild
  the installer. Plan favored (a) because it was faster.
- Alex chose (b) by saying "forget the slowdown" — meaning the new
  installer IS the upgrade, and any post-upgrade perf complaints can
  be triaged with the levers later.
- Rationale: the coworker is on v4.3.1 and significantly behind on
  features anyway (auto-polish, Atlas Navy, voice-confirm, 2-slot Q&A
  all post-date his install). A version bump is more valuable than a
  pinpoint perf patch.

### Memory entry: build_installer.py output line is unreliable
- Caught when the build's "Output:" line said `KodaSetup-4.3.1.exe`
  (the OLD installer from Apr 20) while Inno Setup's own
  `Resulting Setup program filename is:` line correctly named the new
  `KodaSetup-4.4.0-beta1.exe`.
- Root cause: the loop at `installer/build_installer.py:~80` iterates
  `os.listdir(DIST_DIR)` and breaks on the first `KodaSetup*.exe`
  match — alphabetical order, not mtime. With both installers in
  `dist/`, it picked the wrong one.
- Documented in `project_build_installer_output_bug.md`. Fix not
  done this session — a future session can patch the loop (sort by
  mtime, or parse Inno's output) when the installer flow gets touched
  again.

## User Feedback & Corrections

### "we need to do a mac version as well forget the slowdown"
Alex's verbatim. Reframed: drop the perf-fix angle, ship the new
installer for Windows, and add Mac as separate work. I pushed back on
"Mac as same-day deliverable" with hard blockers; Alex accepted the
reframing without further pushback.

### "the overlay is good / I tested that at home already"
Alex's verbatim — answered my flagged question about whether to build
from current branch (Atlas Navy WIP) vs `origin/master` (stable). Atlas
Navy is visually approved on the home PC; no further eyeball needed
before shipping to coworker.

### "come on I wanna go home"
Alex's verbatim — soft urgency signal mid-build. Translated to: don't
rebuild from master "just to be safe," just trust his home-PC eyeball
and ship what's built.

### "also to note on next or whatever koda is way slower than the paid
version of whisper I have seen my boss use it and its lightning fast no
matter the lenght of the speech he tells it"
Captured in `.claude/next.md` as a roadmap item, not a same-session
fix. My read: boss's tool is almost certainly cloud-GPU Whisper (most
likely Groq's whisper-large-v3 on LPU — that's the actual speed
benchmark — sub-second for minute-long clips). Koda's local-CPU
faster-whisper `small` on Alex's Intel UHD is the bottleneck. Levers
listed for later: tiny-model option, optional cloud-API backend,
streaming transcription.

### "ok push commit and handover skill"
Direct authorization to commit + push + handover. Pre-push gate
skipped per koda CLAUDE.md ("when Alex explicitly authorizes a push,
proceed without running the gate; the authorization is the override").
Also docs-only push (just `.claude/next.md`) is exempt regardless.

## Dead Ends Explored

### Building a Mac version from this Windows PC, this session
- **Considered:** kicking off a Mac build alongside the Windows
  installer rebuild.
- **Rejected because:** PyInstaller does not cross-compile (hard
  toolchain constraint), `koda.iss` is Inno Setup (Windows-only),
  and 8 modules use Win32 APIs that need real macOS equivalents.
  No subset of "build a Mac version today" survives those constraints.
- **Where discussed:** mid-session after Alex's "we need to do a mac
  version as well." Reframed as separate multi-day project; full
  rationale captured in `project_mac_port_blockers.md`.

### Shipping a `config.json` patch instead of a fresh installer
- **Considered:** session 49's plan A was a 3-key patch
  (`process_priority`, `cpu_threads`, `model_size`) dropped next to
  the existing exe. Faster delivery, no reinstall.
- **Rejected because:** Alex's "forget the slowdown" + the coworker
  being on v4.3.1 (well behind on features, not just perf) made a
  full version upgrade the better answer.
- **Where discussed:** start of session, before the "forget the
  slowdown" pivot.

### Building from `origin/master` instead of the current feature branch
- **Considered:** rebuilding from `origin/master` would be the
  known-stable choice for a coworker; feature branch had untested
  Atlas Navy.
- **Rejected because:** Alex confirmed Atlas Navy was eyeballed at
  home and is visually good. No risk to send to coworker.
- **Where discussed:** mid-build, when I flagged the question.
  Resolved with "the overlay is good / I tested that at home already."

## Skills Activated This Session

### forge-resume
- **Ask:** "well I guess forge resume first?" (after I started reading
  files for the installer rebuild without running it)
- **Outcome:** session-start summary loaded — handover 49 + memory
  index + git state + next.md. No commits since handover, working
  tree dirty only on `M config.json` (carried). Recommended next
  action was triage-Qs-then-ship.
- **Report path:** N/A (read-only, output to chat)

### forge-handover
- **Ask:** "ok push commit and handover skill"
- **Outcome:** this handover doc + 2 new memory files +
  `MEMORY.md` index updated. Committing the handover after the
  Gate 2 preview.
- **Report path:** `docs/sessions/alex-session-50-work-pc-handover.md`

## Memory Updates

`~/.claude/projects/C--Users-alex-Projects-koda/memory/`:

- **`project_mac_port_blockers.md`** NEW — type: project. The 5 hard
  blockers preventing a Mac build from this Windows PC + realistic
  effort estimate. Saves future sessions from re-deriving the same
  list when Alex re-asks.
- **`project_build_installer_output_bug.md`** NEW — type: project.
  `installer/build_installer.py:~80` reports the alphabetically-first
  `KodaSetup*.exe` in `dist/` as its "Output:" line, not the freshly
  built one. Trust Inno Setup's own filename line instead.

`MEMORY.md` index: 2 lines appended under "Project — open bugs &
quirks" + new "Project — port / platform" section header for the Mac
blockers entry.

## Waiting On

Same as session 49 minus the coworker perf fix (resolved by installer
re-share):

- Coworker re-test of v4.4.0-beta1 once he installs from Google Drive
  (carries forward the original v4.3.1 mic-hotplug + music-bleed
  questions — possibly resolved by upgrade)
- Live mic test of master overlay (Atlas Navy)
- PR #35 review/merge (silent fixes)
- PR #36 review/merge (Atlas Navy)
- v4.4.0-beta1 official tag (after live test + installer port + docs
  refresh)
- Inno installer v2 setup pickers port

New this session:
- Mac version as a separate multi-day project (Mac dev box + Apple Dev
  account decisions pending)
- `docs/user-guide.html` + `docs/user-guide.md` refresh before
  official v4.4.0-beta1 tag

## Next Session Priorities

1. **Hear back from coworker on the v4.4.0-beta1 install.** Did the
   slowdown resolve on upgrade, or does it persist? If persist, work
   the diagnostic order from `feedback_koda_perf_levers.md`
   (`process_priority` → `cpu_threads` → `model_size`) — ship a
   `config.json` patch.
2. **Decide on the Mac port.** Two real questions for Alex:
   (a) does he have access to a Mac dev box, (b) is he willing to
   spin up an Apple Developer account ($99/yr) for clean distribution?
   Both are budget/access decisions that gate the project. Don't start
   coding until both are answered.
3. **Refresh `docs/user-guide.html` + `.md`** before tagging
   v4.4.0-beta1 officially. Both stale since Apr 20 — predate
   auto-polish, Atlas Navy, voice-confirm, 2-slot Q&A, Polish
   rename, settings GUI redesign.
4. **Live-eyeball Atlas Navy via Ctrl+F9** in the REAL prompt-assist
   mic flow on the work PC (still pending from session 47 next.md).
5. **PR #35 + PR #36 review/merge.** v4.4.0-beta1 tag after both land.
6. **Address the Whisper speed gap** — explore Groq cloud backend
   option as a paid tier later (not on the v4.4.0 critical path).

## Files Changed

### Source code
None — no .py / .iss / .json source files changed this session. Only
the build artifact and the next.md checklist were touched.

### Build artifacts (not git-tracked)
- `dist/KodaSetup-4.4.0-beta1.exe` (rebuilt — 560 MB, replaces the
  Apr 24 build)
- `dist/Koda.exe` deleted by `build_installer.py` cleanup at end of
  build (script removes the intermediate exe — only the installer is
  meant to ship)

### Branch / state
- `.claude/next.md` (commit `6694a7b`, pushed): coworker perf item
  struck off; Mac version + speed gap + docs drift sections appended

### This handover
- `docs/sessions/alex-session-50-work-pc-handover.md` (this file)
- `~/.claude/projects/C--Users-alex-Projects-koda/memory/project_mac_port_blockers.md` (new)
- `~/.claude/projects/C--Users-alex-Projects-koda/memory/project_build_installer_output_bug.md` (new)
- `~/.claude/projects/C--Users-alex-Projects-koda/memory/MEMORY.md` (2 index lines + new section header)

## Key Reminders

- **The new installer at `C:\Users\alex\Projects\koda\dist\KodaSetup-4.4.0-beta1.exe`
  is what ships to the coworker via Google Drive.** 560 MB, built
  2026-04-30 ~20:16. Coworker uninstalls v4.3.1 first, then runs
  this. Wizard pages walk him through mic + activation + quality +
  formula choices.
- **`build_installer.py` lies about its output filename.** Always
  cross-check against `ls -la dist/` and Inno Setup's own
  "Resulting Setup program filename" line. See
  `project_build_installer_output_bug.md`.
- **Atlas Navy overlay is visually approved.** Alex eyeballed it at
  home — no further live-eyeball gate before merging PR #36.
  (Work-PC live-eyeball still scheduled but is no longer a blocker
  for shipping the coworker installer.)
- **Mac port is a multi-day project, not a build flag.** When the
  topic returns, surface `project_mac_port_blockers.md` immediately.
  Do NOT promise same-day delivery from this Windows PC.
- **Whisper speed gap is roadmap territory.** The boss's "lightning
  fast" tool is almost certainly Groq whisper-large-v3 on cloud LPU.
  Local-CPU faster-whisper `small` cannot compete on speed. Don't
  pretend a config tweak fixes this — it's an architecture choice
  (cloud backend, optional).
- All session 49 reminders carry: pre-push gate is opt-in for koda
  (solo project), Anthony review N/A here (solo personal), commit means
  push on this project, Alex reads in chat — paste content inline or
  give full absolute path.

## Migration Status
N/A — no migrations this project.

## Test Status
No code changes this session, no test runs needed. Test status carries
from session 49: PR #35 432/432, PR #36 431/431, both pre-push-gate
clean.

## Resume pointer

```
cd C:/Users/alex/Projects/koda
# then in Claude Code:
/forge-resume
```
