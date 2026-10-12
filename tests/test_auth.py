def test_register_success(client, monkeypatch):
    from app import auth_router

    def mock_register_user(**kwargs):
        return {
            "id": 1,
            "email": "new@example.com",
            "full_name": "Test User",
            "is_active": True
        }

    monkeypatch.setattr(auth_router, "register_user", mock_register_user)

    response = client.post(
        "/auth/register",
        json={
            "email": "new@example.com",
            "full_name": "Test User",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 201 or response.status_code == 200
    assert response.json()["email"] == "new@example.com"
    assert "hashed_password" not in response.json()


def test_login_missing_fields(client):
    response = client.post("/auth/login", json={})

    assert response.status_code == 422



def test_login_invalid_credentials(client, monkeypatch):
    from app import auth_router

    def fake_authenticate_user(db, email, password):
        return None

    monkeypatch.setattr(
        auth_router,
        "authenticate_user",
        fake_authenticate_user,
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401



def test_register_missing_fields(client):
    response = client.post("/auth/register", json={})

    assert response.status_code == 422


def test_register_duplicate_email(client, monkeypatch):
    from app import auth_router

    def mock_register_user(**kwargs):
        raise ValueError("Email already registered")

    monkeypatch.setattr(auth_router, "register_user", mock_register_user)

    response = client.post(
        "/auth/register",
        json={
            "email": "existing@example.com",
            "full_name": "Test User",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 400 or response.status_code == 409


def test_login_success(client, monkeypatch):
    from app import auth_router

    user = type("User", (), {"id": 1})()

    def mock_authenticate_user(**kwargs):
        return user

    monkeypatch.setattr(
        auth_router,
        "authenticate_user",
        mock_authenticate_user,
    )
    monkeypatch.setattr(
        auth_router,
        "create_access_token",
        lambda user_id: "test-access-token",
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "valid@example.com",
            "password": "ValidPassword123!",
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "test-access-token"
    assert response.json()["token_type"] == "bearer"


def test_get_me(client):
    from app.main import app
    from app import auth_router

    user = type(
        "User",
        (),
        {
            "id": 1,
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True,
        },
    )()

    app.dependency_overrides[
        auth_router.get_current_user
    ] = lambda: user

    try:
        response = client.get("/auth/me")

        assert response.status_code == 200
        assert response.json()["id"] == 1
        assert response.json()["email"] == "test@example.com"
        assert response.json()["full_name"] == "Test User"

    finally:
        app.dependency_overrides.clear()