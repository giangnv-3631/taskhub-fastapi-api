from http import HTTPStatus
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class AppException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    headers: dict[str, str] | None = None

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class BadRequestException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST


class UnauthorizedException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    headers = {"WWW-Authenticate": "Bearer"}


class ForbiddenException(AppException):
    status_code = status.HTTP_403_FORBIDDEN


class NotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND


class ConflictException(AppException):
    status_code = status.HTTP_409_CONFLICT


class ErrorResponse(BaseModel):
    detail: str


def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message}, headers=exc.headers)


def error_responses(*exceptions: type[AppException]) -> dict[int | str, dict[str, Any]]:
    return {
        exc.status_code: {"model": ErrorResponse, "description": HTTPStatus(exc.status_code).phrase}
        for exc in exceptions
    }
