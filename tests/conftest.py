"""
Pytest configuration and shared fixtures for testing the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application.
    This client can be used to make requests in tests.
    """
    return TestClient(app)


@pytest.fixture
def sample_activity_name():
    """Return a sample activity name that exists in the app."""
    return "Chess Club"


@pytest.fixture
def sample_email():
    """Return a sample email for testing signup."""
    return "student@mergington.edu"
