from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/live")
def liveness() -> dict[str, str]:
    return {"status": "alive"}

@router.get("/ready")
def readiness() -> dict[str, str]:
    settings = get_settings()
    # A configured backend name is not proof that weights loaded or cameras are healthy.
    return {
        "status": "degraded",
        "inference_backend": settings.inference_backend,
        "note": "Readiness remains degraded until model loading and camera health checks are implemented.",
    }
