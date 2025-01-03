from datetime import datetime
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4

class ImageBase(SQLModel):
  filename: str
  filepath: str
  content_type: str
  size: int
  upload_time: datetime = Field(default_factory=datetime.utcnow)
    
class Image(ImageBase, table=True):
  id: UUID | None = Field(default_factory=uuid4, primary_key=True)
  prediction: str | None = Field(default=None)
  validation: bool | None = Field(default=None)

class ImageCreate(ImageBase):
  pass

class ImageRead(ImageBase):
  id: UUID
  predictions: str | None = None