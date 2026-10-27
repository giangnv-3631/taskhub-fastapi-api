from fastapi import APIRouter, status

from app.core.exceptions import BadRequestException, NotFoundException, error_responses
from app.crud import task as task_crud
from app.dependencies import DbSession, TaskDetail
from app.schemas.task import TaskRead, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead], summary="List tasks")
def list_tasks(db: DbSession) -> list[TaskRead]:
    return [TaskRead.model_validate(task) for task in task_crud.get_tasks(db)]


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get task",
    responses=error_responses(NotFoundException),
)
def read_task(task: TaskDetail) -> TaskRead:
    return TaskRead.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    summary="Update task",
    responses=error_responses(NotFoundException, BadRequestException),
)
def update_task(task_in: TaskUpdate, task: TaskDetail, db: DbSession) -> TaskRead:
    return TaskRead.model_validate(task_crud.update_task(db, task, task_in))


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    responses=error_responses(NotFoundException),
)
def delete_task(task: TaskDetail, db: DbSession) -> None:
    task_crud.delete_task(db, task)
