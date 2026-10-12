import pytest

from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_hash_password():
    password = "TestPassword123"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password) is True


def test_verify_password_wrong_password():
    hashed_password = hash_password("CorrectPassword123")

    assert verify_password("WrongPassword123", hashed_password) is False


def test_decode_valid_access_token():
    token = create_access_token(user_id=123)

    assert decode_access_token(token) == 123


def test_decode_invalid_access_token():
    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token("this-is-not-a-valid-token")


def test_decode_token_without_user_id():
    from jose import jwt
    from app.security import SECRET_KEY, ALGORITHM

    token = jwt.encode(
        {"role": "user"},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token(token)


def test_decode_token_with_non_numeric_user_id():
    from jose import jwt
    from app.security import SECRET_KEY, ALGORITHM

    token = jwt.encode(
        {"sub": "not-a-number"},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token(token)