from fastapi import APIRouter, HTTPException, status

from app.crud import project as project_crud
from app.crud import task as task_crud
from app.crud import user as user_crud
from app.dependencies import DbSession
from app.models import Task
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def get_task_or_404(db: DbSession, task_id: int) -> Task:
    task = task_crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def ensure_user_exists(db: DbSession, user_id: int, field: str) -> None:
    if user_crud.get_user(db, user_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field} does not exist")


@router.get("", response_model=list[TaskRead], summary="List tasks")
def list_tasks(db: DbSession) -> list[TaskRead]:
    return [TaskRead.model_validate(task) for task in task_crud.get_tasks(db)]


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED, summary="Create task")
def create_task(task_in: TaskCreate, db: DbSession) -> TaskRead:
    if project_crud.get_project(db, task_in.project_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project does not exist")
    ensure_user_exists(db, task_in.creator_id, "Creator")
    if task_in.assignee_id is not None:
        ensure_user_exists(db, task_in.assignee_id, "Assignee")
    return TaskRead.model_validate(task_crud.create_task(db, task_in))


@router.get("/{task_id}", response_model=TaskRead, summary="Get task")
def read_task(task_id: int, db: DbSession) -> TaskRead:
    return TaskRead.model_validate(get_task_or_404(db, task_id))


@router.patch("/{task_id}", response_model=TaskRead, summary="Update task")
def update_task(task_id: int, task_in: TaskUpdate, db: DbSession) -> TaskRead:
    task = get_task_or_404(db, task_id)
    if task_in.assignee_id is not None:
        ensure_user_exists(db, task_in.assignee_id, "Assignee")
    return TaskRead.model_validate(task_crud.update_task(db, task, task_in))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete task")
def delete_task(task_id: int, db: DbSession) -> None:
    task = get_task_or_404(db, task_id)
    task_crud.delete_task(db, task)
