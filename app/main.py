from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.api.routes import cameras, health, inspections, models
from app.core.config import get_settings
from app.ingestion.camera_manager import CameraManager
from app.infrastructure.database import initialize_database

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    initialize_database()
    manager = CameraManager()
    application.state.camera_manager = manager
    try:
        manager.start()
        yield
    finally:
        manager.stop()


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description=(
        "On-premises visual inspection API. RTSP capture is available when cameras are "
        "configured and the optional OpenCV dependency is installed. Model inference remains "
        "disabled until a validated and licensed backend is implemented."
    ),
    lifespan=lifespan,
)
app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(cameras.router, prefix=settings.api_v1_prefix)
app.include_router(models.router, prefix=settings.api_v1_prefix)
app.include_router(inspections.router, prefix=settings.api_v1_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {"name": settings.app_name, "docs": "/docs", "api_prefix": settings.api_v1_prefix}
