from typing import Annotated, Any, Literal

from pydantic import AnyUrl, BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict

def parse_cors(v: Any) -> list[str] | str:
  if isinstance(v, str) and not v.startswith('['):
    return [i.strip() for i in v.split(',')]
  elif isinstance(v, list | str):
    return v
  raise ValueError(v)

class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file='.env', env_ignore_empty=True, extra='ignore')
  API_STR: str = '/api'
  FRONTEND_HOST: str = 'http://localhost:3000'
  ENVIRONMENT: Literal['local', 'staging', 'production'] = 'local'
  BACKEND_CORS_ORIGINS: list[AnyUrl] | str = []
  ROBOFLOW_API_KEY: str = 'your_api_key_here'
  ROBOFLOW_MODEL_URL: str = 'https://detect.roboflow.com/helm-motor-siter/2'
  UPLOAD_DIR: str = 'images'
  CROPPED_IMAGES_DIR: str = 'cropped_images'

settings = Settings()