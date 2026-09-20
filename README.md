# Kinetiq v5 — the new prototype root

This folder is the **root of the next Kinetiq prototype**. The code lives here; the Claude Code
operating layer (`.claude/`) sits in the same root, so the verifier subagents and skills run
**in-repo** against the code beside them — no copying. The layer encodes how we build and, above all,
how we catch the four deploy failures we already lived through (the "Failed to fetch" saga).

## Intended layout (build to these paths — the agents/skills already reference them)
```
kinetiq v5/
  CLAUDE.md                      ← governance: invariants, earned rules, how agents/skills fit
  .claude/
    settings.json                ← minimal permissions for read/verify/test commands
    agents/                      ← read-only verifiers (no Edit/Write): contract-, deployment-, error-surface-
    skills/                      ← deploy-verify · add-eval-case · postmortem
  docs/                          ← CONTEXT · ERRORS_AND_LESSONS · NEXT_VERSION · AGENTS
  evals/gate0/                   ← eval-validated detector, scorers, golden set, harness, prototype_api (+ verify_deploy.py)
  backend/app/core/config.py     ← single-source constants
  exercises/                     ← exercise contracts
  frontend/                      ← the camera PWA
```
`evals/`, `backend/`, `exercises/`, `frontend/` are built as the prototype comes up. **Carry the
detector + eval harness over from `../kinetiq v4/`** rather than rebuilding them — see below.

## Start here (first Claude Code session, in this folder)
1. Read `CLAUDE.md`, then `docs/CONTEXT.md`, `docs/ERRORS_AND_LESSONS.md`, `docs/NEXT_VERSION.md`.
2. **Carry over the proven engine** from `../kinetiq v4/`: `evals/gate0/` (detector, scorers, golden,
   harness, `prototype_api/` incl. `verify_deploy.py`), `backend/app/core/config.py`, `exercises/`.
   These are the one eval-validated, 315-test-green part of the project; rebuilding the detector
   re-opens every failure class in `docs/ERRORS_AND_LESSONS.md`. Prove the carry-over green
   (`python -m unittest discover -s evals/gate0 -p "test_*.py"` + `aggregate.py --mode full`).
3. Build the new app shell (`frontend/`, and any API changes) on top, respecting the invariants
   (`CLAUDE.md` §2) and **GATE G-REAL** (no threshold tuning / learned model / new exercise until a
   real gym session).
4. After any deploy, run the **deploy-verify** skill / **deployment-verifier** subagent.

## The agents (run in-repo, read-only)
- **deployment-verifier** — "verify from the browser's vantage point" (the curl trap).
- **contract-verifier** — "test the REAL client payload, not a fixture" (the `box` bug).
- **error-surface-auditor** — "an error must never lose its cause at a boundary" (the CORS-less 500).

They have `Read`/`Grep`/`Glob`/`Bash` only — **no `Edit`/`Write`**. They prove and surface; the main
agent fixes, under your review. Each exists because of a specific dated failure in
`docs/ERRORS_AND_LESSONS.md`.

## The one rule behind all of it
Nothing is "built" unless its files exist and an acceptance check ran green. Adding agents or code is
not progress; catching the next real bug — and finally getting one real person through a real set — is.
