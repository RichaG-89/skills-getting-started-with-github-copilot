"""
Tests for GET / endpoint.
Tests the root path redirect to static files.
"""

import pytest


class TestRootRedirect:
    """Test suite for GET / endpoint."""

    def test_root_path_returns_redirect(self, client):
        """Test that root path returns a redirect status."""
        response = client.get("/", follow_redirects=False)
        # Should be 307 (temporary redirect) or 302
        assert response.status_code in [307, 302]

    def test_root_path_redirects_to_static(self, client):
        """Test that root path redirects to static files."""
        response = client.get("/", follow_redirects=False)
        assert "location" in response.headers
        assert "static" in response.headers["location"]

    def test_root_path_with_follow_redirects_returns_html(self, client):
        """Test that following the redirect returns HTML content."""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
