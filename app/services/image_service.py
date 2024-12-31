import os
import uuid
import json
from datetime import datetime
import aiofiles
from fastapi import UploadFile, HTTPException, status
from sqlmodel import Session, select
from app.models.image import Image, ImageCreate
from app.core.db import engine

class ImageService:
  def __init__(self, upload_dir: str = 'images'):
    self.upload_dir = upload_dir

  async def upload(self, file: UploadFile) -> dict:
    try:
      await self._validate_image(file)
      await self._ensure_upload_dir()
      
      file_path, unique_filename = self._generate_file_path(file)
      await self._save_file(file, file_path)
      
      image_data = ImageCreate(
        filename=unique_filename,
        filepath=file_path,
        content_type=file.content_type,
        size=os.path.getsize(file_path)
      )
      db_image = await self._save_to_database(image_data)
      
      return {
        'status': 'success',
        'id': str(db_image.id),
        'filename': unique_filename,
        'filepath': file_path,
        'message': 'Image uploaded successfully',
      }
        
    except HTTPException as he:
      raise he
    except Exception as e:
      raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f'An error occurred while uploading the image: {str(e)}'
      )

  async def _save_to_database(self, image_data: ImageCreate) -> Image:
    try:
      with Session(engine) as session:
        db_image = Image.from_orm(image_data)
        session.add(db_image)
        session.commit()
        session.refresh(db_image)
        return db_image
    except Exception as e:
      if os.path.exists(image_data.filepath):
        os.remove(image_data.filepath)
      raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Failed to save image to database: {str(e)}"
      )

  async def _validate_image(self, file: UploadFile) -> None:
    if not file.content_type.startswith('image/'):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='File must be an image')

  async def _ensure_upload_dir(self) -> None:
    if not os.path.exists(self.upload_dir):
        os.makedirs(self.upload_dir)

  def _generate_file_path(self, file: UploadFile) -> tuple[str, str]:
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f'{uuid.uuid4()}{file_extension}'
    file_path = os.path.join(self.upload_dir, unique_filename)
    return file_path, unique_filename

  async def _save_file(self, file: UploadFile, file_path: str) -> None:
    async with aiofiles.open(file_path, 'wb') as out_file:
      content = await file.read()
      await out_file.write(content)