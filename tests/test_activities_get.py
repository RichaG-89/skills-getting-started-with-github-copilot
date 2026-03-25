"""
Tests for GET /activities endpoint.
Tests retrieving all available activities and their details.
"""

import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns a 200 status code."""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary of activities."""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)

    def test_activities_have_required_fields(self, client):
        """Test that each activity has all required fields."""
        response = client.get("/activities")
        activities = response.json()

        required_fields = {"description", "schedule", "max_participants", "participants"}

        for activity_name, activity_details in activities.items():
            assert isinstance(activity_name, str), f"Activity name should be string, got {type(activity_name)}"
            assert all(
                field in activity_details for field in required_fields
            ), f"Activity '{activity_name}' missing required fields"

    def test_activities_field_types(self, client):
        """Test that activity fields have correct data types."""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_details in activities.items():
            assert isinstance(activity_details["description"], str)
            assert isinstance(activity_details["schedule"], str)
            assert isinstance(activity_details["max_participants"], int)
            assert isinstance(activity_details["participants"], list)

    def test_participants_are_strings(self, client):
        """Test that participants list contains only strings (emails)."""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_details in activities.items():
            for participant in activity_details["participants"]:
                assert isinstance(participant, str), (
                    f"Participant in '{activity_name}' should be string, got {type(participant)}"
                )

    def test_activities_exist(self, client):
        """Test that at least some activities are returned."""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities) > 0, "Should have at least one activity"

    def test_known_activities_exist(self, client):
        """Test that known activities are available."""
        response = client.get("/activities")
        activities = response.json()
        activity_names = set(activities.keys())

        expected_activities = {"Chess Club", "Programming Class", "Basketball Team"}
        assert expected_activities.issubset(
            activity_names
        ), f"Expected activities {expected_activities} not found"

    def test_max_participants_is_positive(self, client):
        """Test that max_participants is always a positive number."""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_details in activities.items():
            assert (
                activity_details["max_participants"] > 0
            ), f"Activity '{activity_name}' has non-positive max_participants"

    def test_participants_count_not_exceeds_max(self, client):
        """Test that current participants count doesn't exceed max_participants."""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_details in activities.items():
            participants_count = len(activity_details["participants"])
            max_participants = activity_details["max_participants"]
            assert (
                participants_count <= max_participants
            ), f"Activity '{activity_name}' has {participants_count} participants but max is {max_participants}"

    def test_response_is_json(self, client):
        """Test that response content type is JSON."""
        response = client.get("/activities")
        assert response.headers["content-type"] == "application/json"
