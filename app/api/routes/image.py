from fastapi import APIRouter, UploadFile, File, Query, HTTPException, status
from fastapi.responses import FileResponse
from uuid import UUID
from typing import Annotated
import os

from app.services.image_service import ImageService
from app.services.prediction_service import PredictionService
from app.core.exceptions import ImageNotFoundException, InvalidImageFormatException
from app.core.config import settings
from app.api.schemas.responses import (
  UploadResponse,
  PredictionResponse,
  ImageResponse,
  ListImagesResponse
)

router = APIRouter(prefix='/image', tags=['image'])
image_service = ImageService()
prediction_service = PredictionService()

@router.post(
  '/upload',
  response_model=UploadResponse,
  status_code=status.HTTP_201_CREATED
)
async def upload_image(
  file: Annotated[UploadFile, File(description="The image file to upload")]
) -> UploadResponse:
  try:
    result = await image_service.upload(file)
    return UploadResponse(**result)
  except InvalidImageFormatException as e:
    raise e
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=str(e)
    )

@router.post(
  '/predict/{image_id}',
  response_model=PredictionResponse
)
async def predict_image(
  image_id: UUID
) -> PredictionResponse:
  try:
    result = await prediction_service.predict_image(image_id)
    return PredictionResponse(**result)
  except ImageNotFoundException as e:
    raise e
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=str(e)
    )

@router.get(
  '/list',
  response_model=ListImagesResponse
)
async def list_images(
  page: Annotated[int, Query(ge=1, description="Page number")] = 1,
  size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10
) -> ListImagesResponse:
  try:
    skip = (page - 1) * size
    images = await image_service.list_images(skip=skip, limit=size)
    total = await image_service.count_images()
    pages = (total + size - 1) // size
    
    image_responses = [ImageResponse.model_validate(image) for image in images]
    
    return ListImagesResponse(
      total=total,
      items=image_responses,
      page=page,
      size=size,
      pages=pages
    )
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=str(e)
    )

@router.get(
  '/{image_id}',
  response_model=ImageResponse
)
async def get_image(
  image_id: UUID
) -> ImageResponse:
  try:
    image = await image_service.get_image(image_id)
    return ImageResponse.model_validate(image)
  except ImageNotFoundException as e:
    raise e
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=str(e)
    )

@router.get(
  '/cropped/{filename}',
  response_class=FileResponse
)
async def get_cropped_image(
  filename: str
) -> FileResponse:
  try:
    file_path = os.path.join(settings.CROPPED_IMAGES_DIR, filename)
    if not os.path.exists(file_path):
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Cropped image not found"
      )
    return FileResponse(file_path)
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=str(e)
    )

@router.delete(
  '/{image_id}',
  status_code=status.HTTP_204_NO_CONTENT
)
async def delete_image(
  image_id: UUID
) -> None:
  try:
    await image_service.delete_image(image_id)
  except ImageNotFoundException as e:
    raise e
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=str(e)
    )