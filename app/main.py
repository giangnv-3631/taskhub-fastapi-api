import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.core.constants import LOG_FORMAT
from app.core.exceptions import AppException, app_exception_handler, unhandled_exception_handler
from app.dependencies import DbSession
from app.routers import comments, projects, tags, tasks, users

logging.basicConfig(level=settings.log_level, format=LOG_FORMAT)

app = FastAPI(title="TaskHub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(users.auth_router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(tasks.project_tasks_router)
app.include_router(comments.router)
app.include_router(tags.router)


@app.get("/health", summary="Health check")
def health(db: DbSession) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
