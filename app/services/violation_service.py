from sqlmodel import select, func
from app.services.base_service import BaseService
from app.models.violation import Violation

class ViolationService(BaseService):
  async def list_violations(self, skip: int = 0, limit: int = 100) -> list[Violation]:
    with self.get_session() as session:
      statement = select(Violation).order_by(Violation.timestamp.desc()).offset(skip).limit(limit)
      return session.exec(statement).all()

  async def count_violations(self) -> int:
    with self.get_session() as session:
      total = session.exec(select(func.count()).select_from(Violation)).first()
      return total or 0