import logging

from app.enums import UserRole
from tests.conftest import create_task, get_user_id


def test_comment_emails_creator_and_assignee_in_background(client, register_user, caplog):
    manager = register_user("manager", UserRole.PROJECT_MANAGER)
    assignee = register_user("assignee")
    commenter = register_user("commenter")
    task_id = create_task(client, manager)
    client.post(f"/api/tasks/{task_id}/assign", json={"assignee_id": get_user_id(client, assignee)}, headers=manager)
    caplog.set_level(logging.INFO, logger="app.services.notifications")

    response = client.post(f"/api/tasks/{task_id}/comments", json={"content": "Looks good"}, headers=commenter)

    assert response.status_code == 201
    emailed = [record.args[0] for record in caplog.records if record.name == "app.services.notifications"]
    assert emailed == ["assignee@example.com", "manager@example.com"]


def test_comment_author_is_not_emailed(client, register_user, caplog):
    manager = register_user("owner", UserRole.PROJECT_MANAGER)
    task_id = create_task(client, manager)
    caplog.set_level(logging.INFO, logger="app.services.notifications")

    client.post(f"/api/tasks/{task_id}/comments", json={"content": "Note to self"}, headers=manager)

    assert [record for record in caplog.records if record.name == "app.services.notifications"] == []


def test_only_author_edits_comment_and_project_owner_can_delete_it(client, register_user):
    manager = register_user("lead", UserRole.PROJECT_MANAGER)
    author = register_user("writer")
    other = register_user("reader")
    task_id = create_task(client, manager)
    comment_id = client.post(
        f"/api/tasks/{task_id}/comments", json={"content": "First draft"}, headers=author
    ).json()["id"]
    comment_path = f"/api/tasks/{task_id}/comments/{comment_id}"

    assert client.patch(comment_path, json={"content": "Hacked"}, headers=other).status_code == 403
    assert client.delete(comment_path, headers=other).status_code == 403

    owner_edit = client.patch(comment_path, json={"content": "Rewritten"}, headers=manager)
    assert owner_edit.status_code == 403
    assert owner_edit.json()["detail"] == "Only the comment author can edit this comment"

    edited = client.patch(comment_path, json={"content": "Second draft"}, headers=author)
    assert edited.status_code == 200
    assert edited.json()["content"] == "Second draft"

    assert client.delete(comment_path, headers=manager).status_code == 204
    assert client.get(f"/api/tasks/{task_id}/comments", headers=author).json()["total"] == 0
