---
session: 49
date: 2026-04-29
scope: koda
resumes-from: alex-session-48-work-pc-handover.md
continues-work-from: null
projects-touched: [koda]
skills-activated: [forge-handover]
---

# Work-PC Session 49 Handover — 2026-04-29

Triage-only session. Alex reported a coworker is experiencing significant
PC slowdown after installing Koda. Diagnosed probable causes and ranked
fixes; Alex parked the work for tomorrow because he hasn't yet sent the
coworker a new install file. No code changes this session.

## Branch
`feat/overlay-rounded-buttons` at `8b6c920` (matches origin). Working
tree dirty: `M config.json` (local runtime tuning, carried since
session 48 — ignore per session 45 rule).

## What Was Built This Session

Nothing. This was a triage discussion only.

## Decisions Made

### Park the coworker perf fix until tomorrow

Alex's verbatim: "i havent sent him the new install file dont worry we
will tackle tomorrow ❯ commit and push and run handover I am going
home"

**Reasoning:** the coworker is still running the OLD installer
(presumed v4.3.1 per `feedback_overdue.md` memory — "Coworker re-test
of v4.3.1 mic-hotplug + music-bleed needs installer re-share first").
A fix needs either (a) a config.json patch shipped to the coworker's
existing install, or (b) a fresh installer with safer defaults baked
in. Alex hasn't shipped either yet, so any code/config change today
wouldn't reach the coworker anyway. Resume tomorrow with the diagnosis
intact.

## User Feedback & Corrections

### "Koda is slowing my coworkers pc by alot"

Alex's framing — actionable problem report, not a status question. The
diagnosis I gave focused on **probable** causes (since I don't have the
coworker's machine specs or symptoms in front of me) rather than a
definitive answer.

## Dead Ends Explored

None this session — only one diagnostic path was explored (config-
based fix via reduced CPU/priority/model footprint). Alex parked the
work before any path was rejected.

## Skills Activated This Session

- **forge-handover** (running now)
  - Ask: "commit and push and run handover I am going home"
  - Outcome: this handover + next.md append + 1 memory entry.
  - Report path: N/A.

## Memory Updates

`~/.claude/projects/C--Users-alex-Projects-koda/memory/`:

- **`feedback_koda_perf_levers.md`** NEW — diagnostic order for "Koda
  slowing host PC" complaints. Captures the ranking
  (`process_priority` first → `cpu_threads` → `model_size`) so future
  sessions don't re-derive the same triage.

`MEMORY.md` index appended with the new entry.

## Waiting On

Same as session 48 plus:
- **Coworker perf fix** — needs config.json patch sent OR fresh
  installer with safer defaults built and shipped. Tomorrow's work.

Carried items:
- Live mic test of master overlay
- PR #35 review/merge (silent fixes)
- PR #36 review/merge (Atlas Navy)
- v4.4.0-beta1 tag
- Inno installer v2 setup pickers port
- Coworker re-test of v4.3.1 (carried from session 41 — possibly
  resolved by the perf fix above; verify after)

## Next Session Priorities

1. **Diagnose + fix coworker's Koda slowdown.** Likely fix order
   (per `feedback_koda_perf_levers.md`):
   1. `process_priority` `"above_normal"` → `"normal"` — biggest
      single lever per `config.py:33`'s own comment ("higher values
      let Windows preempt other normal-priority processes"). No
      transcription-quality hit.
   2. `cpu_threads` `4` → `2` — frees 2 cores for the rest of the
      coworker's system. Slower transcription but coworker is testing,
      not benchmarking.
   3. `model_size` `small` → `base` (or `tiny`) — `small` is ~500MB
      resident, `base` ~150MB, `tiny` ~75MB. Accuracy hit but big
      RAM/CPU savings.
   Triage Qs to ask Alex first: which version is coworker on (v4.3.1
   assumed); slowdown when idle / only during recording / always;
   coworker's specs (CPU/RAM).
   Easiest delivery path = ship a `config.json` patch (3 keys) with
   instructions to drop in next to the exe. No reinstall, just
   restart Koda.

2. Live-eyeball Atlas Navy via Ctrl+F9 (Koda still running on the
   `feat/overlay-rounded-buttons` branch from session 48 — may need
   re-launch if it crashed over the past 2 days).
3. Settings GUI second-pass review.
4. PR #35 + PR #36 review/merge.
5. v4.4.0-beta1 tag after live test + installer port.
6. (Roadmap items unchanged from session 48.)

## Files Changed

### Source code
None.

### Branch / state
None — branch + working tree unchanged from session 48 close.

### This handover
- `docs/sessions/alex-session-49-work-pc-handover.md` (new)
- `.claude/next.md` (1 line appended — coworker perf fix item)
- `~/.claude/projects/C--Users-alex-Projects-koda/memory/feedback_koda_perf_levers.md` (new)
- `~/.claude/projects/C--Users-alex-Projects-koda/memory/MEMORY.md` (1 index line appended)

## Key Reminders

- **Coworker is still on v4.3.1.** Any fix needs to be shipped — a
  fresh install or a config.json patch. Source-only changes don't
  reach his machine.
- **`process_priority: "above_normal"` is the prime suspect** for
  any "Koda slowing my PC" report. The comment in `config.py:33`
  literally says it preempts normal-priority work. On a less-powerful
  machine running normal user apps (browser, Slack, etc.), Koda will
  starve them of CPU.
- **Fix path: config.json patch first**, fresh install second. Patch
  is faster to ship and doesn't require uninstalling.
- All session 48 reminders still apply (Atlas Navy locked, "Polish"
  not "Refine", K-mark dot uses operational colors, avoid Tailwind
  defaults, pre-push gate is opt-in for koda, Git Bash mangles
  slash-prefix flags).

## Migration Status
N/A.

## Test Status
No code changes. Test status carries from session 48: PR #35
432/432, PR #36 431/431, both pre-push-gate clean.

## Resume pointer

```
cd C:/Users/alex/Projects/koda
# then in Claude Code:
/forge-resume
```
