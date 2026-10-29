from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core import messages
from app.core.constants import DEFAULT_PAGE_LIMIT, MAX_PAGE_LIMIT
from app.core.exceptions import ForbiddenException, NotFoundException, UnauthorizedException
from app.crud.common import get_or_raise
from app.database import get_db
from app.enums import UserRole
from app.models import Project, Task, User
from app.security import decode_access_token

DbSession = Annotated[Session, Depends(get_db)]
Skip = Annotated[int, Query(ge=0)]
Limit = Annotated[int, Query(ge=1, le=MAX_PAGE_LIMIT)]

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


ProjectManager = Annotated[User, Depends(verify_project_manager)]
UserDetail = Annotated[User, Depends(get_user_detail)]
ProjectDetail = Annotated[Project, Depends(get_project_detail)]
TaskDetail = Annotated[Task, Depends(get_task_detail)]


def get_managed_project(project: ProjectDetail, current_user: CurrentUser) -> Project:
    if current_user.role != UserRole.ADMIN and project.owner_id != current_user.id:
        raise ForbiddenException(messages.PROJECT_PERMISSION_DENIED)
    return project


ManagedProject = Annotated[Project, Depends(get_managed_project)]
