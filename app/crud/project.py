from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import messages
from app.core.exceptions import BadRequestException
from app.crud.common import get_or_raise
from app.models import Project, User
from app.schemas.project import ProjectCreate, ProjectUpdate


def get_projects(db: Session):
    return db.scalars(select(Project).order_by(Project.id)).all()


def create_project(db: Session, project_in: ProjectCreate) -> Project:
    get_or_raise(db, User, project_in.owner_id, BadRequestException(messages.OWNER_NOT_FOUND))
    project = Project(**project_in.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, project: Project, project_in: ProjectUpdate) -> Project:
    for field, value in project_in.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project: Project) -> None:
    db.delete(project)
    db.commit()
