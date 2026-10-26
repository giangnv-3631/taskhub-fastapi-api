from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project


def get_projects(db: Session):
    return db.scalars(select(Project)).all()
