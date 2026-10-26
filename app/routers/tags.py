from fastapi import APIRouter

from app.crud import tag as tag_crud
from app.dependencies import DbSession
from app.schemas.tag import TagRead

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=list[TagRead], summary="List tags")
def list_tags(db: DbSession) -> list[TagRead]:
    return [TagRead.model_validate(tag) for tag in tag_crud.get_tags(db)]
