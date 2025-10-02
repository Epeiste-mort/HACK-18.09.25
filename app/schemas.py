from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class AnalyzeResponse(BaseModel):
    label: Literal["Норма", "Патология"]
    probabilities: List[float] = Field(min_length=2, max_length=2)
    device: Literal["GPU", "CPU"]
    preview_png_b64: Optional[str] = None


class HealthResponse(BaseModel):
    status: Literal["ok"]
    device: Literal["GPU", "CPU"]


class VersionResponse(BaseModel):
    version: str


