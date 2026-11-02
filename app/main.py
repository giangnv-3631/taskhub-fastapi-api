from fastapi import FastAPI
from sqlalchemy import text

from app.core.exceptions import AppException, app_exception_handler
from app.dependencies import DbSession
from app.routers import projects, tags, tasks, users

app = FastAPI(title="TaskHub API")

app.add_exception_handler(AppException, app_exception_handler)

app.include_router(users.auth_router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(tasks.project_tasks_router)
app.include_router(tags.router)


@app.get("/health")
def health(db: DbSession):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
