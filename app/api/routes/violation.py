from fastapi import APIRouter, Query, HTTPException, status
from typing import Annotated

from app.services.violation_service import ViolationService
from app.api.schemas.responses import (
  ViolationListResponse,
  ViolationResponse,
)

router = APIRouter(prefix='/violation', tags=['violation'])
violation_service = ViolationService()

@router.get(
  '/list',
  response_model=ViolationListResponse,
  description="Get all violations"
)
async def get_violations(
  page: Annotated[int, Query(ge=1, description="Page number")] = 1,
  size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10
) -> ViolationListResponse:
  try:
    skip = (page - 1) * size
    
    violations = await violation_service.list_violations(skip=skip, limit=size)
    total = await violation_service.count_violations()
    pages = (total + size - 1) // size if total else 0
    
    items = [
      ViolationResponse(
        id=violation.id,
        status=violation.status,
        type=violation.type,
        plate_number=violation.plate_number,
        timestamp=violation.timestamp,
        location=violation.location,
        image_url=violation.image_url,
        drone=violation.drone
      ) for violation in violations
    ]
    
    return ViolationListResponse(
      total=total,
      items=items,
      page=page,
      size=size,
      pages=pages
    )
  
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=str(e)
    )