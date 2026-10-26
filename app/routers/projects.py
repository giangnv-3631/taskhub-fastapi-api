from fastapi import APIRouter

from app.crud import project as project_crud
from app.dependencies import DbSession
from app.schemas.project import ProjectRead

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead], summary="List projects")
def list_projects(db: DbSession) -> list[ProjectRead]:
    return project_crud.get_projects(db)
