"""Tests for stats endpoints."""
import httpx


class TestStats:
    """Test statistics endpoints."""

    def test_stats_overview(self, client: httpx.Client, test_user_with_character):
        """Test getting stats overview."""
        response = client.get(
            "/api/stats/overview",
            headers=test_user_with_character["headers"],
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "time_range" in data
        assert "total_habits" in data
        assert "current_streak" in data

    def test_stats_habits(self, client: httpx.Client, test_user_with_character):
        """Test getting habit stats."""
        response = client.get(
            "/api/stats/habits",
            headers=test_user_with_character["headers"],
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_stats_calendar(self, client: httpx.Client, test_user_with_character):
        """Test getting calendar view."""
        response = client.get(
            "/api/stats/calendar",
            headers=test_user_with_character["headers"],
        )
        
        assert response.status_code == 200
