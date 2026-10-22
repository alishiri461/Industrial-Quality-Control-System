from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/live")
def liveness() -> dict[str, str]:
    return {"status": "alive"}

@router.get("/ready")
def readiness() -> dict[str, str]:
    settings = get_settings()
    status = "ready" if settings.inference_backend != "disabled" else "degraded"
    return {
        "status": status,
        "inference_backend": settings.inference_backend,
        "note": "Readiness does not yet validate model weights or camera connectivity.",
    }
