from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.enums import TaskPriority, TaskStatus


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: date | None
    project_id: int
    creator_id: int
    assignee_id: int | None
    created_at: datetime
