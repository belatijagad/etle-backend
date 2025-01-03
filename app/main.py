from fastapi import FastAPI
from fastapi.routing import APIRoute
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

app.include_router(api_router, prefix=settings.API_STR)

@app.on_event("startup")
async def on_startup():
  init_db()