"""Tests for authentication routes."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import get_db_connection


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean up database before each test."""
    conn = get_db_connection()
    conn.execute("DELETE FROM users")
    conn.commit()
    conn.close()
    yield


def test_login_with_correct_credentials(client):
    """Test login with correct username and password."""
    response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "user"
    assert "token" in data
    assert "userId" in data
    assert data["expiresIn"] == 86400


def test_login_with_incorrect_password(client):
    """Test login with incorrect password."""
    response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "wrong"},
    )

    assert response.status_code == 401
    data = response.json()
    assert "Invalid credentials" in data["detail"]


def test_login_with_incorrect_username(client):
    """Test login with incorrect username."""
    response = client.post(
        "/api/auth/login",
        json={"username": "wrong", "password": "password"},
    )

    assert response.status_code == 401
    data = response.json()
    assert "Invalid credentials" in data["detail"]


def test_verify_with_valid_token(client):
    """Test verify endpoint with valid token."""
    # First login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )
    token = login_response.json()["token"]

    # Verify token
    response = client.get(
        "/api/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "user"
    assert data["isAuthenticated"] is True


def test_verify_without_token(client):
    """Test verify endpoint without token."""
    response = client.get("/api/auth/verify")

    assert response.status_code == 401
    data = response.json()
    assert "Missing authentication token" in data["detail"]


def test_verify_with_invalid_token(client):
    """Test verify endpoint with invalid token."""
    response = client.get(
        "/api/auth/verify",
        headers={"Authorization": "Bearer invalid.token.here"},
    )

    assert response.status_code == 401


def test_logout(client):
    """Test logout endpoint."""
    response = client.post("/api/auth/logout")

    assert response.status_code == 200
    data = response.json()
    assert "success" in data["message"].lower() or "logged out" in data["message"].lower()


def test_board_requires_auth(client):
    """Test that board endpoint requires authentication."""
    response = client.get("/api/board")

    assert response.status_code == 401
    data = response.json()
    assert "Missing authentication token" in data["detail"]


def test_board_with_valid_token(client):
    """Test board endpoint with valid token."""
    # Login first
    login_response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )
    token = login_response.json()["token"]

    # Get board
    response = client.get(
        "/api/board",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "columns" in data
    assert "cards" in data
    assert len(data["columns"]) == 5


def test_token_set_in_cookie(client):
    """Test that token is set in httpOnly cookie."""
    response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )

    assert response.status_code == 200
    assert "auth_token" in response.cookies


def test_logout_clears_cookie(client):
    """Test that logout clears the auth cookie."""
    # First login to set cookie
    login_response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )

    # Then logout
    response = client.post("/api/auth/logout")

    assert response.status_code == 200
    # Cookie should be deleted (Max-Age=0 or similar)
    assert "auth_token" in response.cookies or response.cookies.get("auth_token") == ""
