from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core import messages
from app.core.exceptions import BadRequestException
from app.crud.common import get_or_raise
from app.models import Project, Tag, Task, User
from app.schemas.task import TaskCreate, TaskUpdate


def ensure_assignee_exists(db: Session, assignee_id: int | None) -> None:
    if assignee_id is not None:
        get_or_raise(db, User, assignee_id, BadRequestException(messages.ASSIGNEE_NOT_FOUND))


def get_tags_or_raise(db: Session, tag_ids: list[int]) -> list[Tag]:
    unique_ids = set(tag_ids)
    if not unique_ids:
        return []
    tags = db.scalars(select(Tag).where(Tag.id.in_(unique_ids))).all()
    if len(tags) != len(unique_ids):
        raise BadRequestException(messages.TAG_REFERENCE_NOT_FOUND)
    return list(tags)


def get_tasks(db: Session):
    return db.scalars(select(Task).order_by(Task.id)).all()


def get_project_tasks(db: Session, project_id: int):
    statement = (
        select(Task)
        .where(Task.project_id == project_id)
        .options(joinedload(Task.tags))
        .order_by(Task.id)
    )
    return db.scalars(statement).unique().all()


def create_task(db: Session, project: Project, creator: User, task_in: TaskCreate) -> Task:
    ensure_assignee_exists(db, task_in.assignee_id)
    tags = get_tags_or_raise(db, task_in.tag_ids)
    task = Task(**task_in.model_dump(exclude={"tag_ids"}), project=project, creator=creator, tags=tags)
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
