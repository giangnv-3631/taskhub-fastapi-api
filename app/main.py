from fastapi import FastAPI
from sqlalchemy import text

from app.dependencies import DbSession
from app.routers import projects, tags, tasks, users

app = FastAPI(title="TaskHub API")

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(tags.router)


@app.get("/health")
def health(db: DbSession):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
