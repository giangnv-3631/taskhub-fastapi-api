from fastapi import APIRouter, status

from app.core.exceptions import BadRequestException, NotFoundException, error_responses
from app.crud import project as project_crud
from app.crud import task as task_crud
from app.dependencies import DbSession, ProjectDetail
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.schemas.task import TaskCreate, TaskWithTagsRead

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead], summary="List projects")
def list_projects(db: DbSession) -> list[ProjectRead]:
    return [ProjectRead.model_validate(project) for project in project_crud.get_projects(db)]


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
    responses=error_responses(BadRequestException),
)
def create_project(project_in: ProjectCreate, db: DbSession) -> ProjectRead:
    return ProjectRead.model_validate(project_crud.create_project(db, project_in))


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Get project",
    responses=error_responses(NotFoundException),
)
def read_project(project: ProjectDetail) -> ProjectRead:
    return ProjectRead.model_validate(project)


@router.patch(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Update project",
    responses=error_responses(NotFoundException),
)
def update_project(project_in: ProjectUpdate, project: ProjectDetail, db: DbSession) -> ProjectRead:
    return ProjectRead.model_validate(project_crud.update_project(db, project, project_in))


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    responses=error_responses(NotFoundException),
)
def delete_project(project: ProjectDetail, db: DbSession) -> None:
    project_crud.delete_project(db, project)


@router.get(
    "/{project_id}/tasks",
    response_model=list[TaskWithTagsRead],
    summary="List tasks of project",
    responses=error_responses(NotFoundException),
)
def list_project_tasks(project: ProjectDetail, db: DbSession) -> list[TaskWithTagsRead]:
    return [TaskWithTagsRead.model_validate(task) for task in task_crud.get_project_tasks(db, project.id)]


@router.post(
    "/{project_id}/tasks",
    response_model=TaskWithTagsRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create task in project",
    responses=error_responses(NotFoundException, BadRequestException),
)
def create_project_task(task_in: TaskCreate, project: ProjectDetail, db: DbSession) -> TaskWithTagsRead:
    return TaskWithTagsRead.model_validate(task_crud.create_task(db, project, task_in))
