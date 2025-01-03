from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.db import init_db
from app.core.config import settings

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

os.makedirs("images", exist_ok=True)
os.makedirs("cropped_images", exist_ok=True)

app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/cropped_images", StaticFiles(directory="cropped_images"), name="cropped_images")

app.include_router(api_router, prefix=settings.API_STR)

@app.on_event("startup")
async def on_startup():
  init_db()