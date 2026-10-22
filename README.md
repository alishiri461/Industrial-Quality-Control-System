# Industrial Quality Control System

An on-premises visual-inspection API for household appliances (refrigerators, televisions, cookers and related products), designed around live camera/RTSP ingestion, pluggable inference engines, configurable quality rules, and SQLite persistence.

> **Project status:** initial scaffold. No model has been validated for production defect detection. Product-specific data, defect taxonomy, camera geometry, hardware capacity, and model licensing must be confirmed before production use.

## Goals

- Receive frames from configured cameras and RTSP streams.
- Expose versioned REST APIs with FastAPI.
- Keep video ingestion, inference, and quality decisions separated.
- Persist inspection metadata and detections in SQLite; store optional image artifacts on disk.
- Fail safely: an unavailable camera or inference engine must never be reported as a passing inspection.
- Support later evaluation of YOLO detection/segmentation and anomaly-detection backends.

## Non-goals for the initial scaffold

- Claiming to detect every defect without a validated dataset.
- Automatic PLC or production-line control.
- Bundling pretrained weights or making a licensing decision on behalf of the operator.

## Quick start

Python 3.12 is the initial target. Create a virtual environment, install the project, configure `.env`, and run the API:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e ".[dev,vision]"
# Copy .env.example to .env and review every setting.
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The API starts without loading YOLO weights. RTSP capture is implemented as an optional OpenCV-backed worker and remains inactive unless camera entries are configured in the protected local `.env`. Actual inference and quality decisions remain disabled until the dataset, hardware, thresholds, and model license are approved.

## RTSP camera configuration

Set `CAMERAS_JSON` in the protected local `.env` to a JSON array. Each camera entry requires `id`, `name`, and `source_url` (an `rtsp://` or `rtsps://` URL). Optional values include `enabled`, `open_timeout_ms`, `read_timeout_ms`, `reconnect_initial_seconds`, and `reconnect_max_seconds`.

Never commit real camera URLs or credentials. Restrict the service host's outbound network access to approved camera subnets. OpenCV timeout support varies by build and backend; verify actual reconnect and shutdown behavior on the target host.

## API

- `GET /api/v1/health/live` — process liveness.
- `GET /api/v1/health/ready` — readiness status.
- `GET /api/v1/models` — registered inference backends.
- `GET /api/v1/cameras` — configured camera metadata; source URLs and credentials are omitted.
- `GET /api/v1/cameras/status` — capture worker connectivity, reconnect count, frame count, and last-frame age.
- `POST /api/v1/inspections` — request an inspection; returns an explicit unavailable error while inference is unconfigured.
- `GET /api/v1/inspections/{inspection_id}` — retrieve a saved inspection.

Interactive OpenAPI docs are available at `/docs` when the service is running.

## Production gates

1. Define defect classes and pass/fail criteria per product and inspection station.
2. Collect representative good/defective samples and create train/validation/test splits by physical product or production batch.
3. Benchmark candidate models on target hardware and record false-accept/false-reject rates per defect class.
4. Approve model/runtime licenses.
5. Configure authentication, RTSP network allowlists, secret management, backup/restore, monitoring, and retention.
6. Complete camera-disconnect, load, recovery, and acceptance tests before production rollout.
7. Verify OpenCV timeout behavior and bounded shutdown on the actual camera/backend combination.

See `docs/architecture.md`, `docs/data-and-model-validation.md`, and `docs/deployment.md`.
