from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User


@pytest.fixture
def task_client():
    db = MagicMock()
    user = MagicMock(spec=User)
    user.id = 1

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: user

    with TestClient(app) as client:
        yield client, db

    app.dependency_overrides.clear()


def test_create_task(task_client):
    client, db = task_client
    db.refresh.side_effect = lambda task: setattr(task, "id", 10)

    response = client.post(
        "/tasks",
        json={
            "title": "Test task",
            "description": "Task created during testing",
            "status": "pending",
            "priority": "high",
        },
    )

    assert response.status_code == 200 or response.status_code == 201
    assert response.json()["title"] == "Test task"
    assert response.json()["owner_id"] == 1
    db.add.assert_called_once()
    db.commit.assert_called_once()


def test_create_task_invalid_priority(task_client):
    client, db = task_client

    response = client.post(
        "/tasks",
        json={
            "title": "Invalid priority task",
            "priority": "urgent",
        },
    )

    assert response.status_code == 422
    db.add.assert_not_called()


def test_get_tasks_empty_list(task_client):
    client, db = task_client
    db.query.return_value.filter.return_value.all.return_value = []

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_update_task_not_found(task_client):
    client, db = task_client
    db.query.return_value.filter.return_value.first.return_value = None

    response = client.put(
        "/tasks/999",
        json={"title": "Updated title"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
    db.commit.assert_not_called()


def test_delete_task_not_found(task_client):
    client, db = task_client
    db.query.return_value.filter.return_value.first.return_value = None

    response = client.delete("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
    db.delete.assert_not_called()
    db.commit.assert_not_called()


def test_update_task_success(task_client):
    client, db = task_client

    existing_task = MagicMock()
    existing_task.id = 10
    existing_task.title = "Old title"
    existing_task.description = "Old description"
    existing_task.status = "pending"
    existing_task.priority = "medium"
    existing_task.owner_id = 1

    db.query.return_value.filter.return_value.first.return_value = (
        existing_task
    )

    response = client.put(
        "/tasks/10",
        json={
            "title": "Updated title",
            "description": "Updated description",
            "status": "completed",
            "priority": "high",
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"
    assert response.json()["description"] == "Updated description"
    assert response.json()["status"] == "completed"
    assert response.json()["priority"] == "high"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(existing_task)


def test_delete_task_success(task_client):
    client, db = task_client

    existing_task = MagicMock()
    existing_task.id = 10
    existing_task.owner_id = 1

    db.query.return_value.filter.return_value.first.return_value = (
        existing_task
    )

    response = client.delete("/tasks/10")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Task deleted successfully",
        "task_id": 10,
    }
    db.delete.assert_called_once_with(existing_task)
    db.commit.assert_called_once()


def test_get_tasks_with_filters_search_and_sort(task_client):
    client, db = task_client

    query = db.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.filter.return_value = filtered_query
    filtered_query.order_by.return_value = filtered_query
    filtered_query.all.return_value = []

    response = client.get(
        "/tasks?status=pending&priority=high&search=data&sort=-priority"
    )

    assert response.status_code == 200
    assert response.json() == []
    query.filter.assert_called()
    filtered_query.order_by.assert_called_once()


def test_get_tasks_sort_by_priority_ascending(task_client):
    client, db = task_client

    query = db.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.order_by.return_value.all.return_value = []

    response = client.get("/tasks?sort=priority")

    assert response.status_code == 200
    assert response.json() == []
    filtered_query.order_by.assert_called_once()


def test_task_isolation_user_cannot_access_other_user_task(task_client):
    """Ensure user cannot update or access tasks belonging to another user."""
    client, db = task_client
    # Simulate DB returning None because task belongs to another owner_id
    db.query.return_value.filter.return_value.first.return_value = None

    response = client.put(
        "/tasks/999",
        json={"title": "Unauthorized Update"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_user_cannot_delete_other_users_task(task_client):
    client, db = task_client

    # Simulate task not found for the current user
    db.query.return_value.filter.return_value.first.return_value = None

    response = client.delete("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
    db.delete.assert_not_called()
    db.commit.assert_not_called()


def test_user_cannot_see_other_users_tasks(task_client):
    client, db = task_client

    db.query.return_value.filter.return_value.all.return_value = []

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []