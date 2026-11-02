from app.enums import UserRole
from tests.conftest import TEST_PASSWORD


def test_register_login_and_create_task(client, register_user):
    headers = register_user("alice", UserRole.PROJECT_MANAGER)
    me = client.get("/api/users/me", headers=headers).json()

    project = client.post("/api/projects", json={"name": "Website"}, headers=headers)
    assert project.status_code == 201
    project_id = project.json()["id"]

    task = client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "Design homepage", "priority": "high"},
        headers=headers,
    )
    assert task.status_code == 201
    assert task.json()["creator_id"] == me["id"]
    assert task.json()["status"] == "todo"

    tasks = client.get(f"/api/projects/{project_id}/tasks", headers=headers)
    assert tasks.status_code == 200
    assert tasks.json()["total"] == 1
    assert tasks.json()["items"][0]["title"] == "Design homepage"


def test_register_normalizes_username_and_rejects_duplicate(client):
    body = {"username": " Bob ", "email": "bob@example.com", "full_name": "Bob", "password": TEST_PASSWORD}

    response = client.post("/api/users/register", json=body)
    assert response.status_code == 201
    assert response.json()["username"] == "bob"
    assert response.json()["role"] == "member"
    assert "password" not in response.json()
    assert "hashed_password" not in response.json()

    duplicate = client.post("/api/users/register", json={**body, "username": "BOB", "email": "other@example.com"})
    assert duplicate.status_code == 409


def test_login_with_wrong_password_returns_401(client, register_user):
    register_user("carol")

    response = client.post("/api/users/login", data={"username": "carol", "password": "wrong-password"})

    assert response.status_code == 401


def test_create_project_without_token_returns_401(client):
    response = client.post("/api/projects", json={"name": "Website"})

    assert response.status_code == 401


def test_member_cannot_create_project_or_task(client, register_user):
    manager = register_user("dave", UserRole.PROJECT_MANAGER)
    member = register_user("erin")
    project_id = client.post("/api/projects", json={"name": "Website"}, headers=manager).json()["id"]

    assert client.post("/api/projects", json={"name": "Mine"}, headers=member).status_code == 403
    assert client.post(f"/api/projects/{project_id}/tasks", json={"title": "x"}, headers=member).status_code == 403
