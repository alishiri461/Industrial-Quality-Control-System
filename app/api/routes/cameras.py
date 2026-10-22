import json
from fastapi import APIRouter, HTTPException
from app.core.config import get_settings
from app.domain.schemas import CameraInfo

router = APIRouter(prefix="/cameras", tags=["cameras"])

def _configured_cameras() -> list[CameraInfo]:
    try:
        entries = json.loads(get_settings().cameras_json)
        if not isinstance(entries, list):
            raise ValueError("CAMERAS_JSON must be a JSON array")
        return [CameraInfo.model_validate(item) for item in entries]
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=500, detail="Invalid camera configuration") from exc

@router.get("", response_model=list[CameraInfo])
def list_cameras() -> list[CameraInfo]:
    # CameraInfo intentionally omits source URLs to avoid leaking credentials.
    return _configured_cameras()

@router.get("/{camera_id}", response_model=CameraInfo)
def get_camera(camera_id: str) -> CameraInfo:
    for camera in _configured_cameras():
        if camera.id == camera_id:
            return camera
    raise HTTPException(status_code=404, detail="Camera not found")
