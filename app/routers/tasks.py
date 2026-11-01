from fastapi import status

from app.core.exceptions import BadRequestException, ConflictException, NotFoundException, error_responses
from app.crud import task as task_crud
from app.dependencies import (
    CurrentUser,
    DbSession,
    ManagedProject,
    ManagedTask,
    PaginationDep,
    ProjectDetail,
    TaskDetail,
    TaskFilterDep,
)
from app.routers.common import protected_router
from app.schemas.pagination import Page
from app.schemas.task import TaskAssign, TaskBookmarkRead, TaskCreate, TaskRead, TaskUpdate, TaskWithTagsRead

router = protected_router("/api/tasks", "tasks")
project_tasks_router = protected_router("/api/projects/{project_id}/tasks", "tasks")


@router.get("", response_model=Page[TaskRead], summary="List tasks")
def list_tasks(filters: TaskFilterDep, pagination: PaginationDep, db: DbSession) -> Page[TaskRead]:
    tasks, total = task_crud.get_tasks(db, filters, pagination)
    return Page[TaskRead](items=tasks, total=total)


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
    responses=error_responses(NotFoundException),
)
def update_task(task_in: TaskUpdate, task: ManagedTask, db: DbSession) -> TaskRead:
    return TaskRead.model_validate(task_crud.update_task(db, task, task_in))


@router.post(
    "/{task_id}/assign",
    response_model=TaskRead,
    summary="Assign task",
    responses=error_responses(NotFoundException, BadRequestException),
)
def assign_task(assign_in: TaskAssign, task: ManagedTask, db: DbSession) -> TaskRead:
    return TaskRead.model_validate(task_crud.assign_task(db, task, assign_in))


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    responses=error_responses(NotFoundException),
)
def delete_task(task: ManagedTask, db: DbSession) -> None:
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
    response_model=Page[TaskWithTagsRead],
    summary="List tasks of project",
    responses=error_responses(NotFoundException),
)
def list_project_tasks(
    project: ProjectDetail, filters: TaskFilterDep, pagination: PaginationDep, db: DbSession
) -> Page[TaskWithTagsRead]:
    tasks, total = task_crud.get_project_tasks(db, project.id, filters, pagination)
    return Page[TaskWithTagsRead](items=tasks, total=total)


@project_tasks_router.post(
    "",
    response_model=TaskWithTagsRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create task in project",
    responses=error_responses(NotFoundException, BadRequestException),
)
def create_project_task(
    task_in: TaskCreate, project: ManagedProject, current_user: CurrentUser, db: DbSession
) -> TaskWithTagsRead:
    return TaskWithTagsRead.model_validate(task_crud.create_task(db, project, current_user, task_in))
