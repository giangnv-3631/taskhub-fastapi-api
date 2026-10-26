from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.crud import user as user_crud
from app.dependencies import DbSession
from app.models import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/api/users", tags=["users"])


def get_user_or_404(db: DbSession, user_id: int) -> User:
    user = user_crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def ensure_email_available(db: DbSession, email: str) -> None:
    if user_crud.get_user_by_email(db, email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")


@router.get("", response_model=list[UserRead], summary="List users")
def list_users(db: DbSession) -> list[UserRead]:
    return [UserRead.model_validate(user) for user in user_crud.get_users(db)]


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED, summary="Create user")
def create_user(user_in: UserCreate, db: DbSession) -> UserRead:
    ensure_email_available(db, user_in.email)
    return UserRead.model_validate(user_crud.create_user(db, user_in))


@router.get("/{user_id}", response_model=UserRead, summary="Get user")
def read_user(user_id: int, db: DbSession) -> UserRead:
    return UserRead.model_validate(get_user_or_404(db, user_id))


@router.patch("/{user_id}", response_model=UserRead, summary="Update user")
def update_user(user_id: int, user_in: UserUpdate, db: DbSession) -> UserRead:
    user = get_user_or_404(db, user_id)
    if user_in.email is not None and user_in.email != user.email:
        ensure_email_available(db, user_in.email)
    return UserRead.model_validate(user_crud.update_user(db, user, user_in))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user")
def delete_user(user_id: int, db: DbSession) -> None:
    user = get_user_or_404(db, user_id)
    try:
        user_crud.delete_user(db, user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User still owns projects, tasks or comments",
        )
