from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app.core import messages
from app.core.exceptions import BadRequestException
from app.crud.common import commit_or_raise_conflict, get_or_raise
from app.enums import TaskPriority, TaskStatus
from app.models import Project, Tag, Task, TaskBookmark, User
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


def filter_tasks(
    statement: Select, status: TaskStatus | None, priority: TaskPriority | None, skip: int, limit: int
) -> Select:
    if status is not None:
        statement = statement.where(Task.status == status)
    if priority is not None:
        statement = statement.where(Task.priority == priority)
    return statement.order_by(Task.id).offset(skip).limit(limit)


def get_tasks(db: Session, status: TaskStatus | None, priority: TaskPriority | None, skip: int, limit: int):
    return db.scalars(filter_tasks(select(Task), status, priority, skip, limit)).all()


def get_project_tasks(
    db: Session, project_id: int, status: TaskStatus | None, priority: TaskPriority | None, skip: int, limit: int
):
    statement = select(Task).where(Task.project_id == project_id).options(joinedload(Task.tags))
    return db.scalars(filter_tasks(statement, status, priority, skip, limit)).unique().all()


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


def bookmark_task(db: Session, task: Task, user: User) -> TaskBookmark:
    bookmark = TaskBookmark(user_id=user.id, task_id=task.id)
    db.add(bookmark)
    commit_or_raise_conflict(db, messages.TASK_ALREADY_BOOKMARKED)
    db.refresh(bookmark)
    return bookmark
