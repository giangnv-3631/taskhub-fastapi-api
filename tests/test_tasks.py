from app.enums import UserRole
from tests.conftest import create_project, create_task, get_user_id


def test_register_login_and_create_task(client, register_user):
    headers = register_user("alice", UserRole.PROJECT_MANAGER)
    me = client.get("/api/users/me", headers=headers).json()
    project_id = create_project(client, headers)

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


def test_member_cannot_create_project_or_task(client, register_user):
    manager = register_user("dave", UserRole.PROJECT_MANAGER)
    member = register_user("erin")
    project_id = create_project(client, manager)

    assert client.post("/api/projects", json={"name": "Mine"}, headers=member).status_code == 403
    assert client.post(f"/api/projects/{project_id}/tasks", json={"title": "x"}, headers=member).status_code == 403


def test_owner_assigns_and_unassigns_task(client, register_user):
    manager = register_user("grace", UserRole.PROJECT_MANAGER)
    member = register_user("heidi")
    member_id = get_user_id(client, member)
    assign_path = f"/api/tasks/{create_task(client, manager)}/assign"

    assert client.post(assign_path, json={"assignee_id": member_id}, headers=member).status_code == 403
    assert client.post(assign_path, json={"assignee_id": 999999}, headers=manager).status_code == 400

    assigned = client.post(assign_path, json={"assignee_id": member_id}, headers=manager)
    assert assigned.status_code == 200
    assert assigned.json()["assignee_id"] == member_id

    unassigned = client.post(assign_path, json={"assignee_id": None}, headers=manager)
    assert unassigned.status_code == 200
    assert unassigned.json()["assignee_id"] is None


def test_assignee_updates_own_task_but_cannot_delete_it(client, register_user):
    manager = register_user("ivan", UserRole.PROJECT_MANAGER)
    assignee = register_user("judy")
    other = register_user("mallory")
    task_id = create_task(client, manager)
    client.post(f"/api/tasks/{task_id}/assign", json={"assignee_id": get_user_id(client, assignee)}, headers=manager)
    task_path = f"/api/tasks/{task_id}"

    updated = client.patch(task_path, json={"status": "in_progress"}, headers=assignee)
    assert updated.status_code == 200
    assert updated.json()["status"] == "in_progress"

    assert client.patch(task_path, json={"status": "done"}, headers=other).status_code == 403
    assert client.delete(task_path, headers=assignee).status_code == 403


def test_filter_and_paginate_tasks_return_total(client, register_user):
    manager = register_user("oscar", UserRole.PROJECT_MANAGER)
    project_id = create_project(client, manager)
    task_ids = [
        client.post(
            f"/api/projects/{project_id}/tasks", json={"title": title, "priority": priority}, headers=manager
        ).json()["id"]
        for title, priority in (("A", "high"), ("B", "high"), ("C", "low"))
    ]
    client.patch(f"/api/tasks/{task_ids[1]}", json={"status": "done"}, headers=manager)

    filtered = client.get("/api/tasks", params={"status": "TODO", "priority": "HIGH"}, headers=manager)
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert [task["id"] for task in filtered.json()["items"]] == [task_ids[0]]

    page = client.get(f"/api/projects/{project_id}/tasks", params={"skip": 1, "limit": 1}, headers=manager)
    assert page.json()["total"] == 3
    assert [task["id"] for task in page.json()["items"]] == [task_ids[1]]


def test_bookmark_same_task_twice_returns_409(client, register_user):
    manager = register_user("peggy", UserRole.PROJECT_MANAGER)
    member = register_user("trent")
    bookmark_path = f"/api/tasks/{create_task(client, manager)}/bookmark"

    first = client.post(bookmark_path, headers=member)
    assert first.status_code == 201
    assert first.json()["user_id"] == get_user_id(client, member)

    duplicate = client.post(bookmark_path, headers=member)
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Task already bookmarked"
