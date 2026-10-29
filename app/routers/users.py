from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    error_responses,
)
from app.crud import user as user_crud
from app.dependencies import CurrentUser, DbSession, UserDetail
from app.routers.common import protected_router
from app.schemas.user import Token, UserCreate, UserMeUpdate, UserProfile, UserRead, Username
from app.security import create_access_token

auth_router = APIRouter(prefix="/api/users", tags=["users"])
router = protected_router("/api/users", "users")


@auth_router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register",
    responses=error_responses(ConflictException),
)
def register(user_in: UserCreate, db: DbSession) -> UserRead:
    return UserRead.model_validate(user_crud.create_user(db, user_in))


@auth_router.post(
    "/login",
    response_model=Token,
    summary="Login",
    responses=error_responses(UnauthorizedException, ForbiddenException),
)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession) -> Token:
    user = user_crud.authenticate_user(db, form_data.username, form_data.password)
    return Token(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=UserRead, summary="Get current user")
def read_me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserRead,
    summary="Update current user",
    responses=error_responses(ConflictException),
)
def update_me(user_in: UserMeUpdate, current_user: CurrentUser, db: DbSession) -> UserRead:
    return UserRead.model_validate(user_crud.update_user(db, current_user, user_in))


@router.get("", response_model=list[UserRead], summary="List users")
def list_users(db: DbSession) -> list[UserRead]:
    return [UserRead.model_validate(user) for user in user_crud.get_users(db)]


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get user",
    responses=error_responses(NotFoundException),
)
def read_user(user: UserDetail) -> UserRead:
    return UserRead.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    responses=error_responses(NotFoundException, ConflictException),
)
def delete_user(user: UserDetail, db: DbSession) -> None:
    user_crud.delete_user(db, user)


@router.get(
    "/{username}/profile",
    response_model=UserProfile,
    summary="Get user profile",
    responses=error_responses(NotFoundException),
)
def read_user_profile(username: Username, db: DbSession) -> UserProfile:
    return UserProfile.model_validate(user_crud.get_user_profile(db, username))
