"""
Tests for streak freeze functionality.
"""
import pytest
from datetime import datetime, timedelta, timezone
import httpx

from app.routers.streak import (
    is_monday_reset_needed,
    is_new_month,
    FREEZE_COST_COINS,
    MAX_FREEZES_PER_MONTH,
)


class TestHelperFunctions:
    """Test helper functions for streak freeze logic."""
    
    def test_is_monday_reset_needed_none(self):
        now = datetime(2024, 2, 15, 12, 0, 0, tzinfo=timezone.utc)
        assert is_monday_reset_needed(None, now) is True
    
    def test_is_monday_reset_needed_same_week(self):
        now = datetime(2024, 2, 15, 12, 0, 0, tzinfo=timezone.utc)
        last_freeze = datetime(2024, 2, 13, 10, 0, 0, tzinfo=timezone.utc)
        assert is_monday_reset_needed(last_freeze, now) is False
    
    def test_is_monday_reset_needed_previous_week(self):
        now = datetime(2024, 2, 15, 12, 0, 0, tzinfo=timezone.utc)
        last_freeze = datetime(2024, 2, 5, 10, 0, 0, tzinfo=timezone.utc)
        assert is_monday_reset_needed(last_freeze, now) is True
    
    def test_is_new_month_none(self):
        now = datetime(2024, 2, 15, tzinfo=timezone.utc)
        assert is_new_month(None, now) is True
    
    def test_is_new_month_same_month(self):
        now = datetime(2024, 2, 15, tzinfo=timezone.utc)
        last = datetime(2024, 2, 1, tzinfo=timezone.utc)
        assert is_new_month(last, now) is False
    
    def test_is_new_month_different_month(self):
        now = datetime(2024, 2, 15, tzinfo=timezone.utc)
        last = datetime(2024, 1, 31, tzinfo=timezone.utc)
        assert is_new_month(last, now) is True


class TestStreakEndpoints:
    """Test streak API endpoints using sync client."""
    
    def test_get_streak_status(self, client: httpx.Client, test_user):
        """Test basic streak status retrieval."""
        response = client.get("/api/streak/status", headers=test_user["headers"])
        
        assert response.status_code == 200
        data = response.json()
        
        assert "current_streak" in data
        assert "is_frozen" in data
        assert "free_freeze_available" in data
        assert "freezes_used_this_month" in data
    
    def test_freeze_streak(self, client: httpx.Client, test_user):
        """Test applying a freeze."""
        response = client.post("/api/streak/freeze", headers=test_user["headers"])
        
        # Should succeed (first freeze is free)
        assert response.status_code in [200, 400]  # 400 if already frozen
        
        if response.status_code == 200:
            data = response.json()
            assert "message" in data
            assert "frozen_until" in data
