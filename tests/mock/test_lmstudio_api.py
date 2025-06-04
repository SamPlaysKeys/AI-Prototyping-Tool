"""
Mock tests for LM Studio API using httpx-mock.

Tests API interactions, response handling, error scenarios, etc.
"""

import pytest
from httpx import Response
from httpx_mock import HTTPXMock

from src.lmstudio_client import LMStudioClient, CompletionRequest


@pytest.mark.mock
class TestLMStudioAPI:
    """Test LM Studio API interactions with HTTPX mock."""

    def test_list_models_with_httpx_mock(self, httpx_mock: HTTPXMock):
        """Test listing models with mocked response."""
        client = LMStudioClient(base_url="http://testserver/v1")

        # Mock the models response
        httpx_mock.add_response(
            method="GET",
            url="http://testserver/v1/models",
            json={"data": [{"id": "mock-model-1"}, {"id": "mock-model-2"}]},
        )

        models = client.list_models()

        assert len(models) == 2
        assert models[0].id == "mock-model-1"
        assert models[1].id == "mock-model-2"

    def test_create_completion_with_httpx_mock(self, httpx_mock: HTTPXMock):
        """Test creating completion with mocked response."""
        client = LMStudioClient(base_url="http://testserver/v1")
        request = CompletionRequest(
            model="mock-model-1", prompt="Generate a test response", max_tokens=50
        )

        # Mock the completion response
        httpx_mock.add_response(
            method="POST",
            url="http://testserver/v1/completions",
            json={
                "id": "cmpl-mock-123",
                "model": "mock-model-1",
                "choices": [{"text": "Generated test response"}],
            },
        )

        response = client.create_completion(request)

        assert response.id == "cmpl-mock-123"
        assert response.choices[0].text == "Generated test response"

    def test_http_error_handling_with_httpx_mock(self, httpx_mock: HTTPXMock):
        """Test handling HTTP errors with mocked response."""
        client = LMStudioClient(base_url="http://testserver/v1")

        # Mock a 500 error response
        httpx_mock.add_response(
            method="GET",
            url="http://testserver/v1/models",
            status_code=500,
            json={"error": {"message": "Internal Server Error"}},
        )

        with pytest.raises(Exception) as excinfo:
            client.list_models()

        assert "Internal Server Error" in str(excinfo.value)

    def test_timeout_handling_with_httpx_mock(self, httpx_mock: HTTPXMock):
        """Test handling request timeouts with mocked response."""
        client = LMStudioClient(base_url="http://testserver/v1")

        # Mock a timeout
        httpx_mock.add_exception(
            method="GET",
            url="http://testserver/v1/models",
            exception=TimeoutError("Request timed out"),
        )

        with pytest.raises(Exception) as excinfo:
            client.list_models()

        assert "timed out" in str(excinfo.value)
