from datetime import datetime
from typing import Annotated

from pydantic import BeforeValidator, ConfigDict, EmailStr, Field, StringConstraints

from app.core.constants import (
    FULL_NAME_MAX_LENGTH,
    MIN_TEXT_LENGTH,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
    USERNAME_PATTERN,
)
from app.schemas.base import BaseSchema, UpdateSchema
from app.schemas.project import ProjectRead
from app.schemas.task import TaskRead

def normalize_username(value: object) -> object:
    return value.strip().lower() if isinstance(value, str) else value


Username = Annotated[
    str,
    StringConstraints(min_length=USERNAME_MIN_LENGTH, max_length=USERNAME_MAX_LENGTH, pattern=USERNAME_PATTERN),
    BeforeValidator(normalize_username),
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


class UserUpdate(UpdateSchema):
    non_nullable_fields = ("username", "email", "full_name", "password", "is_active")

    username: Username | None = None
    email: EmailStr | None = None
    full_name: FullName | None = None
    password: Password | None = None
    is_active: bool | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime


class UserProfile(UserRead):
    projects: list[ProjectRead]
    assigned_tasks: list[TaskRead]
