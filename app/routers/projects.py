from fastapi import status

from app.core.exceptions import NotFoundException, error_responses
from app.crud import project as project_crud
from app.dependencies import DbSession, ManagedProject, ProjectDetail, ProjectManager
from app.routers.common import protected_router
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

router = protected_router("/api/projects", "projects")


@router.get("", response_model=list[ProjectRead], summary="List projects")
def list_projects(db: DbSession) -> list[ProjectRead]:
    return [ProjectRead.model_validate(project) for project in project_crud.get_projects(db)]


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
)
def create_project(project_in: ProjectCreate, current_user: ProjectManager, db: DbSession) -> ProjectRead:
    return ProjectRead.model_validate(project_crud.create_project(db, current_user, project_in))


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
def update_project(project_in: ProjectUpdate, project: ManagedProject, db: DbSession) -> ProjectRead:
    return ProjectRead.model_validate(project_crud.update_project(db, project, project_in))


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    responses=error_responses(NotFoundException),
)
def delete_project(project: ManagedProject, db: DbSession) -> None:
    project_crud.delete_project(db, project)

