from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import messages
from app.crud.common import commit_or_raise_conflict
from app.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.security import hash_password


def get_users(db: Session):
    return db.scalars(select(User).order_by(User.id)).all()


def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    commit_or_raise_conflict(db, messages.EMAIL_ALREADY_REGISTERED)
    db.refresh(user)
    return user


def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    data = user_in.model_dump(exclude_unset=True)
    password = data.pop("password", None)
    if password is not None:
        user.hashed_password = hash_password(password)
    for field, value in data.items():
        setattr(user, field, value)
    commit_or_raise_conflict(db, messages.EMAIL_ALREADY_REGISTERED)
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    commit_or_raise_conflict(db, messages.USER_HAS_RELATED_DATA)
