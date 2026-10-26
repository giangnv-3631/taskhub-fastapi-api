from fastapi import APIRouter, HTTPException, status

from app.crud import project as project_crud
from app.crud import user as user_crud
from app.dependencies import DbSession
from app.models import Project
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/api/projects", tags=["projects"])


def get_project_or_404(db: DbSession, project_id: int) -> Project:
    project = project_crud.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.get("", response_model=list[ProjectRead], summary="List projects")
def list_projects(db: DbSession) -> list[ProjectRead]:
    return [ProjectRead.model_validate(project) for project in project_crud.get_projects(db)]


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED, summary="Create project")
def create_project(project_in: ProjectCreate, db: DbSession) -> ProjectRead:
    if user_crud.get_user(db, project_in.owner_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner does not exist")
    return ProjectRead.model_validate(project_crud.create_project(db, project_in))


@router.get("/{project_id}", response_model=ProjectRead, summary="Get project")
def read_project(project_id: int, db: DbSession) -> ProjectRead:
    return ProjectRead.model_validate(get_project_or_404(db, project_id))


@router.patch("/{project_id}", response_model=ProjectRead, summary="Update project")
def update_project(project_id: int, project_in: ProjectUpdate, db: DbSession) -> ProjectRead:
    project = get_project_or_404(db, project_id)
    return ProjectRead.model_validate(project_crud.update_project(db, project, project_in))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete project")
def delete_project(project_id: int, db: DbSession) -> None:
    project = get_project_or_404(db, project_id)
    project_crud.delete_project(db, project)
