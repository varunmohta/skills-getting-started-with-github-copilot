"""Tests for POST /activities/{activity_name}/signup endpoint."""

import pytest


class TestSignupForActivity:
    """Test suite for signing up students for activities."""

    def test_signup_valid_student_returns_200(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send POST request to signup with valid activity and email
        ASSERT: Response status should be 200
        """
        # Act
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        # Assert
        assert response.status_code == 200

    def test_signup_returns_success_message(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send POST request to signup
        ASSERT: Response should contain success message
        """
        # Act
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": "newemail@mergington.edu"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert "newemail@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """
        ARRANGE: Get initial participant count for an activity
        ACT: Sign up a new student
        ASSERT: Participant list should be updated
        """
        # Arrange
        response_before = client.get("/activities")
        initial_count = len(response_before.json()["Basketball Team"]["participants"])
        
        # Act
        client.post(
            "/activities/Basketball Team/signup",
            params={"email": "newplayer@mergington.edu"}
        )
        
        # Assert
        response_after = client.get("/activities")
        new_count = len(response_after.json()["Basketball Team"]["participants"])
        assert new_count == initial_count + 1
        assert "newplayer@mergington.edu" in response_after.json()["Basketball Team"]["participants"]

    def test_signup_activity_not_found_returns_404(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send POST request to signup with non-existent activity
        ASSERT: Response status should be 404
        """
        # Act
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_duplicate_student_returns_400(self, client):
        """
        ARRANGE: Student is already signed up for Chess Club
        ACT: Try to sign up the same student again
        ASSERT: Response status should be 400
        """
        # Arrange
        existing_student = "michael@mergington.edu"
        
        # Act
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": existing_student}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up"

    def test_signup_student_not_added_after_error(self, client):
        """
        ARRANGE: Get initial participant count
        ACT: Try to sign up a duplicate student
        ASSERT: Participant list should not change
        """
        # Arrange
        response_before = client.get("/activities")
        initial_count = len(response_before.json()["Soccer Club"]["participants"])
        existing_student = "liam@mergington.edu"
        
        # Act
        client.post(
            "/activities/Soccer Club/signup",
            params={"email": existing_student}
        )
        
        # Assert
        response_after = client.get("/activities")
        new_count = len(response_after.json()["Soccer Club"]["participants"])
        assert new_count == initial_count

    def test_signup_with_special_characters_in_email(self, client):
        """
        ARRANGE: No setup needed
        ACT: Sign up with an email containing special characters
        ASSERT: Should successfully sign up
        """
        # Act
        response = client.post(
            "/activities/Art Club/signup",
            params={"email": "student+test@mergington.edu"}
        )
        
        # Assert
        assert response.status_code == 200
        response_data = client.get("/activities").json()
        assert "student+test@mergington.edu" in response_data["Art Club"]["participants"]

    def test_signup_case_sensitivity_in_activity_name(self, client):
        """
        ARRANGE: No setup needed
        ACT: Try to sign up using different case for activity name
        ASSERT: Should fail because activity names are case-sensitive
        """
        # Act
        response = client.post(
            "/activities/chess club/signup",  # lowercase
            params={"email": "student@mergington.edu"}
        )
        
        # Assert
        assert response.status_code == 404

    @pytest.mark.parametrize("activity,email", [
        ("Drama Club", "actor1@mergington.edu"),
        ("Science Club", "scientist1@mergington.edu"),
        ("Debate Club", "debater1@mergington.edu"),
    ])
    def test_signup_multiple_activities(self, client, activity, email):
        """
        ARRANGE: No setup needed
        ACT: Sign up for different activities with different emails
        ASSERT: Each signup should succeed
        """
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        response_data = client.get("/activities").json()
        assert email in response_data[activity]["participants"]

    def test_signup_same_student_multiple_activities(self, client):
        """
        ARRANGE: Student is not signed up for Art Club
        ACT: Sign up the student for multiple activities
        ASSERT: Each signup should succeed
        """
        # Arrange
        student_email = "versatile@mergington.edu"
        
        # Act - Signup for Art Club
        response1 = client.post(
            "/activities/Art Club/signup",
            params={"email": student_email}
        )
        
        # Act - Signup for Debate Club
        response2 = client.post(
            "/activities/Debate Club/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        response_data = client.get("/activities").json()
        assert student_email in response_data["Art Club"]["participants"]
        assert student_email in response_data["Debate Club"]["participants"]

    def test_signup_missing_email_parameter(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send POST request without email parameter
        ASSERT: Should fail with appropriate error
        """
        # Act
        response = client.post("/activities/Chess Club/signup")
        
        # Assert
        assert response.status_code == 422  # Unprocessable Entity - missing required param

    def test_signup_empty_email(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send POST request with empty email parameter
        ASSERT: Should handle empty email appropriately
        """
        # Act
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": ""}
        )
        
        # Assert - Empty string should still be added (API doesn't validate format)
        assert response.status_code == 200
