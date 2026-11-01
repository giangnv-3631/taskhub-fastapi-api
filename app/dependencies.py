from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core import messages
from app.core.exceptions import ForbiddenException, NotFoundException, UnauthorizedException
from app.crud.common import get_or_raise
from app.database import get_db
from app.enums import UserRole
from app.models import Comment, Project, Task, User
from app.schemas.pagination import PaginationParams
from app.schemas.task import TaskFilterParams
from app.security import decode_access_token

DbSession = Annotated[Session, Depends(get_db)]
PaginationDep = Annotated[PaginationParams, Query()]
TaskFilterDep = Annotated[TaskFilterParams, Query()]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> User:
    subject = decode_access_token(token)
    user = db.get(User, int(subject)) if subject and subject.isdigit() else None
    if user is None:
        raise UnauthorizedException(messages.INVALID_TOKEN)
    return user


def get_current_active_user(user: Annotated[User, Depends(get_current_user)]) -> User:
    if not user.is_active:
        raise ForbiddenException(messages.INACTIVE_USER)
    return user


CurrentUser = Annotated[User, Depends(get_current_active_user)]


def verify_admin_role(current_user: CurrentUser) -> User:
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException(messages.ADMIN_ROLE_REQUIRED)
    return current_user


def verify_project_manager(current_user: CurrentUser) -> User:
    if current_user.role not in (UserRole.ADMIN, UserRole.PROJECT_MANAGER):
        raise ForbiddenException(messages.PROJECT_MANAGER_ROLE_REQUIRED)
    return current_user


def get_user_detail(user_id: int, db: DbSession) -> User:
    return get_or_raise(db, User, user_id, NotFoundException(messages.USER_NOT_FOUND))


def get_project_detail(project_id: int, db: DbSession) -> Project:
    return get_or_raise(db, Project, project_id, NotFoundException(messages.PROJECT_NOT_FOUND))


def get_task_detail(task_id: int, db: DbSession) -> Task:
    return get_or_raise(db, Task, task_id, NotFoundException(messages.TASK_NOT_FOUND))


AdminUser = Annotated[User, Depends(verify_admin_role)]
ProjectManager = Annotated[User, Depends(verify_project_manager)]
UserDetail = Annotated[User, Depends(get_user_detail)]
ProjectDetail = Annotated[Project, Depends(get_project_detail)]
TaskDetail = Annotated[Task, Depends(get_task_detail)]


def can_manage_project(project: Project, user: User) -> bool:
    return user.role == UserRole.ADMIN or project.owner_id == user.id


def ensure_can_manage_project(project: Project, user: User) -> None:
    if not can_manage_project(project, user):
        raise ForbiddenException(messages.PROJECT_PERMISSION_DENIED)


def get_managed_project(project: ProjectDetail, current_user: CurrentUser) -> Project:
    ensure_can_manage_project(project, current_user)
    return project


def get_managed_task(task: TaskDetail, current_user: CurrentUser) -> Task:
    ensure_can_manage_project(task.project, current_user)
    return task


ManagedProject = Annotated[Project, Depends(get_managed_project)]
ManagedTask = Annotated[Task, Depends(get_managed_task)]


def get_comment_detail(comment_id: int, task: TaskDetail, db: DbSession) -> Comment:
    comment = db.get(Comment, comment_id)
    if comment is None or comment.task_id != task.id:
        raise NotFoundException(messages.COMMENT_NOT_FOUND)
    return comment


CommentDetail = Annotated[Comment, Depends(get_comment_detail)]


def get_managed_comment(comment: CommentDetail, current_user: CurrentUser) -> Comment:
    if comment.author_id != current_user.id and not can_manage_project(comment.task.project, current_user):
        raise ForbiddenException(messages.COMMENT_PERMISSION_DENIED)
    return comment


ManagedComment = Annotated[Comment, Depends(get_managed_comment)]
