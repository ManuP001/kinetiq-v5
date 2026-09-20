---
name: add-eval-case
description: >-
  Turn a real field failure into a permanent golden eval case the day it's found (Builder's Gita
  Ch 39 / Ch 18). Use when a bug is seen in a real session or on a real device, or when the user says
  "add this as an eval", "make sure this never regresses", "capture this failure".
---

# Skill: add-eval-case

Every field bug becomes eval case #N the day it's found — this is how known failures die permanently
(the bench→6-reps and hip-sag cases are #1 and #2). Steps:

1. **Reproduce first.** Capture the exact input that triggers it — for the detector, the real keypoint
   frames (with `box`), not a hand-simplified fixture. If it's a client/boundary bug, capture the real
   request the live client sent.
2. **Add the frozen case** under `evals/gate0/golden/` following `docs/EVAL_HARNESS_STAGE0_SPEC.md` §5:
   `<clip_id>.keypoints.jsonl` (the input) + `<clip_id>.labels.json` (PT/human ground truth). For a
   pure API/contract bug, add the case to `prototype_api/test_pwa_frame_contract.py` instead.
3. **Confirm it FAILS before the fix** (it must actually capture the bug), then that it PASSES after.
   Run `python evals/gate0/aggregate.py --golden evals/gate0/golden --mode full` and the unit tests.
4. **Never change the golden set in the same commit that changes a model or threshold** — the
   yardstick holds still (Ch 39). And never invent a "correct" label; form labels need PT sign-off.
5. Record the case's origin (the bug/session it came from) in its labels or the changelog.
