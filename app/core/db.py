from sqlmodel import SQLModel, create_engine
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def get_engine_args():
  if settings.DB_TYPE == 'sqlite':
    return {'check_same_thread': False}
  return {}

def get_engine():
  engine_args = get_engine_args()
  engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
    connect_args=engine_args
  )
  return engine

engine = get_engine()

def init_db():
  try:
    logger.info(f'Initializing {settings.DB_TYPE} database...')
    SQLModel.metadata.create_all(engine)
    logger.info('Database initialized successfully')
  except Exception as e:
    logger.error(f'Error initializing database: {str(e)}')
    raise e
