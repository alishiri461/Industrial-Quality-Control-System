import json
import logging

from pydantic import ValidationError

from app.core.config import get_settings
from app.ingestion.camera_config import CameraConfig
from app.ingestion.rtsp_source import RTSPCameraWorker

logger = logging.getLogger(__name__)


class CameraManager:
    def __init__(self) -> None:
        self._workers: dict[str, RTSPCameraWorker] = {}

    def start(self) -> None:
        raw = get_settings().cameras_json
        try:
            items = json.loads(raw)
            if not isinstance(items, list):
                raise ValueError("CAMERAS_JSON must be a JSON array")
            configs = [CameraConfig.model_validate(item) for item in items]
        except (json.JSONDecodeError, ValueError, ValidationError) as exc:
            raise RuntimeError("Invalid CAMERAS_JSON camera configuration") from exc

        ids = [camera.id for camera in configs]
        if len(ids) != len(set(ids)):
            raise RuntimeError("CAMERAS_JSON contains duplicate camera IDs")

        for config in configs:
            worker = RTSPCameraWorker(config)
            self._workers[config.id] = worker
            worker.start()
        logger.info("Camera ingestion manager initialized: configured=%d", len(self._workers))

    def stop(self) -> None:
        for worker in self._workers.values():
            worker.stop()
        self._workers.clear()

    def statuses(self) -> list[dict[str, object]]:
        return [worker.status().__dict__ for worker in self._workers.values()]

    def get_worker(self, camera_id: str) -> RTSPCameraWorker | None:
        return self._workers.get(camera_id)
