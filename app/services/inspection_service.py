from app.domain.schemas import InspectionCreate, InspectionResult
from app.inference.engine import DisabledInferenceEngine, InferenceEngine
from app.infrastructure.database import get_inspection, save_inspection

class InspectionService:
    def __init__(self, engine: InferenceEngine | None = None) -> None:
        self.engine = engine or DisabledInferenceEngine()

    def create(self, request: InspectionCreate) -> InspectionResult:
        # Do not fabricate a detection result when no real engine exists.
        result = self.engine.inspect(request)
        save_inspection(result)
        return result

    @staticmethod
    def get(inspection_id: str) -> InspectionResult | None:
        return get_inspection(inspection_id)
