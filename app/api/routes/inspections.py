from fastapi import APIRouter, HTTPException, status
from app.domain.schemas import InspectionCreate, InspectionResult
from app.inference.engine import InferenceNotConfigured
from app.services.inspection_service import InspectionService

router = APIRouter(prefix="/inspections", tags=["inspections"])
service = InspectionService()

@router.post("", response_model=InspectionResult, status_code=status.HTTP_201_CREATED)
def create_inspection(request: InspectionCreate) -> InspectionResult:
    try:
        return service.create(request)
    except InferenceNotConfigured as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "INFERENCE_NOT_CONFIGURED", "message": str(exc)},
        ) from exc

@router.get("/{inspection_id}", response_model=InspectionResult)
def read_inspection(inspection_id: str) -> InspectionResult:
    result = service.get(inspection_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return result
