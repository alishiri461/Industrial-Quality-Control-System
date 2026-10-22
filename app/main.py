from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import cameras, health, inspections, models
from app.core.config import get_settings
from app.infrastructure.database import initialize_database

@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "On-premises visual inspection API scaffold. Inference is disabled until "
        "a validated and licensed model backend is explicitly configured."
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
