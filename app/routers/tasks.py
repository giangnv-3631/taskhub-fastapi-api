from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import task as task_crud
from app.database import get_db
from app.schemas.task import TaskRead

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
def list_tasks(db: Session = Depends(get_db)):
    return task_crud.get_tasks(db)
