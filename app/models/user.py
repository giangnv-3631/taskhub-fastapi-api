from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import EMAIL_MAX_LENGTH, FULL_NAME_MAX_LENGTH, HASHED_PASSWORD_MAX_LENGTH, USERNAME_MAX_LENGTH
from app.database import Base

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.project import Project
    from app.models.task import Task


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(USERNAME_MAX_LENGTH), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(EMAIL_MAX_LENGTH), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(FULL_NAME_MAX_LENGTH))
    hashed_password: Mapped[str] = mapped_column(String(HASHED_PASSWORD_MAX_LENGTH))
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    projects: Mapped[list["Project"]] = relationship(back_populates="owner")
    created_tasks: Mapped[list["Task"]] = relationship(back_populates="creator", foreign_keys="Task.creator_id")
    assigned_tasks: Mapped[list["Task"]] = relationship(back_populates="assignee", foreign_keys="Task.assignee_id")
    comments: Mapped[list["Comment"]] = relationship(back_populates="author")
