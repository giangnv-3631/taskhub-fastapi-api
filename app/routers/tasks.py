from fastapi import APIRouter

from app.crud import task as task_crud
from app.dependencies import DbSession
from app.schemas.task import TaskRead

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead], summary="List tasks")
def list_tasks(db: DbSession) -> list[TaskRead]:
    return task_crud.get_tasks(db)
