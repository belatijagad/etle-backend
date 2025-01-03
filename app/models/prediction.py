from pydantic import BaseModel

class BoundingBox(BaseModel):
  x: float
  y: float
  width: float
  height: float
  confidence: float
  class_name: str

class PredictionResult(BaseModel):
  image_id: str
  predictions: list[BoundingBox]
  cropped_images: list[str] | None = None
