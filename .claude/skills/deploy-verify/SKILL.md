---
name: deploy-verify
description: >-
  Verify a Kinetiq deploy the way a browser sees it, after any deploy of the detector API or PWA and
  before handing a URL to a tester. Use when the user says "verify the deploy", "is the deploy good",
  "check prod", or pastes a Render/API URL after deploying.
---

# Skill: deploy-verify

Run the browser-faithful deploy check and interpret it. Do NOT substitute a plain `curl /health` —
that is the trap that hid the "Failed to fetch" bug for days (curl sends no Origin, isn't subject to
CORS). Steps:

1. From the code repo, run:
   `python evals/gate0/prototype_api/verify_deploy.py <api_base_url> --origin <pwa_https_origin>`
2. Read the output:
   - All checks PASS → report the deployed `version` and confirm CORS is correct on success AND error.
   - Any FAIL → report the exact failing check and its printed reason (this is what the browser would
     have shown only as "Failed to fetch"). Hand the reason to the user; do not fix silently.
3. Confirm the printed `version` is the git SHA just deployed. A stale version = the deploy didn't
   take or a cache/worker is serving old code — that is a failure, not a pass.
4. Always end by stating the one thing this cannot check: the on-phone smoke test in a CLEAN/Incognito
   profile on the canonical URL (no `?cb=`). A stale service worker in a normal browser serves the old
   app regardless of what's deployed.

For a deeper, structured audit, invoke the **deployment-verifier** subagent instead.
