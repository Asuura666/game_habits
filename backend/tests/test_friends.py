"""
Tests for Friends/Social endpoints.

Tests:
- Get friends list
- Send friend request
- Accept/reject friend request
- Get pending requests
- Get/use friend code
- Remove friend
- Public profiles
"""

import pytest
from uuid import uuid4


class TestFriendsList:
    """Tests for GET /api/friends"""
    
    def test_get_friends_empty(self, client, test_user):
        """Test getting friends list when empty."""
        # Note: trailing slash to avoid redirect
        response = client.get("/api/friends/", headers=test_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert "friends" in data
        assert data["friends"] == []
        assert data["total"] == 0
    
    def test_get_friends_unauthorized(self, client):
        """Test getting friends without auth."""
        response = client.get("/api/friends/")
        assert response.status_code in [401, 403]


class TestFriendCode:
    """Tests for friend code functionality."""
    
    def test_get_friend_code(self, client, test_user):
        """Test getting own friend code."""
        response = client.get("/api/friends/code", headers=test_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert "friend_code" in data
        assert len(data["friend_code"]) > 0
        assert "username" in data
    
    def test_add_by_invalid_friend_code(self, client, test_user):
        """Test adding friend with invalid code."""
        response = client.post(
            "/api/friends/code/INVALIDCODE123",
            headers=test_user["headers"]
        )
        assert response.status_code == 404
        assert "Invalid friend code" in response.json()["detail"]
    
    def test_cannot_add_self_by_code(self, client, test_user):
        """Test cannot add yourself as friend."""
        # First get own friend code
        code_response = client.get("/api/friends/code", headers=test_user["headers"])
        friend_code = code_response.json()["friend_code"]
        
        # Try to add self
        response = client.post(
            f"/api/friends/code/{friend_code}",
            headers=test_user["headers"]
        )
        assert response.status_code == 400
        assert "cannot add yourself" in response.json()["detail"].lower()


class TestFriendRequests:
    """Tests for friend request flow."""
    
    def test_get_pending_requests_empty(self, client, test_user):
        """Test getting pending requests when empty."""
        response = client.get("/api/friends/pending", headers=test_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert "incoming" in data
        assert "outgoing" in data
        assert data["incoming"] == []
        assert data["outgoing"] == []
        assert data["incoming_count"] == 0
        assert data["outgoing_count"] == 0


class TestFriendRequestFlow:
    """Integration tests for full friend request flow."""
    
    def test_full_friend_flow(self, client, test_user):
        """Test complete friend request flow: send -> accept -> list -> remove."""
        # Create a second user
        unique = uuid4().hex[:8]
        second_user_data = {
            "email": f"friend_{unique}@test.com",
            "username": f"Friend_{unique}",
            "password": "FriendPass123!"
        }
        
        register_response = client.post("/api/auth/register", json=second_user_data)
        assert register_response.status_code in [200, 201]
        second_token = register_response.json()["access_token"]
        second_headers = {"Authorization": f"Bearer {second_token}"}
        
        # 1. Get second user's friend code
        code_response = client.get("/api/friends/code", headers=second_headers)
        assert code_response.status_code == 200
        friend_code = code_response.json()["friend_code"]
        
        # 2. Send friend request via code (first user sends to second)
        send_response = client.post(
            f"/api/friends/code/{friend_code}",
            headers=test_user["headers"]
        )
        assert send_response.status_code == 201
        request_data = send_response.json()
        assert request_data["status"] == "pending"
        
        # 3. Check pending requests (second user should see incoming)
        pending_response = client.get("/api/friends/pending", headers=second_headers)
        assert pending_response.status_code == 200
        pending = pending_response.json()
        assert pending["incoming_count"] == 1
        friendship_id = pending["incoming"][0]["id"]
        
        # 4. Accept friend request
        accept_response = client.post(
            f"/api/friends/accept/{friendship_id}",
            headers=second_headers
        )
        assert accept_response.status_code == 200
        
        # 5. Check friends list (both should see each other) - with trailing slash
        friends_response = client.get("/api/friends/", headers=test_user["headers"])
        assert friends_response.status_code == 200
        friends = friends_response.json()
        assert friends["total"] == 1
        
        friend_user_id = friends["friends"][0]["user_id"]
        
        # 6. Remove friend
        remove_response = client.delete(
            f"/api/friends/{friend_user_id}",
            headers=test_user["headers"]
        )
        assert remove_response.status_code in [200, 204]
        
        # 7. Verify removed
        final_response = client.get("/api/friends/", headers=test_user["headers"])
        assert final_response.json()["total"] == 0
    
    def test_reject_friend_request(self, client, test_user):
        """Test rejecting a friend request."""
        # Create a second user
        unique = uuid4().hex[:8]
        second_user_data = {
            "email": f"reject_{unique}@test.com",
            "username": f"Reject_{unique}",
            "password": "RejectPass123!"
        }
        
        register_response = client.post("/api/auth/register", json=second_user_data)
        assert register_response.status_code in [200, 201]
        second_token = register_response.json()["access_token"]
        second_headers = {"Authorization": f"Bearer {second_token}"}
        
        # Get friend code and send request
        code_response = client.get("/api/friends/code", headers=second_headers)
        friend_code = code_response.json()["friend_code"]
        
        client.post(f"/api/friends/code/{friend_code}", headers=test_user["headers"])
        
        # Get pending and reject
        pending_response = client.get("/api/friends/pending", headers=second_headers)
        friendship_id = pending_response.json()["incoming"][0]["id"]
        
        reject_response = client.post(
            f"/api/friends/reject/{friendship_id}",
            headers=second_headers
        )
        # Reject can return 200 or 204
        assert reject_response.status_code in [200, 204]
        
        # Verify not in friends list
        friends_response = client.get("/api/friends/", headers=second_headers)
        assert friends_response.json()["total"] == 0


class TestPublicProfile:
    """Tests for public profile visibility."""
    
    def test_get_own_profile(self, client, test_user):
        """Test getting own profile via /users/me."""
        response = client.get("/api/users/me", headers=test_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data
    
    def test_update_profile_public(self, client, test_user):
        """Test making profile public."""
        response = client.put(
            "/api/users/me",
            headers=test_user["headers"],
            json={"is_public": True, "bio": "Test bio for public profile"}
        )
        assert response.status_code == 200
        data = response.json()
        # Verify update worked if fields are in response
        if "is_public" in data:
            assert data["is_public"] == True
        if "bio" in data:
            assert data["bio"] == "Test bio for public profile"
    
    def test_find_user_by_friend_code(self, client, test_user):
        """Test finding user by friend code."""
        # Get own friend code first
        code_response = client.get("/api/friends/code", headers=test_user["headers"])
        friend_code = code_response.json()["friend_code"]
        
        response = client.get(
            f"/api/users/friend-code/{friend_code}",
            headers=test_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user["user"]["username"]
    
    def test_private_profile_hidden(self, client, test_user):
        """Test that private profiles return 403 for non-owners."""
        # Create a second user with private profile
        unique = uuid4().hex[:8]
        second_user_data = {
            "email": f"private_{unique}@test.com",
            "username": f"Private_{unique}",
            "password": "PrivatePass123!"
        }
        
        register_response = client.post("/api/auth/register", json=second_user_data)
        assert register_response.status_code in [200, 201]
        second_user_id = register_response.json()["user"]["id"]
        
        # Try to view their profile (should be private by default)
        response = client.get(
            f"/api/users/{second_user_id}",
            headers=test_user["headers"]
        )
        # Should be 403 since profile is private
        assert response.status_code == 403
