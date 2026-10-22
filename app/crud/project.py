from sqlalchemy.orm import Session

from app.models import Project


def get_projects(db: Session):
    return db.query(Project).all()
