from fastapi import APIRouter, status

from app.core.exceptions import ConflictException, NotFoundException, error_responses
from app.crud import user as user_crud
from app.dependencies import DbSession, UserDetail
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserRead], summary="List users")
def list_users(db: DbSession) -> list[UserRead]:
    return [UserRead.model_validate(user) for user in user_crud.get_users(db)]


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    responses=error_responses(ConflictException),
)
def create_user(user_in: UserCreate, db: DbSession) -> UserRead:
    return UserRead.model_validate(user_crud.create_user(db, user_in))


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get user",
    responses=error_responses(NotFoundException),
)
def read_user(user: UserDetail) -> UserRead:
    return UserRead.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Update user",
    responses=error_responses(NotFoundException, ConflictException),
)
def update_user(user_in: UserUpdate, user: UserDetail, db: DbSession) -> UserRead:
    return UserRead.model_validate(user_crud.update_user(db, user, user_in))


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    responses=error_responses(NotFoundException, ConflictException),
)
def delete_user(user: UserDetail, db: DbSession) -> None:
    user_crud.delete_user(db, user)
