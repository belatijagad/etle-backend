from sqlmodel import Session
from app.core.db import engine

class BaseService:
  def get_session(self) -> Session:
    return Session(engine)