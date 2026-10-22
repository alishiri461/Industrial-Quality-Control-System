from pydantic import SecretStr, ValidationError
import pytest

from app.ingestion.camera_config import CameraConfig
from app.ingestion.rtsp_source import FramePacket, RTSPCameraWorker


def camera_config(**overrides: object) -> CameraConfig:
    values: dict[str, object] = {
        "id": "cam-01",
        "name": "Camera 01",
        "source_type": "rtsp",
        "source_url": SecretStr("rtsp://camera.example/stream"),
        "enabled": True,
    }
    values.update(overrides)
    return CameraConfig.model_validate(values)


def test_rejects_non_rtsp_source() -> None:
    with pytest.raises(ValidationError):
        camera_config(source_url=SecretStr("http://camera.example/stream"))


def test_disabled_worker_does_not_start_thread() -> None:
    worker = RTSPCameraWorker(camera_config(enabled=False))
    worker.start()
    status = worker.status()
    assert status.enabled is False
    assert status.state == "disabled"
    assert status.connected is False


def test_frame_queue_keeps_latest_frame_only() -> None:
    worker = RTSPCameraWorker(camera_config())
    worker._publish(FramePacket("cam-01", 1.0, "older"))
    worker._publish(FramePacket("cam-01", 2.0, "newer"))
    packet = worker.latest_frame()
    assert packet is not None
    assert packet.frame == "newer"
    assert worker.latest_frame() is None
