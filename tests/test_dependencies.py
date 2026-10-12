from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.dependencies import get_current_user
from app.models import User


def test_get_current_user_success(monkeypatch):
    expected_user = MagicMock(spec=User)
    db = MagicMock()
    db.get.return_value = expected_user

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-token",
    )

    monkeypatch.setattr(
        "app.dependencies.decode_access_token",
        lambda token: 123,
    )

    result = get_current_user(credentials=credentials, db=db)

    assert result is expected_user
    db.get.assert_called_once_with(User, 123)


def test_get_current_user_invalid_token(monkeypatch):
    db = MagicMock()

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="invalid-token",
    )

    def raise_invalid_token(token):
        raise ValueError("Invalid token")

    monkeypatch.setattr(
        "app.dependencies.decode_access_token",
        raise_invalid_token,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=credentials, db=db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid or expired token"
    db.get.assert_not_called()


def test_get_current_user_not_found(monkeypatch):
    db = MagicMock()
    db.get.return_value = None

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-token",
    )

    monkeypatch.setattr(
        "app.dependencies.decode_access_token",
        lambda token: 999,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=credentials, db=db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "User not found"
    db.get.assert_called_once_with(User, 999)