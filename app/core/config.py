import secrets
import warnings
from typing import Annotated, Any, Literal

from pydantic import AnyUrl, BeforeValidator, HttpUrl, PostgresDsn, computed_field, model_validator
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

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
  BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

settings = Settings()  # type: ignore