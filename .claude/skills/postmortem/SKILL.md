---
name: postmortem
description: >-
  The reproduce-before-fix diagnosis discipline, for any hard/opaque bug — especially a generic
  symptom like "Failed to fetch" that could have several causes. Use when debugging a live failure,
  when a fix "should have worked" but didn't, or when the user says "why is this happening",
  "it's still broken", "diagnose this".
---

# Skill: postmortem (diagnosis discipline)

A generic client-side error message is a *diagnostic failure*, not a symptom. Follow this, earned from
the six-day "Failed to fetch" saga (four unrelated causes behind one message):

1. **Reproduce before fixing.** No fix is allowed until you have a failing reproduction. State the
   hypothesis, the evidence for it, and the test that would DISPROVE it. (Two fixes shipped on
   theories that were only partly right — cold start and a stale service worker were both real and
   both NOT the cause.)
2. **Verify from the user's vantage point.** A browser check needs a browser, a CLEAN profile, and the
   canonical URL. `curl` bypasses CORS and service workers; `?cb=` bypasses the CDN. A check that
   passes there while the user fails is worthless — trust the user's report over the green tool.
3. **Fix the boundary before the bug.** If an error crosses a boundary and loses its cause (a 500 with
   no CORS header, a client that logs nothing), restore the cause FIRST — then the real bug is visible.
4. **One symptom may hide several causes.** Keep looking after the first real bug is found; fixing one
   changed nothing visible because three more remained.
5. **Label every claim** confirmed / observed / inferred. Don't assert a root cause you only suspect
   (the memory-exhaustion 502 is still "observed, not confirmed" — Render logs were never read).
6. **Close the loop:** once fixed, run the **add-eval-case** skill so the failure can never return.

For a structured, read-only pass on a specific surface, invoke the relevant verifier subagent
(contract / deployment / error-surface).
