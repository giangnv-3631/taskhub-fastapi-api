from app.config import settings
from app.enums import UserRole
from tests.conftest import TEST_PASSWORD, get_user_id


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


def test_admin_cannot_delete_self(client, register_user):
    admin = register_user("root", UserRole.ADMIN)
    member = register_user("frank")
    admin_id = get_user_id(client, admin)

    response = client.delete(f"/api/users/{admin_id}", headers=admin)
    assert response.status_code == 403
    assert response.json()["detail"] == "You cannot delete your own account"

    assert client.delete(f"/api/users/{admin_id}", headers=member).status_code == 403
    assert client.delete(f"/api/users/{get_user_id(client, member)}", headers=admin).status_code == 204


def test_cors_preflight_allows_configured_origin(client):
    origin = settings.cors_origins[0]

    response = client.options(
        "/api/tasks",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin


def test_cors_rejects_unknown_origin(client):
    response = client.options(
        "/api/tasks",
        headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "GET"},
    )

    assert "access-control-allow-origin" not in response.headers
