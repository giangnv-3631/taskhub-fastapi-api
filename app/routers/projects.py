from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import project as project_crud
from app.database import get_db
from app.schemas.project import ProjectRead

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    return project_crud.get_projects(db)
