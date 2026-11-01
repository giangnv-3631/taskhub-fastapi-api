from datetime import datetime
from typing import Annotated

from pydantic import ConfigDict, Field

from app.core.constants import MIN_TEXT_LENGTH, PROJECT_NAME_MAX_LENGTH
from app.schemas.base import BaseSchema, UpdateSchema

ProjectName = Annotated[str, Field(min_length=MIN_TEXT_LENGTH, max_length=PROJECT_NAME_MAX_LENGTH)]


class ProjectBase(BaseSchema):
    name: ProjectName
    description: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(UpdateSchema):
    non_nullable_fields = ("name",)

    name: ProjectName | None = None
    description: str | None = None


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime
