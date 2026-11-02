from app.crud import tag as tag_crud
from app.dependencies import DbSession
from app.routers.common import protected_router
from app.schemas.tag import TagRead

router = protected_router("/api/tags", "tags")


@router.get("", response_model=list[TagRead], summary="List tags")
def list_tags(db: DbSession) -> list[TagRead]:
    return [TagRead.model_validate(tag) for tag in tag_crud.get_tags(db)]
