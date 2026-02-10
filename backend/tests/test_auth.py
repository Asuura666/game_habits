"""Tests for authentication endpoints."""
import httpx


class TestAuth:
    """Test authentication endpoints."""

    def test_register_success(self, client: httpx.Client, unique_email, unique_username):
        """Test successful user registration."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "username": unique_username,
                "password": "SecurePass123!",
            },
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == unique_email
        assert data["user"]["level"] == 1
        assert data["user"]["total_xp"] == 0

    def test_login_success(self, client: httpx.Client, test_user):
        """Test successful login."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"],
            },
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "access_token" in data
        assert data["user"]["id"] == test_user["user"]["id"]

    def test_login_wrong_password(self, client: httpx.Client, test_user):
        """Test login with wrong password fails."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
                "password": "WrongPassword123!",
            },
        )
        
        assert response.status_code == 401

    def test_get_me(self, client: httpx.Client, test_user):
        """Test getting current user profile."""
        response = client.get(
            "/api/users/me",
            headers=test_user["headers"],
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["id"] == test_user["user"]["id"]

    def test_get_me_unauthorized(self, client: httpx.Client):
        """Test getting profile without token fails."""
        response = client.get("/api/users/me")
        
        assert response.status_code in [401, 403]
