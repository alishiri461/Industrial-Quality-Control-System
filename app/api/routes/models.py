from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(prefix="/models", tags=["models"])

@router.get("")
def list_models() -> dict[str, object]:
    settings = get_settings()
    configured = settings.inference_backend != "disabled"
    return {
        "active_backend": settings.inference_backend,
        "model_version": settings.model_version,
        "configured": configured,
        "production_validated": False,
        "note": "Model loading, license approval, and benchmark validation are not implemented yet.",
    }
