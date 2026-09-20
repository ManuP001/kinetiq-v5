# ERRORS_AND_LESSONS.md — what went wrong, and the rules it earned

The distilled failure record. Full detail: `../kinetiq v4/docs/POSTMORTEM_FAILED_TO_FETCH.md` and
`SESSION_LEARNINGS_2026-09.md`. **Each verifier subagent in `.claude/agents/` exists to catch one of
these classes before it ships again.**

## The headline
One error message — **"Failed to fetch"** — hid **four unrelated causes** over six days (8–14 Sep
2026). Each fix removed one cause and exposed the next, so the screen never changed and every correct
fix looked like it had failed. A browser prints "Failed to fetch" for a missing server, a refused
connection, a CORS rejection, **and a server error whose response lacks CORS headers** — the last is
the trap: the server knew the real error the whole time.

## The four causes
1. **Nothing to call.** `config.js` shipped pointing at `http://localhost:8000`; on a phone that's the
   phone itself, and an HTTPS page calling `http://` is blocked as mixed content. → *deployment-verifier.*
2. **Stale service worker.** Cache-first with a fixed cache name pinned old `app.js`/`config.js`
   forever; every redeploy was invisible to anyone who'd opened the site. → *deployment-verifier*
   (clean-profile / canonical-URL caveat).
3. **The PWA never sent `box` (root cause).** The client built `people:[{track_id, kp}]`; the detector
   indexes `p["box"]` → `KeyError`. `validate_frame_schema` didn't require `box`, so it passed
   validation and crashed deeper; the 500 lost its CORS header → "Failed to fetch". Every test used a
   fixture that already had a `box`. → *contract-verifier* + *error-surface-auditor.*
4. **A set over ~2 min died.** Session cap returned 413; the client retried the same full session
   forever; re-queued frames grew each retry; sessions were never freed (memory). → bounded queue,
   session roll-over, eviction (already fixed in v4); the *limits-auditor* role (designed, see AGENTS.md)
   guards this class.

## The rules earned (binding — root CLAUDE.md §3 restates these)
1. An error must never lose its cause at a boundary (500 keeps CORS; client logs status+body).
2. Test the REAL client's payload, not a fixture.
3. A validator must require everything its consumer indexes.
4. Verify from the user's vantage point — a browser, a clean profile, the canonical URL; not `curl`,
   not a cache-buster. (Curl passed while the phone failed for the entire incident.)
5. Never treat all non-2xx alike; bound every retry queue; disclose anything dropped.
6. Reproduce before fixing — hypothesis, evidence, disproving test — before any change.
7. Keep looking after the first real bug; one symptom hid four causes.
8. Every format claim in a doc needs an executable test (a stale `frontend/CLAUDE.md` specified a
   payload that crashed the detector for a week).

## Still open / honest unknowns
- **No human has completed a real set in front of the camera.** Every success is synthetic.
- Cause 4's server side (502s from memory exhaustion) is **observed, not confirmed** — Render logs
  were never read.
- The tester's normal browser may still hold the pre-fix service worker — test in Incognito.
