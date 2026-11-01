from typing import Generic, TypeVar

from pydantic import Field

from app.core.constants import DEFAULT_PAGE_LIMIT, MAX_PAGE_LIMIT
from app.schemas.base import BaseSchema

ItemT = TypeVar("ItemT")


class PaginationParams(BaseSchema):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=DEFAULT_PAGE_LIMIT, ge=1, le=MAX_PAGE_LIMIT)


class Page(BaseSchema, Generic[ItemT]):
    items: list[ItemT]
    total: int
