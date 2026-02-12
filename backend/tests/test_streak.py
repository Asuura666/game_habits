"""
Tests for streak freeze functionality.
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from fastapi import status
from httpx import AsyncClient, ASGITransport

# We'll test the router logic directly
from app.routers.streak import (
    is_monday_reset_needed,
    is_new_month,
    FREEZE_COST_COINS,
    MAX_FREEZES_PER_MONTH,
)


class TestHelperFunctions:
    """Test helper functions for streak freeze logic."""
    
    def test_is_monday_reset_needed_none(self):
        """Free freeze available if never used."""
        now = datetime(2024, 2, 15, 12, 0, 0, tzinfo=timezone.utc)  # Thursday
        assert is_monday_reset_needed(None, now) is True
    
    def test_is_monday_reset_needed_same_week(self):
        """No reset if freeze used same week."""
        now = datetime(2024, 2, 15, 12, 0, 0, tzinfo=timezone.utc)  # Thursday
        last_freeze = datetime(2024, 2, 13, 10, 0, 0, tzinfo=timezone.utc)  # Tuesday same week
        assert is_monday_reset_needed(last_freeze, now) is False
    
    def test_is_monday_reset_needed_previous_week(self):
        """Reset available if freeze was previous week."""
        now = datetime(2024, 2, 15, 12, 0, 0, tzinfo=timezone.utc)  # Thursday
        last_freeze = datetime(2024, 2, 5, 10, 0, 0, tzinfo=timezone.utc)  # Monday previous week
        assert is_monday_reset_needed(last_freeze, now) is True
    
    def test_is_new_month_none(self):
        """New month if never used."""
        now = datetime(2024, 2, 15, tzinfo=timezone.utc)
        assert is_new_month(None, now) is True
    
    def test_is_new_month_same_month(self):
        """Not new month if same month."""
        now = datetime(2024, 2, 15, tzinfo=timezone.utc)
        last = datetime(2024, 2, 1, tzinfo=timezone.utc)
        assert is_new_month(last, now) is False
    
    def test_is_new_month_different_month(self):
        """New month if different month."""
        now = datetime(2024, 2, 15, tzinfo=timezone.utc)
        last = datetime(2024, 1, 31, tzinfo=timezone.utc)
        assert is_new_month(last, now) is True


class TestStreakStatus:
    """Test GET /api/streak/status endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_streak_status_basic(self, client: AsyncClient, auth_headers: dict):
        """Test basic streak status retrieval."""
        response = await client.get("/api/streak/status", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "current_streak" in data
        assert "best_streak" in data
        assert "is_frozen" in data
        assert "free_freeze_available" in data
        assert "freezes_used_this_month" in data
        assert "freezes_remaining_this_month" in data
        assert "coins" in data
        assert "freeze_cost" in data
        assert data["freeze_cost"] == FREEZE_COST_COINS
    
    @pytest.mark.asyncio
    async def test_get_streak_status_frozen(self, client: AsyncClient, auth_headers: dict, test_user):
        """Test streak status when frozen."""
        # Set user as frozen
        test_user.streak_frozen_until = datetime.now(timezone.utc) + timedelta(hours=12)
        
        response = await client.get("/api/streak/status", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_frozen"] is True
        assert data["frozen_until"] is not None


class TestFreezeStreak:
    """Test POST /api/streak/freeze endpoint."""
    
    @pytest.mark.asyncio
    async def test_free_freeze_success(self, client: AsyncClient, auth_headers: dict, test_user):
        """Test successful free freeze."""
        # Ensure no previous freeze this week
        test_user.last_free_freeze = None
        test_user.freeze_count_month = 0
        
        response = await client.post("/api/streak/freeze", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["success"] is True
        assert data["was_free"] is True
        assert data["coins_spent"] == 0
        assert "frozen_until" in data
    
    @pytest.mark.asyncio
    async def test_paid_freeze_success(self, client: AsyncClient, auth_headers: dict, test_user):
        """Test successful paid freeze."""
        # User already used free freeze this week
        test_user.last_free_freeze = datetime.now(timezone.utc) - timedelta(days=1)
        test_user.freeze_count_month = 1
        test_user.coins = 100  # Enough coins
        test_user.streak_frozen_until = None  # Not currently frozen
        
        response = await client.post("/api/streak/freeze", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["success"] is True
        assert data["was_free"] is False
        assert data["coins_spent"] == FREEZE_COST_COINS
    
    @pytest.mark.asyncio
    async def test_freeze_insufficient_coins(self, client: AsyncClient, auth_headers: dict, test_user):
        """Test freeze fails with insufficient coins."""
        # User already used free freeze, not enough coins
        test_user.last_free_freeze = datetime.now(timezone.utc) - timedelta(days=1)
        test_user.freeze_count_month = 1
        test_user.coins = 10  # Not enough
        test_user.streak_frozen_until = None
        
        response = await client.post("/api/streak/freeze", headers=auth_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Insufficient coins" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_freeze_monthly_limit(self, client: AsyncClient, auth_headers: dict, test_user):
        """Test freeze fails when monthly limit reached."""
        test_user.freeze_count_month = MAX_FREEZES_PER_MONTH
        test_user.last_free_freeze = datetime.now(timezone.utc) - timedelta(days=1)
        test_user.streak_frozen_until = None
        
        response = await client.post("/api/streak/freeze", headers=auth_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Monthly freeze limit" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_freeze_already_frozen(self, client: AsyncClient, auth_headers: dict, test_user):
        """Test freeze fails when already frozen."""
        test_user.streak_frozen_until = datetime.now(timezone.utc) + timedelta(hours=12)
        
        response = await client.post("/api/streak/freeze", headers=auth_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already frozen" in response.json()["detail"]


# Pytest fixtures (these would be in conftest.py)
@pytest.fixture
def test_user():
    """Create a mock test user."""
    user = MagicMock()
    user.id = uuid4()
    user.current_streak = 5
    user.best_streak = 10
    user.coins = 100
    user.last_free_freeze = None
    user.freeze_count_month = 0
    user.streak_frozen_until = None
    return user


@pytest.fixture
def auth_headers():
    """Mock auth headers."""
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
async def client():
    """Create async test client."""
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
