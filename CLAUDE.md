# CLAUDE.md — Kinetiq v5 (new prototype root)

> **This folder is the root of the next Kinetiq prototype.** The code lives here (built at
> `evals/gate0/…`, `frontend/`, `backend/`, `exercises/` — the same layout as v4), and the Claude
> Code operating layer — the governing rules, the read-only verifier subagents, and the skills — is
> the `.claude/` folder in this same root, so the agents run **in-repo** against the code beside
> them. It captures how we build and, especially, how we *catch the failures we already lived
> through*. The prior repo `../kinetiq v4/` is the reference the code is carried from and the source
> of the deeper docs; it is not where work happens now.
> Last updated: 2026-09-20

---

## 0. Read this first (fresh agent)

1. This file — the invariants, the errors we earned rules from, and how the agents/skills fit.
2. `docs/CONTEXT.md` — what Kinetiq is and the v1→v4 arc, in one page.
3. `docs/ERRORS_AND_LESSONS.md` — the four deploy failures and the rules each one earned. **Every
   subagent in `.claude/agents/` exists because of a specific failure here.**
4. `docs/NEXT_VERSION.md` — what to build next and what to defer (keep the prototype simple).
5. `docs/AGENTS.md` — the agent roster: three built, four designed-not-built.

Source of truth for anything deeper is `../kinetiq v4/docs/` (POSTMORTEM_FAILED_TO_FETCH.md,
NEXT_VERSION_PRINCIPLES.md, SESSION_LEARNINGS_2026-09.md, ROADMAP.md, EVAL_STRATEGY.md). The `docs/`
here distil those; they do not replace them.

## 1. What Kinetiq is (one paragraph)

An AI virtual physical trainer: a phone camera counts reps and flags exercise form, **entirely
on-device**. Pose runs in the browser (MediaPipe/BlazePose); only keypoints cross the network to a
small FastAPI detector; the PWA renders live rep count, form flags, and coaching cues. Three
exercises are vision-live (squat, push-up, lunge); eleven more are defined but gated. The engine is
a **compound of deterministic specialists** (subject-lock → rep-validity → rep counter → form rules
→ safety veto), fronted by an **eval harness** that decides "is it actually better?" with a number.

## 2. Invariants (non-negotiable — do not re-litigate)

- **Privacy: pixels never leave the device.** Pose is on-device; only keypoint frames are sent. No
  frame, image, or video buffer crosses the network — not to the API, not to any model.
- **One detector, N consumers.** `run_detector` is defined once; the live API, the offline harness,
  and the effectiveness report all call it. Detection logic changes in one place, never duplicated.
- **Deterministic safety veto.** A learned/advisory layer may add nuance but can never clear a hard
  safety flag or invent a rep the validity gate rejected.
- **Config is the single source of truth.** Thresholds live in the exercise contracts or
  `config.py`, imported, never restated as inline literals.
- **GATE G-REAL.** No detection-threshold tuning, no learned form model, no new vision-live exercise
  until one real gym session produces a real effectiveness report. Everything green today is on
  synthetic data.
- **Anti-phantom rule.** Nothing is called "built" in any doc, commit, or agent report unless its
  files exist AND an acceptance check ran green. If it wasn't verified, say "not verified."

## 3. The rules this project earned the hard way (the reason the agents exist)

From `docs/ERRORS_AND_LESSONS.md` (full detail there). These are binding working agreements:

1. **An error must never lose its cause at a boundary.** A server error must carry CORS headers; a
   client must log the status and body it received. → *error-surface-auditor.*
2. **Test the real client's payload, not a fixture.** Every client/server boundary needs one test
   that builds the request exactly as the live client does. → *contract-verifier.*
3. **A validator must require everything its consumer indexes.** → *contract-verifier.*
4. **Verify from the user's vantage point.** A browser check needs a browser, a clean profile, and
   the canonical URL — not `curl` and not a cache-buster. → *deployment-verifier.*
5. **Never treat all non-2xx alike; bound every retry queue; disclose anything dropped.**
6. **Reproduce before fixing.** State the hypothesis, the evidence, and the test that would disprove
   it, before any fix. Two fixes shipped on theories that were only partly right. → *postmortem skill.*
7. **Keep looking after the first real bug.** One symptom hid four causes.
8. **Every format claim in a doc needs an executable test.** A stale doc specified a payload that
   crashed the detector for a week.

## 4. How this layer works

- **Subagents (`.claude/agents/`) are read-only verifiers.** They have `Read`, `Grep`, `Glob`, and
  `Bash` — **no `Edit`/`Write`**. That is deliberate: they *surface* problems and *prove* claims;
  they never fix or guess. Fixing is the main agent's job, under human review. This encodes the
  "surface decisions, don't guess" agreement.
- **Skills (`.claude/skills/`) are workflows** the main agent runs: `deploy-verify`, `add-eval-case`,
  `postmortem`.
- **When to reach for a subagent** (Ch 23 decision matrix): independent, read-heavy verification that
  would otherwise be skipped under time pressure. Not for the tightly-coupled fix itself.

## 5. Keep the prototype simple (explicit)

Target: ~10 users. Build the verifiers and observability; **defer** agent teams, the fine-tuned form
model, the 11 new exercises, the pose bake-off, RAG, and any Memory/Orchestrator agent
(`docs/NEXT_VERSION.md`). Three verifier subagents, not a fleet. More machinery is not more progress.

## 6. Repo layout & running the agents (in-repo)

The code lives in this root. Build and keep the same paths the agents and skills already reference:

- `evals/gate0/` — the eval-validated detector (`detector/`, `run_detector`), scorers, golden set,
  the harness (`aggregate.py`), and the detector API (`prototype_api/`, incl. `verify_deploy.py`).
- `frontend/` — the camera PWA. `backend/app/core/config.py` — the single-source constants.
- `exercises/` — the exercise contracts. `.claude/` — this operating layer.

Carry these over from `../kinetiq v4/` rather than rebuilding them: they are the one eval-validated,
315-test-green part of the project, and rebuilding the detector re-opens every failure class in
`docs/ERRORS_AND_LESSONS.md`. Think "new app shell around the same proven engine," not "new engine."

Because `.claude/` sits in this root, the subagents and skills run **in-repo** with no copying: e.g.
"use the deployment-verifier on `https://<api>.onrender.com` with origin `https://<pwa>`", or run the
`deploy-verify` skill. They invoke `evals/gate0/prototype_api/verify_deploy.py` and `aggregate.py`,
which exist here once the engine is carried over — so verify that carry-over is done before relying
on them (anti-phantom rule, §2).
