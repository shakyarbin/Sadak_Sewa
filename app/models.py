from pydantic import BaseModel
from typing import Optional
from ModelTypes import ModelType
from numpy import ndarray

class ImageRequest(BaseModel):
    image_path: str

class DetectionResult(BaseModel):
    damage_type: ModelType
    pothole_count: int
    waste_count: int
    confidence: float
    output_image_path: str  # New field for the output image path

class ErrorResponse(BaseModel):
    detail: str