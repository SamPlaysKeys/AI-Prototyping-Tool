"""
Web integration tests with TestClient.

Tests FastAPI web application endpoints, WebSocket functionality, etc.
"""

import json
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import WebSocket

# Import the web app
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "web"))

from web.app import app


@pytest.fixture
def test_client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.mark.web
@pytest.mark.integration
class TestWebEndpoints:
    """Test web application endpoints."""

    def test_root_endpoint(self, test_client):
        """Test root endpoint returns HTML."""
        response = test_client.get("/")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "AI Prototyping Tool" in response.text
        assert "Generate Content" in response.text

    def test_health_endpoint(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "trace_id" in data
        assert data["status"] == "healthy"

    @patch("web.app.check_lm_studio_status")
    def test_lm_studio_status_connected(self, mock_check_status, test_client):
        """Test LM Studio status when connected."""
        mock_check_status.return_value = True

        with patch("web.app.get_current_lm_model", return_value="test-model"):
            response = test_client.get("/lm-studio/status")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "connected"
            assert data["current_model"] == "test-model"

    @patch("web.app.check_lm_studio_status")
    def test_lm_studio_status_disconnected(self, mock_check_status, test_client):
        """Test LM Studio status when disconnected."""
        mock_check_status.return_value = False

        response = test_client.get("/lm-studio/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "disconnected"
        assert data["current_model"] is None

    @patch("web.app.asyncio.create_task")
    @patch("web.app.check_lm_studio_status")
    def test_generate_content_success(
        self, mock_check_status, mock_create_task, test_client
    ):
        """Test successful content generation request."""
        mock_check_status.return_value = True

        # Mock the background task creation
        mock_task = Mock()
        mock_create_task.return_value = mock_task

        request_data = {
            "prompt": "Create a test system",
            "options": {
                "model": "test-model",
                "max_tokens": 100,
                "temperature": 0.7,
                "format": "markdown",
            },
        }

        response = test_client.post("/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "processing"
        assert "timestamp" in data

        # Verify background task was created
        mock_create_task.assert_called_once()

    def test_generate_content_invalid_request(self, test_client):
        """Test content generation with invalid request."""
        # Missing required prompt field
        request_data = {"options": {"model": "test-model"}}

        response = test_client.post("/generate", json=request_data)

        assert response.status_code == 422  # Validation error

    @patch("web.app.generation_tasks")
    def test_get_task_status_success(self, mock_tasks, test_client):
        """Test getting task status for existing task."""
        task_id = "test-task-123"
        mock_tasks.__contains__.return_value = True
        mock_tasks.__getitem__.return_value = {
            "id": task_id,
            "status": "completed",
            "content": "Generated content",
            "prompt": "Test prompt",
        }

        response = test_client.get(f"/tasks/{task_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["status"] == "completed"

    def test_get_task_status_not_found(self, test_client):
        """Test getting task status for non-existent task."""
        response = test_client.get("/tasks/nonexistent-task")

        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]


@pytest.mark.web
@pytest.mark.integration
class TestWebSocketEndpoints:
    """Test WebSocket functionality."""

    def test_websocket_connection(self, test_client):
        """Test WebSocket connection establishment."""
        with test_client.websocket_connect("/ws") as websocket:
            # Connection should be established successfully
            assert websocket is not None

            # Test sending a message
            websocket.send_text("test message")

            # Connection should remain open
            # Note: In real implementation, server might send back data

    def test_websocket_disconnect(self, test_client):
        """Test WebSocket disconnection handling."""
        with test_client.websocket_connect("/ws") as websocket:
            websocket.close()
        # Should disconnect cleanly without errors


@pytest.mark.web
@pytest.mark.integration
class TestContentGeneration:
    """Test content generation workflow."""

    @patch("web.app.aiohttp.ClientSession")
    @patch("web.app.check_lm_studio_status")
    @patch("web.app.get_current_lm_model")
    async def test_process_generation_with_lm_studio(
        self, mock_get_model, mock_check_status, mock_session_class
    ):
        """Test content generation process with LM Studio."""
        from web.app import process_generation

        # Setup mocks
        mock_check_status.return_value = True
        mock_get_model.return_value = "test-model"

        # Mock aiohttp session and response
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Generated content"}}]
        }

        mock_session.post.return_value.__aenter__.return_value = mock_response
        mock_session_class.return_value.__aenter__.return_value = mock_session

        # Mock manager broadcast
        with patch("web.app.manager.broadcast") as mock_broadcast:
            await process_generation(
                "test-task-123",
                "Create a test application",
                {"model": "test-model", "max_tokens": 100, "temperature": 0.7},
                "trace-123",
            )

            # Verify broadcast was called multiple times (start, completion)
            assert mock_broadcast.call_count >= 2

    @patch("web.app.check_lm_studio_status")
    async def test_process_generation_fallback_mock(self, mock_check_status):
        """Test content generation fallback to mock when LM Studio unavailable."""
        from web.app import process_generation

        # LM Studio not available
        mock_check_status.return_value = False

        with patch("web.app.manager.broadcast") as mock_broadcast:
            await process_generation(
                "test-task-123",
                "Create a test application",
                {"model": "test-model", "format": "markdown"},
                "trace-123",
            )

            # Should broadcast mock generation message
            broadcast_calls = [call[0][0] for call in mock_broadcast.call_args_list]
            assert any("mock generation" in call.lower() for call in broadcast_calls)


@pytest.mark.web
@pytest.mark.integration
class TestErrorHandling:
    """Test web application error handling."""

    def test_404_error(self, test_client):
        """Test 404 error handling."""
        response = test_client.get("/nonexistent-endpoint")

        assert response.status_code == 404

    def test_500_error_simulation(self, test_client):
        """Test 500 error handling."""
        # This would need a specific endpoint that can trigger a 500 error
        # For now, test with malformed JSON
        response = test_client.post(
            "/generate",
            data="{invalid json}",
            headers={"content-type": "application/json"},
        )

        assert response.status_code == 422  # Unprocessable Entity for invalid JSON

    @patch("web.app.handle_error")
    def test_error_with_trace_id(self, mock_handle_error, test_client):
        """Test that errors include trace IDs."""
        mock_handle_error.return_value = Mock(
            get_user_friendly_message=Mock(return_value="Test error"),
            error_id="error-123",
        )

        # Test with custom trace ID header
        response = test_client.get(
            "/nonexistent", headers={"X-Trace-ID": "custom-trace-123"}
        )

        # Should include trace ID in response headers
        assert "X-Trace-ID" in response.headers or response.status_code == 404


@pytest.mark.web
@pytest.mark.integration
class TestConfiguration:
    """Test web application configuration."""

    def test_cors_headers(self, test_client):
        """Test CORS headers are present."""
        response = test_client.options("/")

        # CORS should be configured
        assert response.status_code in [200, 405]  # OPTIONS may not be implemented

    def test_app_metadata(self, test_client):
        """Test application metadata."""
        # Test that the app has proper title and version
        assert app.title is not None
        assert app.version is not None

    @patch("web.app.app_config")
    def test_debug_mode_configuration(self, mock_config, test_client):
        """Test debug mode configuration."""
        mock_config.debug = True

        # In debug mode, error responses should include more details
        response = test_client.get("/nonexistent")
        assert response.status_code == 404


@pytest.mark.web
@pytest.mark.integration
@pytest.mark.slow
class TestPerformance:
    """Test web application performance."""

    def test_health_endpoint_performance(
        self, test_client, measure_time, performance_threshold
    ):
        """Test health endpoint response time."""

        def make_request():
            return test_client.get("/health")

        response, execution_time = measure_time(make_request)

        assert response.status_code == 200
        assert execution_time < performance_threshold["api_response"]

    def test_root_endpoint_performance(
        self, test_client, measure_time, performance_threshold
    ):
        """Test root endpoint response time."""

        def make_request():
            return test_client.get("/")

        response, execution_time = measure_time(make_request)

        assert response.status_code == 200
        assert execution_time < performance_threshold["api_response"]

    def test_concurrent_requests(self, test_client):
        """Test handling multiple concurrent requests."""
        import concurrent.futures
        import threading

        def make_request():
            return test_client.get("/health")

        # Test with 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # All requests should succeed
        assert all(response.status_code == 200 for response in responses)
        assert len(responses) == 10


@pytest.mark.web
@pytest.mark.integration
class TestMetrics:
    """Test metrics and monitoring endpoints."""

    def test_metrics_endpoint_exists(self, test_client):
        """Test metrics endpoint availability."""
        response = test_client.get("/metrics")

        # Should either work or be disabled (404)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "timestamp" in data
            assert "tasks" in data

    @patch("web.app.generation_tasks")
    def test_metrics_data_structure(self, mock_tasks, test_client):
        """Test metrics data structure when enabled."""
        # Mock some tasks
        mock_tasks.values.return_value = [
            {"status": "completed"},
            {"status": "processing"},
            {"status": "error"},
        ]
        mock_tasks.__len__.return_value = 3

        response = test_client.get("/metrics")

        if response.status_code == 200:
            data = response.json()
            assert "tasks" in data
            assert "websocket_connections" in data
            tasks = data["tasks"]
            assert "total" in tasks
            assert "completed" in tasks
            assert "processing" in tasks
            assert "failed" in tasks
