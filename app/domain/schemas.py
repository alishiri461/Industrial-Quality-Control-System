from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def new_id() -> str:
    return str(uuid4())

class InspectionStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class QualityDecision(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    REVIEW = "review"

class Detection(BaseModel):
    class_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: list[float] | None = Field(default=None, min_length=4, max_length=4)
    mask_reference: str | None = None

class InspectionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    product_type: str = Field(min_length=1, max_length=100)
    camera_id: str = Field(min_length=1, max_length=100)
    product_serial: str | None = Field(default=None, max_length=120)
    station_id: str | None = Field(default=None, max_length=100)
    idempotency_key: str | None = Field(default=None, max_length=200)
    metadata: dict[str, Any] = Field(default_factory=dict)

class InspectionResult(BaseModel):
    inspection_id: str
    product_type: str
    camera_id: str
    status: InspectionStatus
    decision: QualityDecision | None = None
    model_name: str | None = None
    model_version: str | None = None
    detections: list[Detection] = Field(default_factory=list)
    captured_at: datetime = Field(default_factory=utc_now)
    processing_ms: float | None = None
    error_code: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class CameraInfo(BaseModel):
    id: str
    name: str
    source_type: str
    enabled: bool = True
