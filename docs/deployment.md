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

## Current limitations

RTSP capture, model loading, authentication, metrics export, artifact retention, and production-grade migrations are not implemented in this initial scaffold. Readiness currently reports a degraded state while inference is disabled.
