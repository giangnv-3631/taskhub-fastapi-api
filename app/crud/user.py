from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.security import hash_password


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_users(db: Session):
    return db.scalars(select(User).order_by(User.id)).all()


def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    data = user_in.model_dump(exclude_unset=True)
    password = data.pop("password", None)
    if password is not None:
        user.hashed_password = hash_password(password)
    for field, value in data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
