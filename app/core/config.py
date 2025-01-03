from typing import Any, Literal

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

def parse_cors(v: Any) -> list[str] | str:
  if isinstance(v, str) and not v.startswith('['):
    return [i.strip() for i in v.split(',')]
  elif isinstance(v, list | str):
    return v
  raise ValueError(v)

class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file='.env', env_ignore_empty=True, extra='ignore')
  DB_TYPE: str = 'sqlite'  # 'sqlite' or 'postgres'
  # SQLite settings
  SQLITE_DB_FILE: str = 'sql_app.db'
  # PostgreSQL settings
  POSTGRES_USER: str = 'postgres'
  POSTGRES_PASSWORD: str = 'abcd'
  POSTGRES_HOST: str = 'localhost'
  POSTGRES_PORT: str = '5432'
  POSTGRES_DB: str = 'etle_app'
  API_STR: str = '/api'
  FRONTEND_HOST: str = 'http://localhost:3000'
  ENVIRONMENT: Literal['local', 'staging', 'production'] = 'local'
  BACKEND_CORS_ORIGINS: list[AnyUrl] | str = []
  ROBOFLOW_API_KEY: str = 'your_api_key_here'
  ROBOFLOW_MODEL_URL: str = 'https://detect.roboflow.com/helm-motor-siter/2'
  UPLOAD_DIR: str = 'images'
  CROPPED_IMAGES_DIR: str = 'cropped_images'
  BASE_URL: str = 'http://localhost:8000'

  @property
  def DATABASE_URL(self) -> str:
    if self.DB_TYPE == 'postgres':
      return f'postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
    return f'sqlite:///./{self.SQLITE_DB_FILE}'

settings = Settings()