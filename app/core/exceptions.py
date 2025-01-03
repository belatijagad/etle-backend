from fastapi import HTTPException, status

class ImageNotFoundException(HTTPException):
  def __init__(self):
    super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail='Image not found')

class InvalidImageFormatException(HTTPException):
  def __init__(self):
    super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail='File must be an image')