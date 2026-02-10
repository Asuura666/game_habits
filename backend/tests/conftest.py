"""Pytest configuration for integration tests."""
import os
from uuid import uuid4

import pytest
import httpx

# Base URL for the API
BASE_URL = os.getenv("TEST_API_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def base_url():
    """Get the base URL for the API."""
    return BASE_URL


@pytest.fixture(scope="session")
def client():
    """Create HTTP client for testing."""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture
def unique_email():
    """Generate a unique email for testing."""
    return f"test_{uuid4().hex[:8]}@test.com"


@pytest.fixture
def unique_username():
    """Generate a unique username for testing."""
    return f"user_{uuid4().hex[:8]}"


@pytest.fixture
def test_user(client, unique_email, unique_username):
    """Create a test user and return credentials with token."""
    user_data = {
        "email": unique_email,
        "username": unique_username,
        "password": "TestPassword123!",
    }
    
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code in [200, 201], f"Registration failed: {response.text}"
    
    data = response.json()
    return {
        "user": data["user"],
        "token": data["access_token"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
        "password": user_data["password"],
        "email": unique_email,
    }


@pytest.fixture
def test_user_with_character(client, test_user):
    """Create a test user with a character."""
    character_data = {
        "name": f"Hero{uuid4().hex[:6]}",
        "character_class": "warrior",
        "stats": {
            "strength": 5,
            "intelligence": 5,
            "agility": 5,
            "vitality": 5,
            "luck": 5,
        },
    }
    
    response = client.post(
        "/api/characters/",
        json=character_data,
        headers=test_user["headers"],
    )
    assert response.status_code == 201, f"Character creation failed: {response.text}"
    
    test_user["character"] = response.json()
    return test_user
