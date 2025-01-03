from datetime import datetime
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4

class ImageBase(SQLModel):
  filename: str = Field(...)
  filepath: str = Field(...)
  content_type: str = Field(...)
  size: int = Field(...)
  predictions: str | None = Field(default=None)

class Image(ImageBase, table=True):
  id: UUID = Field(default_factory=uuid4, primary_key=True)
  created_at: datetime = Field(default_factory=datetime.utcnow)

class ImageCreate(ImageBase):
  id: UUID | None = None

class ImageRead(ImageBase):
  id: UUID
  predictions: str | None = None