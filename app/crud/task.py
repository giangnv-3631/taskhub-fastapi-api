from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import messages
from app.core.exceptions import BadRequestException
from app.crud.common import get_or_raise
from app.models import Project, Task, User
from app.schemas.task import TaskCreate, TaskUpdate


def ensure_assignee_exists(db: Session, assignee_id: int | None) -> None:
    if assignee_id is not None:
        get_or_raise(db, User, assignee_id, BadRequestException(messages.ASSIGNEE_NOT_FOUND))


def get_tasks(db: Session):
    return db.scalars(select(Task).order_by(Task.id)).all()


def create_task(db: Session, task_in: TaskCreate) -> Task:
    get_or_raise(db, Project, task_in.project_id, BadRequestException(messages.PROJECT_REFERENCE_NOT_FOUND))
    get_or_raise(db, User, task_in.creator_id, BadRequestException(messages.CREATOR_NOT_FOUND))
    ensure_assignee_exists(db, task_in.assignee_id)
    task = Task(**task_in.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: Task, task_in: TaskUpdate) -> Task:
    ensure_assignee_exists(db, task_in.assignee_id)
    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()
