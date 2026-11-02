from datetime import datetime
from typing import Annotated

from pydantic import BeforeValidator, ConfigDict, EmailStr, Field, StringConstraints

from app.core.constants import (
    FULL_NAME_MAX_LENGTH,
    MIN_TEXT_LENGTH,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    TOKEN_TYPE_BEARER,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
    USERNAME_PATTERN,
)
from app.enums import UserRole
from app.schemas.base import BaseSchema, normalize_lowercase
from app.schemas.project import ProjectRead
from app.schemas.task import TaskRead


Username = Annotated[
    str,
    StringConstraints(min_length=USERNAME_MIN_LENGTH, max_length=USERNAME_MAX_LENGTH, pattern=USERNAME_PATTERN),
    BeforeValidator(normalize_lowercase),
]
FullName = Annotated[str, Field(min_length=MIN_TEXT_LENGTH, max_length=FULL_NAME_MAX_LENGTH)]
Password = Annotated[
    str,
    StringConstraints(strip_whitespace=False, min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH),
]


class UserBase(BaseSchema):
    username: Username
    email: EmailStr
    full_name: FullName


class UserCreate(UserBase):
    password: Password


class UserMeUpdate(UserBase):
    pass


class Token(BaseSchema):
    access_token: str
    token_type: str = TOKEN_TYPE_BEARER


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: UserRole
    is_active: bool
    created_at: datetime


class UserProfile(UserRead):
    projects: list[ProjectRead]
    assigned_tasks: list[TaskRead]
