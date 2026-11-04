import os

os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only-0123456789"
os.environ["SMTP_HOST"] = ""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text, update
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, get_db
from app.enums import UserRole
from app.main import app
from app.models import User

TEST_PASSWORD = "secret123"
DATABASE_URL = make_url(settings.database_url)
TEST_DATABASE_URL = DATABASE_URL.set(database=f"{DATABASE_URL.database}_test")


def ensure_test_database() -> None:
    admin_engine = create_engine(DATABASE_URL.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        exists = connection.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": TEST_DATABASE_URL.database}
        )
        if not exists:
            connection.execute(text(f'CREATE DATABASE "{TEST_DATABASE_URL.database}"'))
    admin_engine.dispose()


@pytest.fixture(scope="session")
def test_engine():
    ensure_test_database()
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, autoflush=False, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def create_project(client, headers: dict[str, str]) -> int:
    return client.post("/api/projects", json={"name": "Website"}, headers=headers).json()["id"]


def create_task(client, headers: dict[str, str]) -> int:
    project_id = create_project(client, headers)
    return client.post(f"/api/projects/{project_id}/tasks", json={"title": "Homepage"}, headers=headers).json()["id"]


def get_user_id(client, headers: dict[str, str]) -> int:
    return client.get("/api/users/me", headers=headers).json()["id"]


@pytest.fixture
def register_user(client, db_session):
    def register(username: str, role: UserRole = UserRole.MEMBER) -> dict[str, str]:
        response = client.post(
            "/api/users/register",
            json={
                "username": username,
                "email": f"{username}@example.com",
                "full_name": username,
                "password": TEST_PASSWORD,
            },
        )
        assert response.status_code == 201
        if role != UserRole.MEMBER:
            db_session.execute(update(User).where(User.username == username).values(role=role))
            db_session.commit()
        login = client.post("/api/users/login", data={"username": username, "password": TEST_PASSWORD})
        return {"Authorization": f"Bearer {login.json()['access_token']}"}

    return register
