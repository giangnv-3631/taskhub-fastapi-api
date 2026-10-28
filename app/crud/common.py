from typing import TypeVar

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppException, ConflictException
from app.database import Base

ModelT = TypeVar("ModelT", bound=Base)


def get_or_raise(db: Session, model: type[ModelT], obj_id: int, exception: AppException) -> ModelT:
    obj = db.get(model, obj_id)
    if obj is None:
        raise exception
    return obj


def commit_or_raise_conflict(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictException(message) from exc
