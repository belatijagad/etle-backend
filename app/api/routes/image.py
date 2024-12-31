from fastapi import APIRouter, UploadFile
from app.services.image_service import ImageService

router = APIRouter(tags=['image'], prefix='/image')
image_service = ImageService()

@router.post('/upload')
async def upload_image(file: UploadFile):
  return await image_service.upload(file)