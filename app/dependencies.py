from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core import messages
from app.core.exceptions import NotFoundException
from app.crud.common import get_or_raise
from app.database import get_db
from app.models import Project, Task, User

DbSession = Annotated[Session, Depends(get_db)]


def get_user_detail(user_id: int, db: DbSession) -> User:
    return get_or_raise(db, User, user_id, NotFoundException(messages.USER_NOT_FOUND))


def get_project_detail(project_id: int, db: DbSession) -> Project:
    return get_or_raise(db, Project, project_id, NotFoundException(messages.PROJECT_NOT_FOUND))


def get_task_detail(task_id: int, db: DbSession) -> Task:
    return get_or_raise(db, Task, task_id, NotFoundException(messages.TASK_NOT_FOUND))


UserDetail = Annotated[User, Depends(get_user_detail)]
ProjectDetail = Annotated[Project, Depends(get_project_detail)]
TaskDetail = Annotated[Task, Depends(get_task_detail)]
