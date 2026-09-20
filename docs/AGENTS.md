# AGENTS.md — the roster

The full set of agent roles this project's failures imply (`../kinetiq v4/docs/SESSION_LEARNINGS_2026-09.md`
§6). Built **three** now — the read-only verifiers that map to the deploy failures we actually lived
through. The rest are **designed, not built**: add one only when a real need appears, in keeping with
"keep the prototype simple" (`NEXT_VERSION.md`). Schema-now / build-by-phase, same as the exercise
library.

## Built (active — `.claude/agents/`)
| Agent | Catches | Earned from |
|---|---|---|
| **contract-verifier** | the real client payload isn't what the server accepts; validator weaker than consumer | the `box` bug (cause #3) |
| **deployment-verifier** | a deploy that's broken the way only a browser sees (CORS, stale worker, wrong version) | the "curl passed while the phone failed" trap |
| **error-surface-auditor** | an error that loses its cause at a boundary (CORS-less 500; client logs nothing) | the KeyError 500 hidden as "Failed to fetch" |

All three are **read-only** (`Read`, `Grep`, `Glob`, `Bash`; no `Edit`/`Write`) — they prove and
surface; the main agent fixes, under human review. This is the "surface decisions, don't guess"
agreement encoded as tool restriction.

## Designed, not built (add when a real need appears)
| Role | Would guard | Why deferred |
|---|---|---|
| **limits-auditor** | every cap/timeout/quota has a documented behaviour at, and one past, the limit | the 3,600-frame cap (cause #4) is already fixed; revisit if new limits appear |
| **resource-profiler** | memory per session / CPU per request vs the hosting tier | the 512 MB free-tier / OOM class; needs real load, gated with G-REAL |
| **doc-drift-checker** | format claims in CLAUDE.md/docs match code + tests | the stale `frontend/CLAUDE.md`; the anti-phantom rule + a small suite cover it for now |
| **diagnosis-agent** | no fix ships without a failing reproduction first | encoded as the `postmortem` **skill** instead — a workflow, not a standing agent |

## Spawning patterns (when the time comes — Ch 23 / SESSION_LEARNINGS §6)
- **Parallel hypothesis fan-out** for a generic symptom: one agent per hypothesis (CORS, cache, server
  error, cold start, payload), each required to return a reproduction or a disproof.
- **Evidence gate before a fix:** a fixing step starts only after a diagnosis produced a failing repro.
- **Independent post-fix verification:** a fresh verifier subagent, without the fixer's context.

Keep it to the three built agents until a specific failure demands another. Adding agents is not
progress; catching the next real bug is.
