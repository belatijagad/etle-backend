from fastapi import APIRouter

from app.api.routes import private, image, violation
from app.core.config import settings

api_router = APIRouter()

api_router.include_router(image.router)
api_router.include_router(violation.router)

if settings.ENVIRONMENT == 'local':
  api_router.include_router(private.router)