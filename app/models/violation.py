from datetime import datetime
from sqlmodel import Field, SQLModel

class ViolationBase(SQLModel):
  status: int = Field(default=0)
  type: int = Field(...)
  plate_number: str | None = Field(default=None)
  timestamp: datetime = Field(default_factory=datetime.utcnow)
  location: str | None = Field(default=None)
  image_url: str = Field(...)
  drone: str | None = Field(default=None)

class Violation(ViolationBase, table=True):
  id: int = Field(default=None, primary_key=True)

class ViolationCreate(ViolationBase):
  pass
