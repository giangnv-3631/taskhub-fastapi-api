from fastapi import APIRouter, Depends

from app.core.exceptions import ForbiddenException, UnauthorizedException, error_responses
from app.dependencies import get_current_user


def protected_router(prefix: str, tag: str) -> APIRouter:
    return APIRouter(
        prefix=prefix,
        tags=[tag],
        dependencies=[Depends(get_current_user)],
        responses=error_responses(UnauthorizedException, ForbiddenException),
    )
