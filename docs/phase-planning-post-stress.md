# Phase Planning — Post-Stress-Testing Roadmap

> **Created:** 2026-04-16 (Session 36)
> **Context:** Stress testing is ~90% complete (Blocks 1–3 done, Block 4/5 remaining). This doc maps what comes after testing wraps, organized as discrete phases you can pick or reorder. Nothing here is started yet.

---

## Where We Are Today

| Area | State |
|---|---|
| Core app | v4.2.0 shipped as `KodaSetup-4.2.0.exe` |
| Tests | 339 passing (`test_features.py`) |
| Stress testing | Blocks 1–3 PASS; Blocks 4 (correction, readback) & 5 (edge cases) pending live run |
| CI/CD | PR #14 open — GitHub Actions auto-builds installer on version tag push |
| Distribution | Public GitHub Releases (user plans to make repo private) |
| Monetization | **Nothing built.** No license system, no payment, no landing page, no tier gating |
| Domain | `kodaspeak.com` chosen (per STATUS.md) |

---

## Guiding Principles

1. **Ship narrow first.** Sell to one type of user (devs who use LLMs all day) before widening.
2. **Local-first is the moat.** $0 runtime cost, no cloud dependency — keep it that way.
3. **No Product Hunt.** Explicit DO NOT in STATUS.md.
4. **Offline-capable license checks.** DRM must not break when user is on a plane.

---

## Phase 14 — Close Out Stress Testing (1 session, ~2 hours)

Finish what's in flight before starting new work.

**Tasks:**
- Block 4 live test — Tests 15–18 (correction mode, correction in terminal, readback, readback selected)
- Block 5 live test — silent dictation, long dictation, background noise, "we should undo" false positive
- Excel actions live test — Ctrl+F9 in Excel: nav, table, formula mode
- Fresh installer test — install `KodaSetup-4.2.0.exe` on a clean machine, run through wizard
- Merge PR #14 (GitHub Actions workflow)

**Exit criteria:** All 5 blocks green, installer verified on clean machine.

---

## Phase 15 — Privacy & Release Infrastructure (1 session, ~1 hour)

Separate source from distribution before any paid customers exist.

**Tasks:**
- Make `Moonhawk80/koda` private (GitHub Settings → Danger Zone)
- Create public `Moonhawk80/koda-releases` repo (releases only, no source)
- Adjust `.github/workflows/build-release.yml` to upload to `koda-releases` instead of source repo
- Update `updater.py` to point at `koda-releases` for auto-update checks
- Update README install link to point at `koda-releases`
- Cut `v4.3.0` tag to verify end-to-end CI → public release flow

**Exit criteria:** Unauthenticated user can download the installer from `koda-releases`; auto-update still works.

**Open question:** Is a two-repo split overkill vs. just shipping installers via Gumroad/LemonSqueezy download page? Tradeoff is auto-update cost — update checks are trivial against a public repo's releases API, harder against a Gumroad-hosted file.

---

## Phase 16 — License System (2–3 sessions)

The big one. Required before any commercial sale.

**Design decisions needed first (not in this doc):**
- Online activation only, or offline-capable?
- Hardware fingerprint, or account-based?
- Per-device limit (e.g. 2 machines per license)?
- Grace period on license check failure (e.g. 7 days offline allowed)?
- Refund / deactivation flow?

