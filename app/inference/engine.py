from typing import Protocol
from app.domain.schemas import InspectionCreate, InspectionResult

class InferenceNotConfigured(RuntimeError):
    """Raised when a production-capable inference backend has not been configured."""

class InferenceEngine(Protocol):
    @property
    def name(self) -> str: ...
    @property
    def version(self) -> str: ...
    def inspect(self, request: InspectionCreate) -> InspectionResult: ...

class DisabledInferenceEngine:
    name = "disabled"
    version = "unconfigured"

    def inspect(self, request: InspectionCreate) -> InspectionResult:
        raise InferenceNotConfigured(
            "No inference engine is configured. Do not treat an unavailable model as PASS."
        )
