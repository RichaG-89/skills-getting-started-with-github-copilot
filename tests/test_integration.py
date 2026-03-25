"""
Integration tests for the Activities API.
Tests complete user workflows and interactions between endpoints.
"""

import pytest


class TestIntegration:
    """Integration tests for user workflows."""

    def test_complete_signup_workflow(self, client):
        """Test complete workflow: fetch activities, then signup."""
        # Step 1: Get activities
        activities_response = client.get("/activities")
        assert activities_response.status_code == 200
        activities = activities_response.json()
        
        # Step 2: Pick an activity
        activity_name = list(activities.keys())[0]
        
        # Step 3: Sign up for the activity
        email = "workflow@test.edu"
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Step 4: Verify the signup by fetching activities again
        verify_response = client.get("/activities")
        updated_activities = verify_response.json()
        assert email in updated_activities[activity_name]["participants"]

    def test_multiple_activities_signup_workflow(self, client):
        """Test user signing up for multiple activities."""
        email = "multiactivity@test.edu"
        activities = client.get("/activities").json()
        activity_list = list(activities.keys())[:2]  # Get first 2 activities
        
        # Sign up for multiple activities
        for activity in activity_list:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify user is in all activities
        updated_activities = client.get("/activities").json()
        for activity in activity_list:
            assert email in updated_activities[activity]["participants"]

    def test_activity_availability_updates_after_signup(self, client):
        """Test that availability decreases after each signup."""
        activity = "Chess Club"
        
        # Get initial availability
        initial = client.get("/activities").json()[activity]
        initial_available = initial["max_participants"] - len(initial["participants"])
        
        # Sign up a student
        response = client.post(f"/activities/{activity}/signup?email=test1@test.edu")
        assert response.status_code == 200
        
        # Get updated availability
        updated = client.get("/activities").json()[activity]
        updated_available = updated["max_participants"] - len(updated["participants"])
        
        assert updated_available == initial_available - 1

    def test_signup_multiple_students_same_activity_sequential(self, client):
        """Test signing up multiple students sequentially."""
        activity = "Drama Club"
        emails = [f"student{i}@test.edu" for i in range(3)]
        
        # Sign up each student
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all are signed up
        activities = client.get("/activities").json()
        participants = activities[activity]["participants"]
        
        for email in emails:
            assert email in participants

    def test_error_recovery_workflow(self, client):
        """Test that API recovers properly after errors."""
        activity = "Science Club"
        email = "good@test.edu"
        
        # Try invalid activity (should fail)
        bad_response = client.post(f"/activities/Invalid/signup?email={email}")
        assert bad_response.status_code == 404
        
        # Then try valid activity (should succeed)
        good_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert good_response.status_code == 200
        
        # Verify the valid signup worked
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
