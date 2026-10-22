# On-premises deployment notes

The scaffold targets Python 3.12 and a single service instance. Do not expose the API directly to untrusted networks without authentication, TLS termination, network controls, and rate/size limits.

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
2. Add approved camera records to the protected local `.env` as a JSON array in `CAMERAS_JSON`. Each entry requires `id`, `name`, and `source_url` using `rtsp://` or `rtsps://`; `source_type` defaults to `rtsp`. Optional values include `enabled`, `open_timeout_ms`, `read_timeout_ms`, `reconnect_initial_seconds`, and `reconnect_max_seconds`.
3. Restrict outbound access to approved camera subnets at the host/network firewall. Do not expose an API that accepts arbitrary RTSP URLs from callers.
4. Check `GET /api/v1/cameras/status` for worker state and last-frame age. This is capture telemetry only, not evidence of inference correctness.
5. Verify OpenCV's selected backend honors timeout parameters. Some builds require a fallback without bounded read timeouts; in that case, do not treat shutdown as guaranteed until integration-tested.

Each worker keeps a single latest-frame slot, so stale frames are dropped rather than accumulating unbounded latency. The API does not yet expose frame images to clients or connect captured frames to a model.

## Current limitations

YOLO/model loading, product-specific quality rules, authentication/authorization, metrics export, artifact retention, and production-grade migrations are not implemented. Readiness remains degraded; camera capture status does not indicate model readiness or inspection correctness.
