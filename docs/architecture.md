# Architecture

## Current scaffold

The application is a modular monolith. FastAPI exposes HTTP contracts; services coordinate domain operations; inference is behind an interface; SQLite stores inspection metadata. Camera configuration is read from environment settings and public responses deliberately omit source URLs.

## Planned processing path

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
