from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import user as user_crud
from app.database import get_db
from app.schemas.user import UserRead

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)):
    return user_crud.get_users(db)
