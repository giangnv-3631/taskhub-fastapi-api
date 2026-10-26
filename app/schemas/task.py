from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.enums import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: date | None = None
    assignee_id: int | None = None


class TaskCreate(TaskBase):
    project_id: int
    creator_id: int


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None
    assignee_id: int | None = None

    @model_validator(mode="after")
    def reject_null_for_required_fields(self) -> "TaskUpdate":
        for field in ("title", "status", "priority"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    creator_id: int
    created_at: datetime
