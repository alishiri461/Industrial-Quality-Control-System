import json

from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError

from app.core.config import get_settings
from app.domain.schemas import CameraInfo

router = APIRouter(prefix="/cameras", tags=["cameras"])


def _configured_cameras() -> list[CameraInfo]:
    try:
        entries = json.loads(get_settings().cameras_json)
        if not isinstance(entries, list):
            raise ValueError("CAMERAS_JSON must be a JSON array")
        # CameraInfo is a public DTO; source_url and other private settings are omitted.
        return [CameraInfo.model_validate(item) for item in entries]
    except (json.JSONDecodeError, ValueError, ValidationError) as exc:
        raise HTTPException(status_code=500, detail="Invalid camera configuration") from exc


@router.get("", response_model=list[CameraInfo])
def list_cameras() -> list[CameraInfo]:
    return _configured_cameras()


@router.get("/status")
def camera_status(request: Request) -> dict[str, object]:
    manager = getattr(request.app.state, "camera_manager", None)
    return {
        "configured": len(_configured_cameras()),
        "workers": manager.statuses() if manager else [],
        "note": "Status reports capture state only; it does not imply inspection/model readiness.",
    }


@router.get("/{camera_id}", response_model=CameraInfo)
def get_camera(camera_id: str) -> CameraInfo:
    for camera in _configured_cameras():
        if camera.id == camera_id:
            return camera
    raise HTTPException(status_code=404, detail="Camera not found")
