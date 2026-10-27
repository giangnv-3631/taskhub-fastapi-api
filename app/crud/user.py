from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


def get_users(db: Session):
    return db.scalars(select(User)).all()
