import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException, status

class ImageService:
  def __init__(self, upload_dir: str = 'images'):
    self.upload_dir = upload_dir

  async def upload(self, file: UploadFile) -> dict:
    try:
      await self._validate_image(file)
      await self._ensure_upload_dir()
      
      file_path, unique_filename = self._generate_file_path(file)
      await self._save_file(file, file_path)
      
      return {
        'status': 'success',
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