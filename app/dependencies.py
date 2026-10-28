from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core import messages
from app.core.exceptions import ForbiddenException, NotFoundException, UnauthorizedException
from app.crud.common import get_or_raise
from app.database import get_db
from app.models import Project, Task, User
from app.security import decode_access_token

DbSession = Annotated[Session, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> User:
    subject = decode_access_token(token)
    user = db.get(User, int(subject)) if subject and subject.isdigit() else None
    if user is None:
        raise UnauthorizedException(messages.INVALID_TOKEN)
    if not user.is_active:
        raise ForbiddenException(messages.INACTIVE_USER)
    return user


def get_user_detail(user_id: int, db: DbSession) -> User:
    return get_or_raise(db, User, user_id, NotFoundException(messages.USER_NOT_FOUND))


def get_project_detail(project_id: int, db: DbSession) -> Project:
    return get_or_raise(db, Project, project_id, NotFoundException(messages.PROJECT_NOT_FOUND))


def get_task_detail(task_id: int, db: DbSession) -> Task:
    return get_or_raise(db, Task, task_id, NotFoundException(messages.TASK_NOT_FOUND))


CurrentUser = Annotated[User, Depends(get_current_user)]
UserDetail = Annotated[User, Depends(get_user_detail)]
ProjectDetail = Annotated[Project, Depends(get_project_detail)]
TaskDetail = Annotated[Task, Depends(get_task_detail)]
