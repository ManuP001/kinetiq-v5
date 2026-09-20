#!/usr/bin/env python3
"""
verify_deploy.py — "can I trust what I just deployed?" in one command.

The problem this solves (docs/POSTMORTEM_FAILED_TO_FETCH.md): a deploy could be broken four
different ways and the browser showed only "Failed to fetch". check_local.sh uses curl, which is
NOT subject to CORS and does NOT send an Origin -- so it passed while the browser failed. This
script talks to the API the way the BROWSER does: it sends an `Origin` header and checks that the
CORS header comes back, on a success AND on a deliberately-broken request, then reports the
deployed version.

It is still not a real browser (no service worker, no mixed-content, no getUserMedia) -- the
on-phone smoke test in a clean/Incognito profile (docs/DEPLOY_RUNBOOK.md) remains the last word.
This catches the server/CORS/version class of failure in seconds, without a phone.

Stdlib only (urllib) -- runs anywhere, no install.

Usage:
    python verify_deploy.py <api_base_url> --origin <pwa_https_origin>

    # local dev run (origin defaults to the localhost PWA):
    python verify_deploy.py http://127.0.0.1:8000 --origin http://localhost:8080

    # deployed:
    python verify_deploy.py https://kinetiq-v4-api.onrender.com --origin https://kinetiq-v4.onrender.com

Exit code 0 = every check passed. Non-zero = at least one failed (details printed).
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


def _request(method, url, origin, body=None, timeout=20):
    """Return (status, headers_lower, body_text). A network-level failure returns status 0."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Origin", origin)  # <-- the thing curl never sends; makes CORS observable
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read().decode()
    except urllib.error.HTTPError as e:  # 4xx/5xx still carry headers + body
        return e.code, {k.lower(): v for k, v in e.headers.items()}, e.read().decode()
    except Exception as e:  # DNS, refused connection, timeout, TLS
        return 0, {}, f"{type(e).__name__}: {e}"


def _cors_ok(headers, origin):
    acao = headers.get("access-control-allow-origin")
    return acao is not None and acao in (origin, "*"), acao


# A real 33-keypoint BlazePose frame, exactly the shape frontend/app.js sends (incl. `box`) --
# a rough standing pose. One static frame => rep_count 0; we're checking the wire, not counting.
def _real_frame():
    kp = [[0.5, 0.15 + i * 0.02, 0.0, 0.9] for i in range(33)]
    return {
        "t_ms": 0,
        "pose_model": "blazepose_33",
        "people": [{"track_id": 0, "kp": kp, "box": [0.4, 0.1, 0.2, 0.8]}],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Browser-faithful deploy check for the detector API.")
    ap.add_argument("base_url", help="API base URL, e.g. https://kinetiq-v4-api.onrender.com")
    ap.add_argument("--origin", default="http://localhost:8080",
                    help="PWA origin to simulate in the Origin header (default: local PWA).")
    args = ap.parse_args()
    base = args.base_url.rstrip("/")
    origin = args.origin.rstrip("/")

    print(f"Verifying {base}  (as if called from {origin})\n")
    results = []  # (label, passed, detail)

    # 1) /health: 200, CORS present, and REPORT THE VERSION.
    st, h, body = _request("GET", f"{base}/health", origin)
    if st == 0:
        results.append(("health reachable", False, body))
    else:
        try:
            hb = json.loads(body)
        except Exception:
            hb = {}
        cors, acao = _cors_ok(h, origin)
        version = hb.get("version", "<none>")
        smf = hb.get("session_max_frames", "<none>")
        ok = st == 200 and hb.get("status") == "ok"
        results.append(("GET /health = 200 ok", ok, f"status={st}"))
        results.append(("/health CORS header present", cors, f"access-control-allow-origin={acao}"))
        print(f"    deployed version : {version}")
        print(f"    session_max_frames: {smf}\n")

    # 2) A GOOD assess (real PWA-shaped frame): 200 + CORS + valid response shape.
    good = {"session_id": "verify-deploy", "exercise_id": "squat", "reset": True, "frames": [_real_frame()]}
    st, h, body = _request("POST", f"{base}/prototype/assess", origin, good)
    cors, acao = _cors_ok(h, origin)
    shape_ok = False
    try:
        shape_ok = "rep_count" in json.loads(body)
    except Exception:
        pass
    results.append(("POST /assess (real frame) = 200", st == 200, f"status={st} body={body[:120]}"))
    results.append(("/assess success CORS header present", cors, f"access-control-allow-origin={acao}"))
    results.append(("/assess response has rep_count", shape_ok, ""))

    # 3) A DELIBERATELY BROKEN assess (frame missing `box`): must be a clean 422 that STILL
    #    carries CORS -- proving an error keeps its cause across the boundary (the root trap).
    bad_frame = {"t_ms": 0, "pose_model": "blazepose_33",
                 "people": [{"track_id": 0, "kp": [[0.5, 0.5, 0.0, 0.9]]}]}  # no box
    bad = {"session_id": "verify-deploy-bad", "exercise_id": "squat", "reset": True, "frames": [bad_frame]}
    st, h, body = _request("POST", f"{base}/prototype/assess", origin, bad)
    cors, acao = _cors_ok(h, origin)
    is_legible_4xx = st == 422
    has_reason = False
    try:
        has_reason = bool(json.loads(body).get("detail"))
    except Exception:
        pass
    results.append(("bad frame -> 422 (not 500/no-response)", is_legible_4xx, f"status={st}"))
    results.append(("error response STILL carries CORS", cors, f"access-control-allow-origin={acao}"))
    results.append(("error names the reason (detail)", has_reason, body[:120]))

    # ---- report ----
    print("  check                                          result")
    print("  " + "-" * 60)
    all_ok = True
    for label, passed, detail in results:
        mark = "PASS" if passed else "FAIL"
        if not passed:
            all_ok = False
        line = f"  {label:<46} {mark}"
        if not passed and detail:
            line += f"\n      -> {detail}"
        print(line)

    print()
    if all_ok:
        print("ALL CHECKS PASSED. The deploy is reachable, CORS is correct on success AND error,")
        print("and the version above is what's actually live. (Still run the on-phone smoke test")
        print("in a clean/Incognito profile -- this can't see service workers or mixed content.)")
        return 0
    print("SOME CHECKS FAILED (see above). This is what a browser would have hit as 'Failed to")
    print("fetch' -- but now you can read the actual reason. Fix, redeploy, re-run.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
