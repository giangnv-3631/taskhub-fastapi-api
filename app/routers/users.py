from fastapi import APIRouter

from app.crud import user as user_crud
from app.dependencies import DbSession
from app.schemas.user import UserRead

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserRead], summary="List users")
def list_users(db: DbSession) -> list[UserRead]:
    return user_crud.get_users(db)
