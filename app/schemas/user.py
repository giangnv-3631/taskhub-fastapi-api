from datetime import datetime
from typing import Annotated

from pydantic import ConfigDict, EmailStr, Field, StringConstraints

from app.core.constants import (
    FULL_NAME_MAX_LENGTH,
    MIN_TEXT_LENGTH,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
)
from app.schemas.base import BaseSchema, UpdateSchema

FullName = Annotated[str, Field(min_length=MIN_TEXT_LENGTH, max_length=FULL_NAME_MAX_LENGTH)]
Password = Annotated[
    str,
    StringConstraints(strip_whitespace=False, min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH),
]


class UserBase(BaseSchema):
    email: EmailStr
    full_name: FullName


class UserCreate(UserBase):
    password: Password


class UserUpdate(UpdateSchema):
    non_nullable_fields = ("email", "full_name", "password", "is_active")

    email: EmailStr | None = None
    full_name: FullName | None = None
    password: Password | None = None
    is_active: bool | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
