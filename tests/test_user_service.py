from unittest.mock import MagicMock

from app import user_service


def test_register_user_success(monkeypatch):
    db = MagicMock()
    created_user = object()
    captured = {}

    def mock_get_user_by_email(db, email):
        return None

    def mock_hash_password(password):
        return "hashed-password"

    def mock_create_user(**kwargs):
        captured.update(kwargs)
        return created_user

    monkeypatch.setattr(
        user_service,
        "get_user_by_email",
        mock_get_user_by_email,
    )
    monkeypatch.setattr(
        user_service,
        "hash_password",
        mock_hash_password,
    )
    monkeypatch.setattr(
        user_service,
        "create_user",
        mock_create_user,
    )

    result = user_service.register_user(
        db=db,
        email="new@example.com",
        full_name="New User",
        password="TestPassword123!",
    )

    assert result is created_user
    assert captured["email"] == "new@example.com"
    assert captured["full_name"] == "New User"
    assert captured["hashed_password"] == "hashed-password"

import pytest


def test_register_user_duplicate_email(monkeypatch):
    db = MagicMock()
    existing_user = object()

    def mock_get_user_by_email(db, email):
        return existing_user

    monkeypatch.setattr(
        user_service,
        "get_user_by_email",
        mock_get_user_by_email,
    )

    with pytest.raises(
        ValueError,
        match="Email already registered",
    ):
        user_service.register_user(
            db=db,
            email="existing@example.com",
            full_name="Existing User",
            password="TestPassword123!",
        )

def test_authenticate_user_success(monkeypatch):
    db = MagicMock()

    user = type(
        "User",
        (),
        {
            "id": 1,
            "email": "valid@example.com",
            "hashed_password": "hashed-password",
        },
    )()

    monkeypatch.setattr(
        user_service,
        "get_user_by_email",
        lambda db, email: user,
    )
    monkeypatch.setattr(
        user_service,
        "verify_password",
        lambda password, hashed_password: True,
    )

    result = user_service.authenticate_user(
        db=db,
        email="valid@example.com",
        password="ValidPassword123!",
    )

    assert result is user


def test_authenticate_user_not_found(monkeypatch):
    db = MagicMock()

    monkeypatch.setattr(
        user_service,
        "get_user_by_email",
        lambda db, email: None,
    )

    result = user_service.authenticate_user(
        db=db,
        email="missing@example.com",
        password="AnyPassword123!",
    )

    assert result is None


def test_authenticate_user_wrong_password(monkeypatch):
    db = MagicMock()

    user = type(
        "User",
        (),
        {"hashed_password": "hashed-password"},
    )()

    monkeypatch.setattr(
        user_service,
        "get_user_by_email",
        lambda db, email: user,
    )
    monkeypatch.setattr(
        user_service,
        "verify_password",
        lambda password, hashed_password: False,
    )

    result = user_service.authenticate_user(
        db=db,
        email="valid@example.com",
        password="WrongPassword123!",
    )

    assert result is None