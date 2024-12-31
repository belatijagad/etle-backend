from fastapi import APIRouter

router = APIRouter(tags=['private'], prefix='/private')

@router.get('/')
def get_root():
  return 'Hello World!'