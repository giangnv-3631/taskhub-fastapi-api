from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Task


def get_tasks(db: Session):
    return db.scalars(select(Task)).all()
