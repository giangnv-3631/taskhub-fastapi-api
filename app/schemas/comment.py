from datetime import datetime
from typing import Annotated

from pydantic import ConfigDict, Field

from app.core.constants import COMMENT_MAX_LENGTH, MIN_TEXT_LENGTH
from app.schemas.base import BaseSchema, UpdateSchema

CommentContent = Annotated[str, Field(min_length=MIN_TEXT_LENGTH, max_length=COMMENT_MAX_LENGTH)]


class CommentCreate(BaseSchema):
    content: CommentContent


class CommentUpdate(UpdateSchema):
    non_nullable_fields = ("content",)

    content: CommentContent | None = None


class CommentRead(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    task_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
