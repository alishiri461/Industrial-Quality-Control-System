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
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e ".[dev]"
# Copy .env.example to .env and review every setting.
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The scaffold starts without loading YOLO weights. Model execution and RTSP capture are intentionally not enabled until their dependencies, hardware, and model license are confirmed.

## API

- `GET /api/v1/health/live` — process liveness.
- `GET /api/v1/health/ready` — readiness status.
- `GET /api/v1/models` — registered inference backends.
- `GET /api/v1/cameras` — configured camera metadata (credentials are never returned).
- `POST /api/v1/inspections` — create an inspection from metadata; live frame execution is enabled only when a suitable engine is configured.
- `GET /api/v1/inspections/{inspection_id}` — retrieve a saved inspection.

Interactive OpenAPI docs are available at `/docs` when the service is running.

## Production gates

1. Define defect classes and pass/fail criteria per product and inspection station.
2. Collect representative good/defective samples and create train/validation/test splits by physical product or production batch.
3. Benchmark candidate models on target hardware and record false-accept/false-reject rates per defect class.
4. Approve model/runtime licenses.
5. Configure authentication, RTSP network allowlists, secret management, backup/restore, monitoring, and retention.
6. Complete camera-disconnect, load, recovery, and acceptance tests before production rollout.

See `docs/architecture.md`, `docs/data-and-model-validation.md`, and `docs/deployment.md`.