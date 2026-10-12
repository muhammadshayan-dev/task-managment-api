import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app import models
from app.dependencies import get_current_user
from app.main import app
from app.models import User
from app.security import create_access_token


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/taskdb_test",
)

if not TEST_DATABASE_URL.rstrip("/").endswith("taskdb_test"):
    raise RuntimeError(
        "Ownership tests must use the taskdb_test database."
    )

test_engine = create_engine(TEST_DATABASE_URL)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture
def clean_test_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def ownership_setup(clean_test_database):
    db = TestSessionLocal()

    user_a = User(
        email="owner_a@example.com",
        full_name="Owner A",
        hashed_password="test-hash-a",
    )
    user_b = User(
        email="owner_b@example.com",
        full_name="Owner B",
        hashed_password="test-hash-b",
    )

    db.add_all([user_a, user_b])
    db.commit()
    db.refresh(user_a)
    db.refresh(user_b)

    token_a = create_access_token(user_a.id)
    token_b = create_access_token(user_b.id)

    app.dependency_overrides[get_db] = lambda: db

    try:
        with TestClient(app) as client:
            yield (
                client,
                db,
                user_a,
                {
                    "Authorization": f"Bearer {token_a}"
                },
                {
                    "Authorization": f"Bearer {token_b}"
                },
            )
    finally:
        app.dependency_overrides.clear()
        db.close()


@pytest.fixture
def task_owned_by_a(ownership_setup):
    client, db, user_a, headers_a, headers_b = ownership_setup

    response = client.post(
        "/tasks/",
        headers=headers_a,
        json={
            "title": "Owner A private task",
            "description": "Ownership integration test",
            "status": "pending",
            "priority": "high",
        },
    )

    assert response.status_code == 200, response.text

    return (
        client,
        db,
        response.json()["id"],
        headers_a,
        headers_b,
    )


def test_owner_can_see_own_task(task_owned_by_a):
    client, db, task_id, headers_a, headers_b = task_owned_by_a

    response = client.get("/tasks/", headers=headers_a)

    assert response.status_code == 200
    assert any(task["id"] == task_id for task in response.json())


def test_other_user_cannot_see_task(task_owned_by_a):
    client, db, task_id, headers_a, headers_b = task_owned_by_a

    response = client.get("/tasks/", headers=headers_b)

    assert response.status_code == 200
    assert all(task["id"] != task_id for task in response.json())


def test_other_user_cannot_update_task(task_owned_by_a):
    client, db, task_id, headers_a, headers_b = task_owned_by_a

    response = client.put(
        f"/tasks/{task_id}",
        headers=headers_b,
        json={"title": "Unauthorized change"},
    )

    assert response.status_code == 404

    db.expire_all()
    task = db.get(models.Task, task_id)

    assert task is not None
    assert task.title == "Owner A private task"


def test_other_user_cannot_delete_task(task_owned_by_a):
    client, db, task_id, headers_a, headers_b = task_owned_by_a

    task_before = db.get(models.Task, task_id)
    original_owner_id = task_before.owner_id

    response = client.delete(
        f"/tasks/{task_id}",
        headers=headers_b,
    )

    assert response.status_code == 404

    db.expire_all()
    task = db.get(models.Task, task_id)

    assert task is not None
    assert task.owner_id == original_owner_id