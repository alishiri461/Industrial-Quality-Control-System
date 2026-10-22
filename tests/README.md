# Validation plan

Test files cover initial health/model/inspection API contracts and RTSP camera configuration, disabled-worker behavior, and latest-frame queue semantics.

These tests have **not been executed**. Add target-system integration tests before production use, including actual RTSP connect/read timeout behavior, reconnect after network interruption, shutdown while a stream is stalled, camera-count/load behavior, disk full, and end-to-end inference/quality decisions.
