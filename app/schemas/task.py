from datetime import date, datetime
from typing import Annotated

from pydantic import ConfigDict, Field, PositiveInt, field_validator

from app.core import messages
from app.core.constants import MIN_TEXT_LENGTH, TASK_TITLE_MAX_LENGTH
from app.enums import TaskPriority, TaskStatus
from app.schemas.base import BaseSchema, UpdateSchema

TaskTitle = Annotated[str, Field(min_length=MIN_TEXT_LENGTH, max_length=TASK_TITLE_MAX_LENGTH)]


class TaskBase(BaseSchema):
    title: TaskTitle
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: date | None = None
    assignee_id: PositiveInt | None = None


class TaskCreate(TaskBase):
    project_id: PositiveInt
    creator_id: PositiveInt

    @field_validator("due_date")
    @classmethod
    def reject_past_due_date(cls, value: date | None) -> date | None:
        if value is not None and value < date.today():
            raise ValueError(messages.DUE_DATE_IN_PAST)
        return value


class TaskUpdate(UpdateSchema):
    non_nullable_fields = ("title", "status", "priority")

    title: TaskTitle | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None
    assignee_id: PositiveInt | None = None


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: TaskStatus
    project_id: int
    creator_id: int
    created_at: datetime
