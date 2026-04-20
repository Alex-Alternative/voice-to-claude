# Alex Session 36 Handover — 2026-04-17

## Branch
`docs/phase-planning-post-stress` — 1 commit ahead of master. PR #15 OPEN at Moonhawk80/koda#15. Working tree clean.

Note: PR #14 (`feat/github-actions-release-build`) from session 35 is also still OPEN — both PRs are independent and can be merged in any order.

---

## What Was Built This Session

### 1. Phase Planning Doc (PR #15)

**File:** `docs/phase-planning-post-stress.md` (new, 242 lines)

Documentation-only change. Maps the post-stress-testing roadmap as discrete phases the user can pick / reorder / cut. No code changes.

**Phases covered:**
- **Phase 14** — Close out stress testing (Block 4/5 live tests, Excel actions, fresh installer test, merge PR #14)
- **Phase 15** — Privacy & Release infrastructure (make repo private, set up `Moonhawk80/koda-releases` public repo, redirect CI/updater)
- **Phase 16** — License system (key validation, activation, offline grace period, tier gating hooks). Flagged as the biggest single phase, 2–3 sessions.
- **Phase 17** — Tier definition & feature gating (proposed Free / Personal $29 / Pro $59 strawman with feature matrix)
- **Phase 18** — Payment integration (Lemon Squeezy)
- **Phase 19** — Landing page (kodaspeak.com — recommended GitHub Pages + plain HTML)
- **Phase 20** — Private beta (5–10 testers, free Pro keys, focused feedback channel)
- **Phase 21** — Public launch (HN Show HN, Reddit, Lobsters, X — explicitly NOT Product Hunt per permanent DO NOT)
- **Phase 22** — Post-launch iteration
- **Speculative future phases** (no order, no commitment) — macOS port, team tier, cloud sync (opt-in), voice profile training, meeting mode, API/CLI, mobile companion, bundled local LLM for Pro

**3 open decisions called out** that need answers before Phase 16 starts:
1. Subscription vs one-time purchase
2. Online-only vs offline-capable activation
3. 1, 2, or 3 tiers

---

## Decisions Made

### Phase planning doc as a PR (not inline, not memory)
**Why:** User said "I won't be able to work on anything here at work — let's do a PR or whatever that I can pull up at home." A PR is the natural artifact: reviewable at home, redirectable, and version-controlled.

### Phase planning chosen over license scaffold or distribution playbook
**Why:** Three options were offered (phase plan, license scaffold, distribution playbook). Phase planning was picked first because it frames everything else — license scaffold and distribution choices both depend on tier/pricing decisions that the phase plan surfaces explicitly.

### Strawman tier table included even though user hadn't approved tiers
**Why:** Easier to redirect a concrete proposal than respond to "what tiers do you want?" Doc explicitly labels it as a strawman and lists open questions.

### Handover for session 36 written even though the session was short
**Why:** User explicitly asked for handover. PR work is captured + open decisions are queued for the next session.

---

## User Feedback & Corrections

- **"I won't be able to work on anything here at work, let's do a PR or whatever I can pull up at home"** — drove the entire session shape: produce a PR-able artifact rather than do live testing or interactive work. Useful pattern: when user is at work PC and live testing isn't possible, default to documentation/planning PRs they can review at home.
- **"yes" to phase planning doc as a PR** — confirmed direction quickly with no redirect. No corrections during execution.

No mid-session corrections, redirects, or rework.

---

## Waiting On

### Decisions needed from user (block Phase 16):
- **Pricing model** — subscription vs. one-time purchase
- **Activation model** — online-only vs. offline-capable
- **Tier count** — 1, 2, or 3 tiers (and whether the strawman Free / Personal $29 / Pro $59 split is roughly right)

### User actions needed:
- **Read PR #15** at home, redirect / approve phase plan
- **Merge PR #14** — GitHub Actions release workflow (no testing needed, just merge)
- **Make repo private** — GitHub UI, still not done
- **Block 4 live tests** (Tests 15–18: correction, correction in terminal, readback, readback selected) — still not run from session 35
- **Block 5 edge cases** — silent dictation, long dictation, background noise, "we should undo" false positive
- **Excel actions live test** — Ctrl+F9 in Excel
- **Coworker installer share** — needs new URL after repo goes private (Google Drive/OneDrive)
- **Fresh-machine installer wizard test**

---

## Next Session Priorities

1. **Discuss the 3 open decisions** (pricing, activation, tier count) — needed before any Phase 16 code work
2. **Merge PRs #14 + #15** assuming both look good at home
3. **Make repo private** + decide Google Drive vs koda-releases for installer hosting
4. **Block 4 live tests** (Tests 15–18) — Koda was running from source at end of session 35; still likely running
5. **Block 5 edge cases**
6. **Excel actions live test**
7. After stress testing wraps: kick off Phase 15 (privacy + release infra)

---

## Files Changed This Session

| File | Status | Description |
|---|---|---|
| `docs/phase-planning-post-stress.md` | Created | Phase 14–22 roadmap + speculative future phases + open decisions |
| `docs/sessions/alex-session-36-handover.md` | Created | This document |

No code files touched. No tests added or modified.

---

## Key Reminders

- **Two PRs open simultaneously** — #14 (CI workflow, session 35) and #15 (phase plan, session 36). Independent. Either can merge first.
- **Phase plan is a strawman** — tier matrix, prices, and phase boundaries are all up for redirect. Don't treat the doc as final until user confirms.
- **Open decisions block Phase 16 code work** — do NOT start writing `license.py` or feature gates until pricing/activation/tier decisions are made.
- **No Product Hunt** — permanent DO NOT in STATUS.md, repeated in phase plan Phase 21.
- **Domain is `kodaspeak.com`** (already chosen per STATUS.md, used in Phase 19).
- **No activation system exists yet** — Koda has zero DRM. Selling commercially without it = source can be copied. This is what Phase 16 fixes.
- **Repo still public** — same as session 35. User intends to make private but hasn't.
- **339 tests passing** — no test changes this session.
- **PRs only for Moonhawk80** — no direct pushes to master.
- **Block 4/5 live tests carry over** — third consecutive session they're flagged as pending. Should be done in person at the work PC, in front of Koda running from source.

---

## Migration Status

None this session.

---

## Test Status

| Suite | Count | Status |
|---|---|---|
| `test_features.py` | 339 | ✅ All passing (unchanged) |
| **Total** | **339** | **✅** |

No test changes this session — documentation-only PR.
