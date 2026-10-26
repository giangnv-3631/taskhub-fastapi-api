from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Tag


def get_tags(db: Session):
    return db.scalars(select(Tag).order_by(Tag.name)).all()
