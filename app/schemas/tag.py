from typing import Annotated

from pydantic import ConfigDict, Field

from app.core.constants import MIN_TEXT_LENGTH, TAG_NAME_MAX_LENGTH
from app.schemas.base import BaseSchema, UpdateSchema

TagName = Annotated[str, Field(min_length=MIN_TEXT_LENGTH, max_length=TAG_NAME_MAX_LENGTH)]


class TagBase(BaseSchema):
    name: TagName


class TagCreate(TagBase):
    pass


class TagUpdate(UpdateSchema):
    non_nullable_fields = ("name",)

    name: TagName | None = None


class TagRead(TagBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
