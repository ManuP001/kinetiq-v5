// config.js — runtime config for the Kinetiq v4 camera PWA.
// The API base URL is the ONE thing that changes between local and deployed. Keep it here so
// deploy = edit this one line (or run set-api-url), never a code change.
//
// Local run (run_local): the API is same-host on :8000.
// Render/Cloudflare: set this to the deployed API origin (https://<api>.onrender.com), no trailing slash.
window.KINETIQ_CONFIG = {
  // unset — set to the deployed v5 API origin via set-api-url.ps1 during deploy wiring.
  // Empty is DELIBERATE: if the PWA is ever deployed unwired, every call becomes a
  // same-origin request to the static host, which 404s, and the app's API-unreachable
  // state shows plainly. Pointing at a stale origin instead would silently talk to the
  // wrong backend and look fine.
  API_BASE_URL: "",

  // How often we flush buffered keypoint frames to the detector API (ms). The API recomputes over
  // the whole buffer each call, so this trades latency against request volume. 400ms matches the
  // prototype_api design note (~300–500ms poll).
  POST_INTERVAL_MS: 400,

  // Pose model tag the detector keys its keypoint map on. Must stay "blazepose_33" — that is the
  // MediaPipe PoseLandmarker landmark order the detector's keypoint_map.py expects.
  POSE_MODEL: "blazepose_33",

  // Session roll-over, as fractions of the server's per-session frame cap (the cap itself is
  // read from GET /health -> session_max_frames, never restated here). At SESSION_ROLL_AT the
  // app starts a fresh server session, but only between reps so no rep is split. At
  // SESSION_FORCE_ROLL_AT it rolls regardless: splitting one rep beats an unrecoverable 413.
  SESSION_ROLL_AT: 0.8,
  SESSION_FORCE_ROLL_AT: 0.95,
};
