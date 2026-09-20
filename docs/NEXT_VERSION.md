# NEXT_VERSION.md — what to build next, what to defer

Distilled from `../kinetiq v4/docs/NEXT_VERSION_PRINCIPLES.md` (which draws on *The Builder's Gita*
Parts II–III and Boris Cherny's 10 Claude Code principles). Keep the prototype **simple** — that is a
constraint, not an afterthought. Target: ~10 users.

## The thesis
We built at the **top** of the eval-maturity ladder (Hamel Husain: Vibes → Quantitative → Automated) —
an automated, CI-gated harness — while never standing on the **bottom** rung: one real person, once,
in front of the camera. The next version climbs *down* to that rung, then adds just enough
observability and a few verifier agents to make the climb back up trustworthy.

## Do now (simple, high-value)
1. **G-LIVE** — one human, clean/Incognito browser, real reps, the counter moves. **No code.** The one
   rung never climbed; it may itself surface the next thing to fix.
2. **Observability** — done/underway in v4: `verify_deploy.py` (browser-faithful), `/health` version
   SHA, client logs status+body. Remaining: wire `KINETIQ_VERSION` to the git SHA in `render.yaml`;
   an automated post-deploy check in CI.
3. **The three verifier subagents** (this repo's `.claude/agents/`, run in-repo) — read-only, would
   have caught the box bug on day one. The only multi-agent work that passes the book's decision matrix.
4. **A couple of skills** (this repo's `.claude/skills/`) — `deploy-verify`, `add-eval-case`,
   `postmortem`.
5. **Then GATE G-REAL** — the first real gym session → the first real accuracy number.

## Defer (do NOT build yet — keeps it simple)
- **Agent teams / hierarchical or debate orchestration** — experimental; overkill at 10 users.
- **The fine-tuned Stage-4 form model** — gated by G-REAL; no labelled real data to train on yet.
- **The 11 new exercises** — harder for vision than the first three (`EXERCISE_LIBRARY.md` §2); three
  is the right scope.
- **Pose bake-off, Memory agent, Orchestrator agent, RAG, multi-pose** — later, data-driven, or
  irrelevant to a prototype.

## The through-line
Climb down to Vibes; add only the observability and the handful of read-only verifier subagents that
make the climb back up trustworthy. Everything else waits for a real number. More machinery is not
more progress.
