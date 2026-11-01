from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.common import paginate
from app.models import Comment, Task, User
from app.schemas.comment import CommentCreate, CommentUpdate
from app.schemas.pagination import PaginationParams


def get_task_comments(db: Session, task_id: int, pagination: PaginationParams):
    statement = select(Comment).where(Comment.task_id == task_id).order_by(Comment.id)
    return paginate(db, statement, pagination)


def create_comment(db: Session, task: Task, author: User, comment_in: CommentCreate) -> Comment:
    comment = Comment(**comment_in.model_dump(), task=task, author=author)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def update_comment(db: Session, comment: Comment, comment_in: CommentUpdate) -> Comment:
    for field, value in comment_in.model_dump(exclude_unset=True).items():
        setattr(comment, field, value)
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment: Comment) -> None:
    db.delete(comment)
    db.commit()
