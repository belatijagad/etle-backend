from sqlmodel import SQLModel, create_engine
from app.core.config import settings

DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
  DATABASE_URL, 
  echo=True,
  connect_args={"check_same_thread": False}
)

def init_db():
  SQLModel.metadata.create_all(engine)