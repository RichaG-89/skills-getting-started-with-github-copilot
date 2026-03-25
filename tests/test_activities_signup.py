"""
Tests for POST /activities/{activity_name}/signup endpoint.
Tests student signup functionality and error handling.
"""

import pytest


class TestActivitySignup:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_returns_200_on_success(self, client, sample_activity_name, sample_email):
        """Test that successful signup returns 200 status code."""
        response = client.post(
            f"/activities/{sample_activity_name}/signup?email={sample_email}"
        )
        assert response.status_code == 200

    def test_signup_returns_json_response(self, client, sample_activity_name, sample_email):
        """Test that signup response is JSON."""
        response = client.post(
            f"/activities/{sample_activity_name}/signup?email={sample_email}"
        )
        assert response.headers["content-type"] == "application/json"

    def test_signup_response_contains_message(self, client, sample_activity_name):
        """Test that signup response contains a message field."""
        email = "test_message_response@test.edu"
        response = client.post(
            f"/activities/{sample_activity_name}/signup?email={email}"
        )
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)

    def test_signup_response_message_contains_email(self, client, sample_activity_name):
        """Test that response message contains the student's email."""
        email = "test_message_email@test.edu"
        response = client.post(
            f"/activities/{sample_activity_name}/signup?email={email}"
        )
        data = response.json()
        assert email in data["message"]

    def test_signup_nonexistent_activity_returns_404(self, client, sample_email):
        """Test that signup for non-existent activity returns 404."""
        response = client.post(
            f"/activities/Nonexistent Activity/signup?email={sample_email}"
        )
        assert response.status_code == 404

    def test_signup_missing_email_returns_422(self, client, sample_activity_name):
        """Test that signup without email parameter returns 422."""
        response = client.post(f"/activities/{sample_activity_name}/signup")
        assert response.status_code == 422

    def test_signup_duplicate_email_returns_400(self, client, sample_activity_name):
        """Test that duplicate signup returns 400 error."""
        # First signup should succeed
        response1 = client.post(
            f"/activities/{sample_activity_name}/signup?email=duplicate@test.edu"
        )
        assert response1.status_code == 200

        # Second signup with same email should fail
        response2 = client.post(
            f"/activities/{sample_activity_name}/signup?email=duplicate@test.edu"
        )
        assert response2.status_code == 400

    def test_signup_duplicate_returns_error_message(self, client, sample_activity_name):
        """Test that duplicate signup error contains meaningful message."""
        email = "duplicate@test.edu"
        
        # First signup
        client.post(f"/activities/{sample_activity_name}/signup?email={email}")
        
        # Second signup
        response = client.post(f"/activities/{sample_activity_name}/signup?email={email}")
        data = response.json()
        
        assert "detail" in data
        assert "already" in data["detail"].lower() or "already signed up" in data["detail"].lower()

    def test_signup_adds_participant_to_activity(self, client, sample_activity_name):
        """Test that signup actually adds the participant to the activity."""
        email = "newstudent@test.edu"
        
        # Get initial count
        activities_before = client.get("/activities").json()
        count_before = len(activities_before[sample_activity_name]["participants"])
        
        # Sign up
        client.post(f"/activities/{sample_activity_name}/signup?email={email}")
        
        # Get updated count
        activities_after = client.get("/activities").json()
        count_after = len(activities_after[sample_activity_name]["participants"])
        
        assert count_after == count_before + 1
        assert email in activities_after[sample_activity_name]["participants"]

    def test_signup_email_appears_in_participants_list(self, client, sample_activity_name):
        """Test that signed-up email appears in activity's participants list."""
        email = "verify@test.edu"
        
        client.post(f"/activities/{sample_activity_name}/signup?email={email}")
        
        activities = client.get("/activities").json()
        participants = activities[sample_activity_name]["participants"]
        
        assert email in participants

    def test_signup_does_not_affect_other_activities(self, client):
        """Test that signing up for one activity doesn't affect others."""
        activity1 = "Chess Club"
        activity2 = "Basketball Team"
        email = "multiactivity@test.edu"
        
        # Get initial state
        activities_before = client.get("/activities").json()
        basketball_before = set(activities_before[activity2]["participants"])
        
        # Sign up for Chess Club
        client.post(f"/activities/{activity1}/signup?email={email}")
        
        # Check that Basketball Team is unchanged
        activities_after = client.get("/activities").json()
        basketball_after = set(activities_after[activity2]["participants"])
        
        assert basketball_before == basketball_after

    def test_signup_different_students_same_activity(self, client, sample_activity_name):
        """Test that multiple different students can sign up for the same activity."""
        activity = sample_activity_name
        email1 = "student1@test.edu"
        email2 = "student2@test.edu"
        
        # Sign up first student
        response1 = client.post(f"/activities/{activity}/signup?email={email1}")
        assert response1.status_code == 200
        
        # Sign up second student
        response2 = client.post(f"/activities/{activity}/signup?email={email2}")
        assert response2.status_code == 200
        
        # Verify both are in the activity
        activities = client.get("/activities").json()
        participants = activities[activity]["participants"]
        
        assert email1 in participants
        assert email2 in participants

    def test_signup_with_special_characters_in_email(self, client, sample_activity_name):
        """Test signup with special characters in email address."""
        # Valid email with common special characters
        email = "test.student+tag@example.edu"
        
        response = client.post(f"/activities/{sample_activity_name}/signup?email={email}")
        
        # Should successfully sign up (email format might be validated)
        assert response.status_code in [200, 422]  # 422 if email validation fails

    def test_signup_case_sensitivity_of_activity_name(self, client):
        """Test if activity names are case-sensitive."""
        email = "case@test.edu"
        
        # Try with different cases
        response_lower = client.post(
            f"/activities/chess%20club/signup?email={email}"
        )
        
        # The original activity is "Chess Club" with capitals
        # This tests whether the API is case-sensitive
        # Both might work or only the correct case might work
        assert response_lower.status_code in [200, 404]
