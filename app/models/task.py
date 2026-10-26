from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import TaskPriority, TaskStatus
from app.models.tag import task_tags

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.project import Project
    from app.models.tag import Tag
    from app.models.user import User


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, native_enum=False, length=20, values_callable=lambda e: [m.value for m in e]),
        default=TaskStatus.TODO,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, native_enum=False, length=20, values_callable=lambda e: [m.value for m in e]),
        default=TaskPriority.MEDIUM,
    )
    due_date: Mapped[date | None] = mapped_column(Date)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["Project"] = relationship(back_populates="tasks")
    creator: Mapped["User"] = relationship(back_populates="created_tasks", foreign_keys=[creator_id])
    assignee: Mapped["User | None"] = relationship(back_populates="assigned_tasks", foreign_keys=[assignee_id])
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="task", cascade="all, delete", passive_deletes=True
    )
    tags: Mapped[list["Tag"]] = relationship(secondary=task_tags, back_populates="tasks")
