from fastapi import status

from app.core.constants import DEFAULT_PAGE_LIMIT
from app.core.exceptions import BadRequestException, ConflictException, NotFoundException, error_responses
from app.crud import task as task_crud
from app.dependencies import CurrentUser, DbSession, Limit, ProjectDetail, Skip, TaskDetail
from app.routers.common import protected_router
from app.schemas.task import (
    TaskBookmarkRead,
    TaskCreate,
    TaskPriorityFilter,
    TaskRead,
    TaskStatusFilter,
    TaskUpdate,
    TaskWithTagsRead,
)

router = protected_router("/api/tasks", "tasks")
project_tasks_router = protected_router("/api/projects/{project_id}/tasks", "tasks")


@router.get("", response_model=list[TaskRead], summary="List tasks")
def list_tasks(
    db: DbSession,
    status: TaskStatusFilter = None,
    priority: TaskPriorityFilter = None,
    skip: Skip = 0,
    limit: Limit = DEFAULT_PAGE_LIMIT,
) -> list[TaskRead]:
    tasks = task_crud.get_tasks(db, status, priority, skip, limit)
    return [TaskRead.model_validate(task) for task in tasks]


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


@router.post(
    "/{task_id}/bookmark",
    response_model=TaskBookmarkRead,
    status_code=status.HTTP_201_CREATED,
    summary="Bookmark task",
    responses=error_responses(NotFoundException, ConflictException),
)
def bookmark_task(task: TaskDetail, current_user: CurrentUser, db: DbSession) -> TaskBookmarkRead:
    return TaskBookmarkRead.model_validate(task_crud.bookmark_task(db, task, current_user))


@project_tasks_router.get(
    "",
    response_model=list[TaskWithTagsRead],
    summary="List tasks of project",
    responses=error_responses(NotFoundException),
)
def list_project_tasks(
    project: ProjectDetail,
    db: DbSession,
    status: TaskStatusFilter = None,
    priority: TaskPriorityFilter = None,
    skip: Skip = 0,
    limit: Limit = DEFAULT_PAGE_LIMIT,
) -> list[TaskWithTagsRead]:
    tasks = task_crud.get_project_tasks(db, project.id, status, priority, skip, limit)
    return [TaskWithTagsRead.model_validate(task) for task in tasks]


@project_tasks_router.post(
    "",
    response_model=TaskWithTagsRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create task in project",
    responses=error_responses(NotFoundException, BadRequestException),
)
def create_project_task(
    task_in: TaskCreate, project: ProjectDetail, current_user: CurrentUser, db: DbSession
) -> TaskWithTagsRead:
    return TaskWithTagsRead.model_validate(task_crud.create_task(db, project, current_user, task_in))
