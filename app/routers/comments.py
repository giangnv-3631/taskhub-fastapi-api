from fastapi import status

from app.core.exceptions import NotFoundException, error_responses
from app.crud import comment as comment_crud
from app.dependencies import CurrentUser, DbSession, ManagedComment, PaginationDep, TaskDetail
from app.routers.common import protected_router
from app.schemas.comment import CommentCreate, CommentRead, CommentUpdate
from app.schemas.pagination import Page

router = protected_router("/api/tasks/{task_id}/comments", "comments")


@router.get(
    "",
    response_model=Page[CommentRead],
    summary="List comments of task",
    responses=error_responses(NotFoundException),
)
def list_comments(task: TaskDetail, pagination: PaginationDep, db: DbSession) -> Page[CommentRead]:
    comments, total = comment_crud.get_task_comments(db, task.id, pagination)
    return Page[CommentRead](items=comments, total=total)


@router.post(
    "",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add comment to task",
    responses=error_responses(NotFoundException),
)
def create_comment(
    comment_in: CommentCreate, task: TaskDetail, current_user: CurrentUser, db: DbSession
) -> CommentRead:
    return CommentRead.model_validate(comment_crud.create_comment(db, task, current_user, comment_in))


@router.patch(
    "/{comment_id}",
    response_model=CommentRead,
    summary="Update comment",
    responses=error_responses(NotFoundException),
)
def update_comment(comment_in: CommentUpdate, comment: ManagedComment, db: DbSession) -> CommentRead:
    return CommentRead.model_validate(comment_crud.update_comment(db, comment, comment_in))


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete comment",
    responses=error_responses(NotFoundException),
)
def delete_comment(comment: ManagedComment, db: DbSession) -> None:
    comment_crud.delete_comment(db, comment)
