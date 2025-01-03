from uuid import UUID, uuid4
import aiofiles
import os
from fastapi import UploadFile, HTTPException, status
from sqlalchemy import func
from sqlmodel import select
from app.models.image import Image, ImageCreate
from app.core.config import settings
from app.core.exceptions import ImageNotFoundException, InvalidImageFormatException
from app.services.base_service import BaseService

class ImageService(BaseService):
  def __init__(self, upload_dir: str = 'images'):
    self.upload_dir = upload_dir

  async def upload(self, file: UploadFile) -> dict:
    try:
      await self._validate_image(file)
      await self._ensure_upload_dir()
      
      file_path, unique_filename, file_id = self._generate_file_path(file)
      await self._save_file(file, file_path)
      
      image_data = ImageCreate(
        id=UUID(file_id),  # Use the same ID
        filename=unique_filename,
        filepath=file_path,
        content_type=file.content_type,
        size=os.path.getsize(file_path)
      )
      db_image = await self._save_to_database(image_data)
      
      return {
        'status': 'success',
        'id': file_id,
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

  async def get_image(self, image_id: UUID) -> Image:
    with self.get_session() as session:
      image = session.get(Image, image_id)
      if not image:
        raise ImageNotFoundException()
      return image

  async def count_images(self) -> int:
    with self.get_session() as session:
      statement = select(func.count(Image.id))
      result = session.exec(statement).first()
      return result or 0

  async def list_images(self, skip: int = 0, limit: int = 100) -> list[Image]:
    with self.get_session() as session:
      statement = select(Image).offset(skip).limit(limit)
      images = session.exec(statement).all()
      return images

  async def list_violations(self, skip: int = 0, limit: int = 100) -> list[Image]:
    with self.get_session() as session:
      statement = select(Image).where(Image.predictions.isnot(None)).offset(skip).limit(limit)
      images = session.exec(statement).all()
      return images

  async def count_violations(self) -> int:
    with self.get_session() as session:
      result = session.exec(select(func.count()).select_from(Image).where(Image.predictions.isnot(None))).first()
      return result or 0

  async def delete_image(self, image_id: UUID) -> None:
    with self.get_session() as session:
      image = session.get(Image, image_id)
      if not image: raise ImageNotFoundException()
      if os.path.exists(image.filepath): os.remove(image.filepath)
      base_name = f"{image_id}_violation_"
      cropped_dir = settings.CROPPED_IMAGES_DIR
      for file in os.listdir(cropped_dir):
        if file.startswith(base_name):
          os.remove(os.path.join(cropped_dir, file))
      session.delete(image)
      session.commit()

  def _create_upload_response(self, db_image: Image, filename: str, filepath: str) -> dict:
    return {
      'status': 'success',
      'id': str(db_image.id),
      'filename': filename,
      'filepath': filepath,
      'message': 'Image uploaded successfully',
    }

  async def _validate_image(self, file: UploadFile) -> None:
    if not file.content_type.startswith('image/'):
      raise InvalidImageFormatException()

  async def _ensure_upload_dir(self) -> None:
    os.makedirs(self.upload_dir, exist_ok=True)

  def _generate_file_path(self, file: UploadFile) -> tuple[str, str]:
    original_extension = os.path.splitext(file.filename)[1]
    file_id = str(uuid4())
    unique_filename = f"{file_id}{original_extension}"
    file_path = os.path.join(self.upload_dir, unique_filename)
    return file_path, unique_filename, file_id

  async def _save_file(self, file: UploadFile, file_path: str) -> None:
    async with aiofiles.open(file_path, 'wb') as out_file:
      content = await file.read()
      await out_file.write(content)

  async def _save_to_database(self, image_data: ImageCreate) -> Image:
    try:
      with self.get_session() as session:
        db_image = Image.model_validate(image_data)
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
