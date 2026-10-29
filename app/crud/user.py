from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core import messages
from app.core.exceptions import ForbiddenException, NotFoundException, UnauthorizedException
from app.crud.common import commit_or_raise_conflict
from app.models import User
from app.schemas.base import normalize_lowercase
from app.schemas.user import UserCreate, UserMeUpdate
from app.security import DUMMY_PASSWORD_HASH, hash_password, verify_password


def get_users(db: Session):
    return db.scalars(select(User).order_by(User.id)).all()


def get_user_profile(db: Session, username: str) -> User:
    statement = (
        select(User)
        .where(User.username == username)
        .options(selectinload(User.projects), selectinload(User.assigned_tasks))
    )
    user = db.scalar(statement)
    if user is None:
        raise NotFoundException(messages.USER_NOT_FOUND)
    return user


def authenticate_user(db: Session, username: str, password: str) -> User:
    user = db.scalar(select(User).where(User.username == normalize_lowercase(username)))
    if user is None:
        verify_password(password, DUMMY_PASSWORD_HASH)
        raise UnauthorizedException(messages.INVALID_CREDENTIALS)
    if not verify_password(password, user.hashed_password):
        raise UnauthorizedException(messages.INVALID_CREDENTIALS)
    if not user.is_active:
        raise ForbiddenException(messages.INACTIVE_USER)
    return user


def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    commit_or_raise_conflict(db, messages.USER_ALREADY_EXISTS)
    db.refresh(user)
    return user


def update_user(db: Session, user: User, user_in: UserMeUpdate) -> User:
    for field, value in user_in.model_dump().items():
        setattr(user, field, value)
    commit_or_raise_conflict(db, messages.USER_ALREADY_EXISTS)
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    commit_or_raise_conflict(db, messages.USER_HAS_RELATED_DATA)
