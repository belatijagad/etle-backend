from fastapi import APIRouter, UploadFile, Query
from uuid import UUID
from app.services.image_service import ImageService
from app.services.prediction_service import PredictionService

router = APIRouter(tags=['image'], prefix='/image')
image_service = ImageService()
prediction_service = PredictionService()

@router.post('/upload')
async def upload_image(file: UploadFile):
  return await image_service.upload(file)

@router.post('/predict/{image_id}')
async def predict_image(image_id: UUID):
  return await prediction_service.predict_image(image_id)

@router.get('/list')
async def list_images(skip: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
  return await image_service.list_images(skip, limit)

@router.get('/{image_id}')
async def get_image(image_id: UUID):
  return await image_service.get_image(image_id)