from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi import status

from app.schemas import AnalyzeResponse, HealthResponse, VersionResponse
from app.services.simple_pipeline import simple_process_upload as process_upload
from app.services.model import get_device_label
from app.core.config import APP_VERSION


router = APIRouter()


@router.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok", device=get_device_label())


@router.get("/version", response_model=VersionResponse)
def version() -> VersionResponse:
    return VersionResponse(version=APP_VERSION)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(file: UploadFile = File(...)) -> AnalyzeResponse:
    try:
        return await process_upload(file)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error") from e


