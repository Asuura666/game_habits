"""Tests for the calendar endpoint."""

import pytest
from datetime import date, timedelta
from uuid import uuid4


class TestCalendarEndpoint:
    """Tests for GET /api/completions/calendar."""

    def test_get_calendar_current_month(self, client, test_user_with_character):
        """Test getting calendar data for the current month."""
        headers = test_user_with_character["headers"]
        
        # Create a habit
        habit_data = {
            "title": "Test Calendar Habit",
            "description": "Test description",
            "frequency": "daily",
            "base_xp": 10,
        }
        response = client.post("/api/habits/", json=habit_data, headers=headers)
        assert response.status_code == 201
        habit = response.json()
        
        # Complete the habit
        response = client.post(
            "/api/completions/",
            json={"habit_id": habit["id"]},
            headers=headers,
        )
        assert response.status_code == 201
        
        # Request calendar data
        response = client.get("/api/completions/calendar", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify response structure
        assert "month" in data
        assert "days" in data
        assert "summary" in data
        
        # Verify current month format
        today = date.today()
        expected_month = today.strftime("%Y-%m")
        assert data["month"] == expected_month
        
        # Verify days array is not empty
        assert len(data["days"]) > 0
        
        # Verify first day has correct structure
        first_day = data["days"][0]
        assert "date" in first_day
        assert "completion_rate" in first_day
        assert "habits_done" in first_day
        assert "habits_total" in first_day
        assert "xp_earned" in first_day

    def test_get_calendar_specific_month(self, client, test_user_with_character):
        """Test getting calendar data for a specific month."""
        headers = test_user_with_character["headers"]
        
        # Request calendar for current month
        today = date.today()
        month_str = today.strftime("%Y-%m")
        
        response = client.get(
            f"/api/completions/calendar?month={month_str}",
            headers=headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["month"] == month_str
        # Verify number of days matches the month
        from calendar import monthrange
        _, days_in_month = monthrange(today.year, today.month)
        assert len(data["days"]) == days_in_month

    def test_calendar_with_no_completions(self, client, test_user_with_character):
        """Test calendar when there are no completions for a past month."""
        headers = test_user_with_character["headers"]
        
        # Request calendar for past month (should have no completions)
        response = client.get(
            "/api/completions/calendar?month=2025-01",
            headers=headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["month"] == "2025-01"
        assert data["summary"]["perfect_days"] == 0
        assert data["summary"]["total_completions"] == 0
        assert data["summary"]["average_rate"] == 0.0
        
        # All days should have 0 completion rate
        for day in data["days"]:
            assert day["habits_done"] == 0
            assert day["completion_rate"] == 0.0

    def test_calendar_summary_calculation(self, client, test_user_with_character):
        """Test that summary statistics are calculated correctly."""
        headers = test_user_with_character["headers"]
        
        # Get calendar data
        response = client.get("/api/completions/calendar", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        summary = data["summary"]
        
        # Verify summary structure
        assert "perfect_days" in summary
        assert "total_completions" in summary
        assert "average_rate" in summary
        
        # Values should be non-negative
        assert summary["perfect_days"] >= 0
        assert summary["total_completions"] >= 0
        assert 0.0 <= summary["average_rate"] <= 1.0

    def test_calendar_invalid_month_format(self, client, test_user_with_character):
        """Test that invalid month format returns 422."""
        headers = test_user_with_character["headers"]
        
        response = client.get(
            "/api/completions/calendar?month=invalid",
            headers=headers,
        )
        
        assert response.status_code == 422

    def test_calendar_unauthorized(self, client):
        """Test that unauthorized access returns 401 or 403."""
        response = client.get("/api/completions/calendar")
        
        assert response.status_code in [401, 403]
