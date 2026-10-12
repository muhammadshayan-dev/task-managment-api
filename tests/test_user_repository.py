from unittest.mock import MagicMock

from app.models import User
from app.user_repository import get_user_by_email, create_user


def test_get_user_by_email_found():
    db = MagicMock()

    expected_user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed-password",
    )

    db.execute.return_value.scalar_one_or_none.return_value = expected_user

    result = get_user_by_email(db, "test@example.com")

    assert result == expected_user
    db.execute.assert_called_once()


def test_get_user_by_email_not_found():
    db = MagicMock()

    db.execute.return_value.scalar_one_or_none.return_value = None

    result = get_user_by_email(db, "missing@example.com")

    assert result is None
    db.execute.assert_called_once()


def test_create_user():
    db = MagicMock()

    result = create_user(
        db=db,
        email="new@example.com",
        full_name="New User",
        hashed_password="hashed-password",
    )

    assert isinstance(result, User)
    assert result.email == "new@example.com"
    assert result.full_name == "New User"
    assert result.hashed_password == "hashed-password"

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)