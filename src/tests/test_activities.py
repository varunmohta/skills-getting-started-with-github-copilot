"""Tests for GET /activities endpoint."""

import pytest


class TestGetActivities:
    """Test suite for retrieving all activities."""

    def test_get_activities_returns_200(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send GET request to /activities
        ASSERT: Response status should be 200
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send GET request to /activities
        ASSERT: Response should contain all 9 activities
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_has_correct_structure(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send GET request to /activities
        ASSERT: Each activity should have required fields
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_returns_correct_participants(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send GET request to /activities
        ASSERT: Specific activities should have correct participant lists
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 2

    def test_get_activities_chess_club_data(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send GET request to /activities
        ASSERT: Chess Club should have correct data
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]
        
        # Assert
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert len(chess_club["participants"]) == 2

    @pytest.mark.parametrize("activity_name", [
        "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
        "Soccer Club", "Art Club", "Drama Club", "Debate Club", "Science Club"
    ])
    def test_get_activities_all_activities_present(self, client, activity_name):
        """
        ARRANGE: No setup needed
        ACT: Send GET request to /activities
        ASSERT: All expected activities should be in response
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert activity_name in activities
        assert isinstance(activities[activity_name], dict)

    def test_get_activities_response_content_type(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send GET request to /activities
        ASSERT: Response should be JSON
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.headers["content-type"] == "application/json"
