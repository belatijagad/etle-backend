from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class ImageResponse(BaseModel):
  id: UUID
  filename: str
  filepath: str
  content_type: str
  size: int
  created_at: datetime
  predictions: Optional[str] = None
  
  model_config = ConfigDict(from_attributes=True)

class UploadResponse(BaseModel):
  status: str
  id: str
  filename: str
  filepath: str
  message: str

class PredictionResponse(BaseModel):
  status: str
  image_id: str
  predictions: List[dict]
  cropped_images: Optional[List[str]]
  message: str

class ListImagesResponse(BaseModel):
  total: int
  items: List[ImageResponse]
  page: int
  size: int
  pages: int