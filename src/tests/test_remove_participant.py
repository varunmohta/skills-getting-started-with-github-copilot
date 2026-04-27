"""Tests for DELETE /activities/{activity_name}/participants/{email} endpoint."""

import pytest


class TestRemoveParticipant:
    """Test suite for removing participants from activities."""

    def test_remove_participant_returns_200(self, client):
        """
        ARRANGE: No setup needed (participants already exist)
        ACT: Send DELETE request to remove an existing participant
        ASSERT: Response status should be 200
        """
        # Act
        response = client.delete(
            "/activities/Chess Club/participants/michael@mergington.edu"
        )
        
        # Assert
        assert response.status_code == 200

    def test_remove_participant_returns_success_message(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send DELETE request to remove a participant
        ASSERT: Response should contain success message
        """
        # Act
        response = client.delete(
            "/activities/Soccer Club/participants/liam@mergington.edu"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]
        assert "liam@mergington.edu" in data["message"]

    def test_remove_participant_deletes_from_activity(self, client):
        """
        ARRANGE: Get initial participant count and list
        ACT: Remove a participant from an activity
        ASSERT: Participant should no longer be in the list, count should decrease
        """
        # Arrange
        response_before = client.get("/activities")
        chess_participants_before = response_before.json()["Chess Club"]["participants"].copy()
        initial_count = len(chess_participants_before)
        
        # Act
        client.delete("/activities/Chess Club/participants/daniel@mergington.edu")
        
        # Assert
        response_after = client.get("/activities")
        chess_participants_after = response_after.json()["Chess Club"]["participants"]
        assert len(chess_participants_after) == initial_count - 1
        assert "daniel@mergington.edu" not in chess_participants_after
        assert "michael@mergington.edu" in chess_participants_after  # Other participant unaffected

    def test_remove_participant_activity_not_found_returns_404(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send DELETE request for non-existent activity
        ASSERT: Response status should be 404
        """
        # Act
        response = client.delete(
            "/activities/Nonexistent Activity/participants/student@mergington.edu"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_remove_nonexistent_participant_returns_404(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send DELETE request for participant not in activity
        ASSERT: Response status should be 404
        """
        # Act
        response = client.delete(
            "/activities/Chess Club/participants/nonexistent@mergington.edu"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Participant not found"

    def test_remove_participant_case_sensitive(self, client):
        """
        ARRANGE: No setup needed
        ACT: Try to remove participant with different email case
        ASSERT: Should fail because email is case-sensitive
        """
        # Act
        response = client.delete(
            "/activities/Drama Club/participants/MASON@MERGINGTON.EDU"  # uppercase
        )
        
        # Assert
        assert response.status_code == 404

    def test_remove_participant_activity_name_case_sensitive(self, client):
        """
        ARRANGE: No setup needed
        ACT: Try to remove participant using different case for activity name
        ASSERT: Should fail because activity names are case-sensitive
        """
        # Act
        response = client.delete(
            "/activities/basketball team/participants/alex@mergington.edu"  # lowercase
        )
        
        # Assert
        assert response.status_code == 404

    def test_remove_participant_then_readd(self, client):
        """
        ARRANGE: Get initial state
        ACT: Remove a participant, then add them back
        ASSERT: Both operations should succeed
        """
        # Arrange
        activity = "Programming Class"
        email = "emma@mergington.edu"
        
        # Act - Remove
        response_remove = client.delete(f"/activities/{activity}/participants/{email}")
        
        # Assert removal succeeded
        assert response_remove.status_code == 200
        response_check = client.get("/activities")
        assert email not in response_check.json()[activity]["participants"]
        
        # Act - Re-add
        response_add = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert re-add succeeded
        assert response_add.status_code == 200
        response_final = client.get("/activities")
        assert email in response_final.json()[activity]["participants"]

    def test_remove_last_participant(self, client):
        """
        ARRANGE: Get activity with only one participant
        ACT: Remove the only participant
        ASSERT: Activity should have empty participant list
        """
        # Arrange
        activity = "Art Club"
        email = "isabella@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity}/participants/{email}")
        
        # Assert
        assert response.status_code == 200
        response_data = client.get("/activities").json()
        assert len(response_data[activity]["participants"]) == 0

    def test_remove_participant_does_not_affect_other_activities(self, client):
        """
        ARRANGE: Get initial state of other activities
        ACT: Remove participant from one activity
        ASSERT: Other activities should be unaffected
        """
        # Arrange
        response_before = client.get("/activities")
        soccer_before = response_before.json()["Soccer Club"]["participants"].copy()
        
        # Act - Remove from Chess Club
        client.delete("/activities/Chess Club/participants/michael@mergington.edu")
        
        # Assert
        response_after = client.get("/activities")
        soccer_after = response_after.json()["Soccer Club"]["participants"]
        assert soccer_after == soccer_before  # Soccer unaffected

    @pytest.mark.parametrize("activity,email", [
        ("Drama Club", "mason@mergington.edu"),
        ("Science Club", "harper@mergington.edu"),
        ("Debate Club", "ethan@mergington.edu"),
    ])
    def test_remove_multiple_participants(self, client, activity, email):
        """
        ARRANGE: No setup needed
        ACT: Remove different participants from different activities
        ASSERT: Each removal should succeed
        """
        # Act
        response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 200
        response_data = client.get("/activities").json()
        assert email not in response_data[activity]["participants"]

    def test_remove_same_participant_twice_returns_404_on_second(self, client):
        """
        ARRANGE: No setup needed
        ACT: Remove the same participant twice
        ASSERT: First removal should succeed, second should fail
        """
        # Arrange
        activity = "Basketball Team"
        email = "alex@mergington.edu"
        
        # Act - First removal
        response1 = client.delete(f"/activities/{activity}/participants/{email}")
        
        # Assert first removal succeeded
        assert response1.status_code == 200
        
        # Act - Second removal (should fail)
        response2 = client.delete(f"/activities/{activity}/participants/{email}")
        
        # Assert second removal failed
        assert response2.status_code == 404
        assert response2.json()["detail"] == "Participant not found"

    def test_remove_participant_with_email_containing_plus(self, client):
        """
        ARRANGE: First add a participant with special email format
        ACT: Remove that participant
        ASSERT: Removal should succeed
        """
        # Arrange
        activity = "Gym Class"
        email = "student+special@mergington.edu"
        
        # Add the participant first
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Act - Remove
        response = client.delete(f"/activities/{activity}/participants/{email}")
        
        # Assert
        assert response.status_code == 200
        response_data = client.get("/activities").json()
        assert email not in response_data[activity]["participants"]