**Tasks:**
- `license.py` module — key validation, activation state, expiry check
- License key format — signed JWT or Ed25519-signed blob with embedded fingerprint
- First-run flow — prompt for key after install, no wizard bypass
- `config.json` stores activation state (encrypted or signed, so users can't hand-edit)
- Tier gating in code — map features to tiers (see Phase 17)
- Grace period logic — allow X days offline before locking
- Tray menu — "Enter License Key…", "About / License Status"
- Settings GUI — license tab showing tier, expiry, machines activated

**Exit criteria:** App refuses to start (or falls back to free tier) without a valid key. Key lookup works offline after first activation.

**Risk:** Easy to over-engineer. Start with an absolute minimum (one-time key check, stored locally, no phone-home) and add sophistication only if piracy becomes a real problem.

---

## Phase 17 — Tier Definition & Feature Gating (1 session)

Needs to land alongside Phase 16 but is separable.

**Proposed tiers (for discussion, not final):**

| Feature | Free | Personal ($29 one-time?) | Pro ($59 one-time?) |
|---|---|---|---|
| Dictation (Ctrl+Space) | ✅ | ✅ | ✅ |
| Command mode (F8) | ✅ | ✅ | ✅ |
| Prompt Assist (F9) | — | ✅ | ✅ |
| Per-app profiles | — | ✅ | ✅ |
| Voice commands (30+) | Limited (10) | ✅ | ✅ |
| Custom vocabulary | — | ✅ | ✅ |
| Readback (F5/F6) | — | ✅ | ✅ |
| Correction (F7) | — | ✅ | ✅ |
| Translation | — | — | ✅ |
| Audio file transcription | — | — | ✅ |
| Plugins | — | — | ✅ |
| Usage stats dashboard | — | ✅ | ✅ |
| Ollama LLM polish | — | — | ✅ |
| Auto-update | ✅ | ✅ | ✅ |
| Email support | — | ✅ | ✅ |

**Open questions:**
- One-time vs. annual? One-time is friendlier for indie buyers; annual builds recurring revenue.
- Free tier too generous? Too stingy?
- Pro tier — is there enough in it to justify 2x Personal? Or make it 1 tier to start?

**Tasks:**
- Decide tier structure (needs conversation, not code)
- Add `tier_check(feature)` helper in `license.py`
- Sprinkle checks at feature entry points (voice.py dictation handler, prompt_assist.py, readback path, etc.)
- Upgrade prompts — when user tries a gated feature, show a dialog with upgrade link

---

## Phase 18 — Payment Integration (1 session)

**Platform choice:** Lemon Squeezy (per STATUS.md) — handles VAT/MoSS, license key delivery, refunds.

**Tasks:**
- Lemon Squeezy account + product setup (Personal / Pro SKUs)
- License keys generated by LS, emailed to buyer on purchase
- LS webhook → static license server OR skip webhook and treat LS-signed keys as authoritative offline
- Test buy flow with a $0 test SKU

**Dependencies:** Phase 16 must define the key format Lemon Squeezy generates.

**Exit criteria:** Can buy a test license from a staging SKU, paste key into Koda, activate, use gated features.

---

## Phase 19 — Landing Page (1 session)

`kodaspeak.com` — simple marketing page.

**Stack options:**
- Carrd — simplest, $19/yr, limits on complex layouts
- GitHub Pages + a plain HTML/CSS template — free, full control, no JS framework needed
- Next.js on Vercel — overkill for a single page but future-proof if a blog/docs section is added later

**Rec:** GitHub Pages + plain HTML to start. Migrate to Next.js if the site grows.

**Must-haves:**
- Hero with 30-sec demo video (screen recording of Ctrl+Space → paste flow)
- Feature list (3–5 bullets max)
- Pricing table (mirror Phase 17)
- Download (free tier) / Buy (paid tiers) CTAs
- FAQ — "does it work offline?" "is my audio sent to the cloud?" "Mac support?"
- Privacy policy + Terms (required by Lemon Squeezy)
- Contact email

**Exit criteria:** kodaspeak.com live, all links work, purchase flow round-trips.

---

## Phase 20 — Private Beta (1–2 weeks elapsed, low code)

Before going public, validate with trusted testers.

**Tasks:**
- Pick 5–10 testers (coworkers, dev Discord contacts, etc.)
- Give them free Pro licenses
- Ask for specific feedback: what broke, what surprised them, what they'd pay
- Dedicated feedback channel (Discord server? shared doc?)
- Fix whatever Priority-0 bugs surface

**Exit criteria:** 3 testers actively using it for a full work week with no blocking bugs.

---

## Phase 21 — Public Launch (1 session + ongoing)

**Launch channels (in order of likely value for dev tools):**
1. **Hacker News — Show HN** — best for dev tools, Tuesday/Wednesday morning
2. **r/productivity, r/accessibility, r/programming** — Reddit
3. **Lobsters** — small but high signal
4. **X/Twitter — dev-focused accounts** — weaker than it was but still a thing
5. **Personal network** — LinkedIn, Discord servers already in

**Explicitly NOT:** Product Hunt (per permanent DO NOT in STATUS.md).

**Launch-day checklist:**
- Landing page load-tested
- Lemon Squeezy working in production mode (not staging)
- First-run onboarding tight (no wizard dead-ends)
- Update channel stable (no auto-update failures)
- A 60-second demo video

**Exit criteria:** First 10 paying customers. Not a vanity metric — it's the proof that the funnel works end-to-end.

---

## Phase 22 — Post-Launch Iteration (ongoing)

After the launch bump, the real work is retention and word-of-mouth.

**Focus areas:**
- Bug reports from real users (faster turnaround than beta)
- Feature requests — rank by how many independent people ask for the same thing
- Churn analysis — people who activated but stopped using: why?
- Documentation — most-asked-questions become docs, then FAQ entries
- A second/third marketing push after 1–2 months (changelog post, HN follow-up with "what I learned")

---

## Speculative Future Phases (no order, not committed)

These are ideas, not a roadmap — here so they're not forgotten.

- **Phase N — macOS port.** Python stack is cross-platform but pystray/tkinter/keyboard hooks need rework. Biggest single expansion of TAM.
- **Phase N — Team tier.** Shared vocabularies, centrally-managed licenses, SSO. Higher ASP than individual.
- **Phase N — Cloud sync (opt-in).** User settings + vocabularies across machines. Must remain optional — offline-first is the moat.
- **Phase N — Voice profile training.** Per-user acoustic adaptation for accents / noisy environments.
- **Phase N — Meeting mode.** Always-on transcription during meetings with speaker diarization. Different product shape; could be spun out.
- **Phase N — API / CLI.** Power users want to script dictation into their own tools.
- **Phase N — iOS / Android companion.** Mobile dictation that syncs to desktop. Large undertaking.
- **Phase N — LLM polish as first-class feature.** Currently Ollama-only and off by default. Could ship a bundled local LLM for Pro tier.

---

## Immediate Next Step

**Phase 14 (close out stress testing)** is the obvious next session. Everything else is blocked on (a) repo going private and (b) decisions about tiers/pricing that haven't been made yet.

Before starting Phase 16 (license system), have a conversation about:
- One-time vs. subscription
- Online-only vs. offline-capable activation
- Number of tiers (1, 2, or 3)

Those three decisions reshape ~2 sessions of work, so make them deliberately.
