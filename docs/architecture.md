# Architecture

## Current scaffold

The application is a modular monolith. FastAPI exposes HTTP contracts; services coordinate domain operations; inference is behind an interface; SQLite stores inspection metadata. Camera configuration is read from environment settings and public responses deliberately omit source URLs.

## Implemented RTSP capture stage\n\n`app/ingestion/CameraManager` validates camera entries from `CAMERAS_JSON` and starts one worker per enabled camera. Each worker reconnects with capped exponential backoff and keeps only the newest frame in a queue of size one, intentionally dropping stale frames under load. `GET /api/v1/cameras/status` reports connection state, reconnect count, frame count, and last-frame age without exposing source URLs. OpenCV is an optional `vision` extra; no configured camera means no worker is started.\n\nOpenCV timeout-property support varies by build/backend. Validate that the selected RTSP backend actually honors open/read timeouts and that shutdown is bounded on the target system. Worker threads are daemonized as a last-resort process-exit safeguard, not a substitute for validating camera shutdown behavior.\n\n## Planned processing path

1. Camera adapter receives RTSP frames with explicit connect/read timeouts.
2. A bounded per-camera queue applies a documented drop/backpressure policy.
3. Preprocessing normalizes frame format and selects configured regions of interest.
4. The inference engine returns typed detections/anomaly scores with model version metadata.
5. Product-specific quality rules produce PASS, FAIL, or REVIEW.
6. Inspection metadata and optional artifact references are persisted.
7. Metrics record frame rate, inference latency, reconnects, queue drops, and decision counts.

## Safety invariants

- No configured/healthy inference engine means no quality decision.
- An ingestion or inference failure must never be converted to PASS.
- Model name, version, and weight digest must be traceable for every completed inspection.
- Camera URLs and credentials must never be returned by public APIs or committed to source control.
- RTSP targets must be restricted to approved camera networks to reduce SSRF/network-pivot risk.

## SQLite

SQLite is the initial metadata store. Use local storage, short transactions, foreign keys, WAL where supported, and a tested backup/restore procedure. It is not intended as a shared multi-host write database or a video-frame store.
