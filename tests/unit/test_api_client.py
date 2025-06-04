"""
Unit tests for the LM Studio API client module.

Tests functionality like model listing, completion requests, error handling, etc.
"""

import pytest
from unittest.mock import Mock, patch
from requests.exceptions import RequestException

from src.lmstudio_client import LMStudioClient, LMStudioError, CompletionRequest


@pytest.fixture
def client():
    return LMStudioClient(
        base_url="http://localhost:1234/v1", api_key="test-key", timeout=10
    )


@pytest.mark.unit
class TestLMStudioClient:
    def test_list_models_success(self, client, mock_requests_session):
        """Test successful model listing."""
        mock_requests_session.get.return_value.json.return_value = {
            "data": [{"id": "model1", "object": "model"}]
        }
        models = client.list_models()
        assert len(models) == 1
        assert models[0].id == "model1"

    def test_create_completion_success(
        self, client, mock_requests_session, sample_completion_request
    ):
        """Test successful completion request."""
        mock_requests_session.post.return_value.json.return_value = {
            "id": "cmpl-123",
            "choices": [{"text": "Test response"}],
            "model": "model1",
        }
        response = client.create_completion(sample_completion_request)
        assert response.id == "cmpl-123"
        assert response.choices[0].text == "Test response"

    def test_request_timeout_error(self, client, mock_requests_session):
        """Test handling of request timeout error."""
        mock_requests_session.get.side_effect = RequestException("Request timed out")
        with pytest.raises(LMStudioError, match="Request timed out"):
            client.list_models()

    def test_authentication_error(self, client, mock_requests_session):
        """Test handling of authentication error."""
        mock_requests_session.get.return_value.status_code = 401
        with pytest.raises(LMStudioError, match="authentication error"):
            client.list_models()
