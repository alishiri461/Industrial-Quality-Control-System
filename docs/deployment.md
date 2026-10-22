# On-premises deployment notes

The initial scaffold targets Python 3.12 and a single service instance. Do not expose the API directly to untrusted networks without authentication, TLS termination, network controls, and rate/size limits.

## Required before production

- Replace development defaults and protect environment secrets with OS permissions or a secret manager.
- Configure camera network allowlists; never accept arbitrary RTSP URLs from unauthenticated callers.
- Decide authentication and authorization requirements.
- Define retention, backup, restore, disk monitoring, and incident procedures.
- Configure structured logs and metrics without recording credentials or sensitive frames.
- Benchmark target hardware and configure worker/process count. Do not assume more Uvicorn workers improve GPU inference.
- Validate restart/reconnect behavior, camera loss, model load failure, disk full, and graceful shutdown.
- Approve the model license and third-party dependency licenses.

## Configure RTSP capture

1. Install the optional vision dependencies with `python -m pip install -e ".[vision]"`.
2. Add approved camera records to the protected local `.env` as a JSON array in `CAMERAS_JSON`. Each entry needs `id`, `name`, `source_type: "rtsp"`, `source_url`, and optional `enabled`, `open_timeout_ms`, and `read_timeout_ms` values.
3. Restrict outbound access to approved camera subnets at the host/network firewall. Do not expose an API that accepts arbitrary RTSP URLs from callers.
4. Check `GET /api/v1/cameras/status` for worker state and last-frame age. This is capture telemetry only, not evidence of inference correctness.
5. Verify OpenCV's selected backend honors timeout parameters. Some builds require a fallback without bounded read timeouts; in that case, do not treat shutdown as guaranteed until integration-tested.

The worker keeps a single latest-frame slot per camera, so stale frames are dropped rather than accumulating unbounded latency. The current scaffold does not yet expose frame images to clients or connect frames to a model.

## Current limitations

RTSP capture, model loading, authentication, metrics export, artifact retention, and production-grade migrations are not implemented in this initial scaffold. Readiness currently reports a degraded state while inference is disabled.
