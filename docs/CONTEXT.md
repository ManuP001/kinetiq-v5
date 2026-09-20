# CONTEXT.md — Kinetiq, in one page

Distilled orientation for a fresh Claude Code session. Deeper source of truth: `../kinetiq v4/docs/`.

## What it is
An AI virtual physical trainer. A phone camera counts reps and flags exercise form, **on-device**.
Pose runs in the browser (MediaPipe / BlazePose, 33 keypoints); only **keypoints** cross the network
to a small FastAPI "detector"; the PWA renders live rep count, phase, form flags, and a coaching cue.

## The pipeline (compound of deterministic specialists)
```
webcam ─(in browser)→ BlazePose 33 kp ─→ frame {t_ms, pose_model, people:[{track_id, kp, box}]}
   → POST /prototype/assess → subject-lock → rep-validity gate → rep counter → form rules
   → deterministic safety veto → {rep_count, phase, flags, coaching_cue, subject_lock_ok}
```
Everything is graded by an **eval harness** (golden set + regression gate) that answers "is it
actually better?" with a number, not an opinion. Method backbone: *The Builder's Gita* Ch 30
(compound AI) + Ch 39 (eval-driven development).

## The version arc
- **v1 / v2** — designed a deterministic geometry detector + a no-camera UX demo. Real camera rep
  counting was never measured; the one gym trial *was* the test, and it failed (bench counted 6 reps,
  hip-sag flagged on good form). This is why evals exist.
- **v3** — re-architected the detector into the compound-of-specialists above and put the eval harness
  in front of it. Docs-heavy; code lived across sibling repos; a camera PWA ("kinetiq-demo3") was
  described as built but never existed.
- **v4** — the **self-contained monorepo**: eval-validated detector, harness, 14 exercise contracts,
  the FastAPI detector API, and — finally real — the camera PWA, in one repo. Deployed to Render.
  Then six days of "Failed to fetch" debugging (see `ERRORS_AND_LESSONS.md`). Latest addition:
  `verify_deploy.py` + a `/health` version stamp so a deploy can actually be tested.
- **v5 (this repo — the new prototype root)** — the code lives here (the eval-validated engine
  carried over from v4, plus a new app shell), together with the Claude Code operating layer
  (`.claude/`: verifier subagents + skills that encode the build discipline and catch the v4 failure
  classes). The agents run in-repo against the code beside them.

## Current state (honest)
- 3 exercises vision-live (squat, push-up, lunge); 11 more defined, `vision_support: false`, gated.
- ~315 Python tests + a Stage-0 eval gate, all green — **on synthetic/stubbed data.**
- **No real accuracy measurement exists, and no human has completed a real set in front of the camera.**
  Every "success" is scripted. That is the state, stated plainly.

## The invariants (see root CLAUDE.md §2)
Pixels never leave the device · one detector / N consumers · deterministic safety veto · config is
the single source · GATE G-REAL blocks tuning until real data · nothing is "built" without a green
acceptance check.
