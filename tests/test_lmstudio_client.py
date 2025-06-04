"""Unit tests for LM Studio API client module."""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from requests import Response, HTTPError, ConnectionError, Timeout
from requests.exceptions import JSONDecodeError

from src.lmstudio_client import (
    LMStudioClient,
    LMStudioError,
    ErrorType,
    Model,
    CompletionRequest,
    CompletionResponse,
    CompletionChoice,
    CompletionUsage,
    RetryConfig,
    create_client,
    list_models,
    complete,
)


class TestModel:
    """Test Model class."""

    def test_model_from_dict(self):
        """Test Model creation from dictionary."""
        data = {
            "id": "test-model",
            "object": "model",
            "created": 1234567890,
            "owned_by": "openai",
        }
        model = Model.from_dict(data)

        assert model.id == "test-model"
        assert model.object == "model"
        assert model.created == 1234567890
        assert model.owned_by == "openai"

    def test_model_from_dict_minimal(self):
        """Test Model creation with minimal data."""
        data = {"id": "test-model"}
        model = Model.from_dict(data)

        assert model.id == "test-model"
        assert model.object == "model"
        assert model.created is None
        assert model.owned_by is None


class TestCompletionChoice:
    """Test CompletionChoice class."""

    def test_completion_choice_from_dict(self):
        """Test CompletionChoice creation from dictionary."""
        data = {"text": "Hello, world!", "index": 0, "finish_reason": "stop"}
        choice = CompletionChoice.from_dict(data)

        assert choice.text == "Hello, world!"
        assert choice.index == 0
        assert choice.finish_reason == "stop"
        assert choice.logprobs is None


class TestCompletionUsage:
    """Test CompletionUsage class."""

    def test_completion_usage_from_dict(self):
        """Test CompletionUsage creation from dictionary."""
        data = {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        usage = CompletionUsage.from_dict(data)

        assert usage.prompt_tokens == 10
        assert usage.completion_tokens == 20
        assert usage.total_tokens == 30


class TestCompletionResponse:
    """Test CompletionResponse class."""

    def test_completion_response_from_dict(self):
        """Test CompletionResponse creation from dictionary."""
        data = {
            "id": "cmpl-123",
            "object": "text_completion",
            "created": 1234567890,
            "model": "test-model",
            "choices": [{"text": "Hello, world!", "index": 0, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        }
        response = CompletionResponse.from_dict(data)

        assert response.id == "cmpl-123"
        assert response.object == "text_completion"
        assert response.created == 1234567890
        assert response.model == "test-model"
        assert len(response.choices) == 1
        assert response.choices[0].text == "Hello, world!"
        assert response.usage is not None
        assert response.usage.total_tokens == 30


class TestCompletionRequest:
    """Test CompletionRequest class."""

    def test_completion_request_to_dict(self):
        """Test CompletionRequest conversion to dictionary."""
        request = CompletionRequest(
            model="test-model", prompt="Hello", max_tokens=100, temperature=0.7
        )
        data = request.to_dict()

        assert data["model"] == "test-model"
        assert data["prompt"] == "Hello"
        assert data["max_tokens"] == 100
        assert data["temperature"] == 0.7
        assert "n" not in data  # None values should be excluded


class TestLMStudioError:
    """Test LMStudioError class."""

    def test_error_str_representation(self):
        """Test string representation of LMStudioError."""
        error = LMStudioError(
            message="Test error", error_type=ErrorType.API_ERROR, status_code=400
        )
        assert str(error) == "api_error: Test error"


class TestRetryConfig:
    """Test RetryConfig class."""

    def test_retry_config_defaults(self):
        """Test RetryConfig default values."""
        config = RetryConfig()

        assert config.max_retries == 3
        assert config.backoff_factor == 1.0
        assert config.max_backoff == 60.0
        assert config.retry_on_status == (500, 502, 503, 504, 429)

    def test_retry_config_custom(self):
        """Test RetryConfig with custom values."""
        config = RetryConfig(
            max_retries=5,
            backoff_factor=2.0,
            max_backoff=120.0,
            retry_on_status=(500, 503),
        )

        assert config.max_retries == 5
        assert config.backoff_factor == 2.0
        assert config.max_backoff == 120.0
        assert config.retry_on_status == (500, 503)


class TestLMStudioClient:
    """Test LMStudioClient class."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return LMStudioClient(
            base_url="http://localhost:1234/v1",
            timeout=30.0,
            retry_config=RetryConfig(max_retries=1),
        )

    @pytest.fixture
    def mock_response(self):
        """Create a mock response."""
        response = Mock(spec=Response)
        response.status_code = 200
        response.raise_for_status.return_value = None
        return response

    def test_client_initialization(self):
        """Test client initialization."""
        client = LMStudioClient(
            base_url="http://localhost:1234/v1", api_key="test-key", timeout=60.0
        )

        assert client.base_url == "http://localhost:1234/v1"
        assert client.api_key == "test-key"
        assert client.timeout == 60.0
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == "Bearer test-key"

    def test_client_initialization_no_api_key(self):
        """Test client initialization without API key."""
        client = LMStudioClient()

        assert client.base_url == "http://localhost:1234/v1"
        assert client.api_key is None
        assert "Authorization" not in client.session.headers

    def test_classify_error(self, client):
        """Test error classification."""
        response = Mock()

        response.status_code = 401
        assert client._classify_error(response) == ErrorType.AUTHENTICATION_ERROR

        response.status_code = 429
        assert client._classify_error(response) == ErrorType.RATE_LIMIT_ERROR

        response.status_code = 400
        assert client._classify_error(response) == ErrorType.CLIENT_ERROR

        response.status_code = 500
        assert client._classify_error(response) == ErrorType.SERVER_ERROR

        response.status_code = 200
        assert client._classify_error(response) == ErrorType.API_ERROR

    def test_handle_response_success(self, client, mock_response):
        """Test successful response handling."""
        test_data = {"test": "data"}
        mock_response.json.return_value = test_data

        result = client._handle_response(mock_response)
        assert result == test_data

    def test_handle_response_json_decode_error(self, client, mock_response):
        """Test handling of JSON decode error."""
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)

        with pytest.raises(LMStudioError) as exc_info:
            client._handle_response(mock_response)

        assert exc_info.value.error_type == ErrorType.API_ERROR
        assert "Invalid JSON response" in str(exc_info.value)

    def test_handle_response_http_error(self, client):
        """Test handling of HTTP error."""
        response = Mock()
        response.status_code = 400
        response.raise_for_status.side_effect = HTTPError("Bad Request")
        response.json.return_value = {"error": {"message": "Invalid request"}}

        with pytest.raises(LMStudioError) as exc_info:
            client._handle_response(response)

        assert exc_info.value.error_type == ErrorType.CLIENT_ERROR
        assert exc_info.value.status_code == 400
        assert "Invalid request" in str(exc_info.value)

    @patch("src.lmstudio_client.requests.Session.get")
    def test_list_models_success(self, mock_get, client):
        """Test successful model listing."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": [
                {"id": "model1", "object": "model"},
                {"id": "model2", "object": "model"},
            ]
        }
        mock_get.return_value = mock_response

        models = client.list_models()

        assert len(models) == 2
        assert models[0].id == "model1"
        assert models[1].id == "model2"
        mock_get.assert_called_once()

    @patch("src.lmstudio_client.requests.Session.get")
    def test_list_models_connection_error(self, mock_get, client):
        """Test model listing with connection error."""
        mock_get.side_effect = ConnectionError("Connection failed")

        with pytest.raises(LMStudioError) as exc_info:
            client.list_models()

        assert exc_info.value.error_type == ErrorType.NETWORK_ERROR
        assert "Connection error" in str(exc_info.value)

    @patch("src.lmstudio_client.requests.Session.post")
    def test_create_completion_success(self, mock_post, client):
        """Test successful completion creation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": "cmpl-123",
            "object": "text_completion",
            "created": 1234567890,
            "model": "test-model",
            "choices": [{"text": "Hello, world!", "index": 0, "finish_reason": "stop"}],
        }
        mock_post.return_value = mock_response

        request = CompletionRequest(model="test-model", prompt="Hello")
        response = client.create_completion(request)

        assert response.id == "cmpl-123"
        assert response.model == "test-model"
        assert len(response.choices) == 1
        assert response.choices[0].text == "Hello, world!"
        mock_post.assert_called_once()

    def test_create_completion_with_stream(self, client):
        """Test completion creation with streaming (should raise error)."""
        request = CompletionRequest(model="test-model", prompt="Hello", stream=True)

        with pytest.raises(ValueError) as exc_info:
            client.create_completion(request)

        assert "Streaming is not supported" in str(exc_info.value)

    @patch("src.lmstudio_client.requests.Session.post")
    def test_create_completion_simple(self, mock_post, client):
        """Test simple completion creation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": "cmpl-123",
            "object": "text_completion",
            "created": 1234567890,
            "model": "test-model",
            "choices": [{"text": "Hello, world!", "index": 0, "finish_reason": "stop"}],
        }
        mock_post.return_value = mock_response

        response = client.create_completion_simple(
            model="test-model", prompt="Hello", max_tokens=100, temperature=0.7
        )

        assert response.id == "cmpl-123"
        mock_post.assert_called_once()

    @patch("src.lmstudio_client.LMStudioClient.list_models")
    def test_health_check_healthy(self, mock_list_models, client):
        """Test health check when service is healthy."""
        mock_list_models.return_value = [Mock(), Mock()]

        health = client.health_check()

        assert health["status"] == "healthy"
        assert health["models_count"] == 2
        assert health["base_url"] == client.base_url

    @patch("src.lmstudio_client.LMStudioClient.list_models")
    def test_health_check_unhealthy(self, mock_list_models, client):
        """Test health check when service is unhealthy."""
        error = LMStudioError(
            message="Connection failed", error_type=ErrorType.NETWORK_ERROR
        )
        mock_list_models.side_effect = error

        health = client.health_check()

        assert health["status"] == "unhealthy"
        assert health["error_type"] == "network_error"
        assert "Connection failed" in health["error"]

    @patch("src.lmstudio_client.time.sleep")
    @patch("src.lmstudio_client.requests.Session.get")
    def test_retry_logic_with_server_error(self, mock_get, mock_sleep, client):
        """Test retry logic with server errors."""
        # First call fails with 500, second succeeds
        error_response = Mock()
        error_response.status_code = 500
        error_response.raise_for_status.side_effect = HTTPError("Internal Server Error")
        error_response.json.return_value = {"error": {"message": "Server error"}}

        success_response = Mock()
        success_response.status_code = 200
        success_response.raise_for_status.return_value = None
        success_response.json.return_value = {"data": []}

        mock_get.side_effect = [error_response, success_response]

        result = client._make_request("GET", "/models")

        assert result == {"data": []}
        assert mock_get.call_count == 2
        mock_sleep.assert_called_once()  # Should have slept before retry

    @patch("src.lmstudio_client.requests.Session.get")
    def test_retry_logic_max_retries_exceeded(self, mock_get, client):
        """Test retry logic when max retries exceeded."""
        error_response = Mock()
        error_response.status_code = 500
        error_response.raise_for_status.side_effect = HTTPError("Internal Server Error")
        error_response.json.return_value = {"error": {"message": "Server error"}}

        mock_get.return_value = error_response

        with pytest.raises(LMStudioError) as exc_info:
            client._make_request("GET", "/models")

        assert exc_info.value.error_type == ErrorType.SERVER_ERROR
        # Should try initial + max_retries (1) = 2 times
        assert mock_get.call_count == 2

    @patch("src.lmstudio_client.requests.Session.get")
    def test_retry_logic_no_retry_on_client_error(self, mock_get, client):
        """Test that client errors don't trigger retries."""
        error_response = Mock()
        error_response.status_code = 400
        error_response.raise_for_status.side_effect = HTTPError("Bad Request")
        error_response.json.return_value = {"error": {"message": "Bad request"}}

        mock_get.return_value = error_response

        with pytest.raises(LMStudioError) as exc_info:
            client._make_request("GET", "/models")

        assert exc_info.value.error_type == ErrorType.CLIENT_ERROR
        # Should only try once (no retries for client errors)
        assert mock_get.call_count == 1

    def test_context_manager(self):
        """Test client as context manager."""
        with LMStudioClient() as client:
            assert isinstance(client, LMStudioClient)
        # Session should be closed after exiting context
        assert client.session.close

    def test_unsupported_http_method(self, client):
        """Test unsupported HTTP method."""
        with pytest.raises(ValueError) as exc_info:
            client._make_request("DELETE", "/models")

        assert "Unsupported HTTP method: DELETE" in str(exc_info.value)


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_create_client(self):
        """Test create_client function."""
        client = create_client(base_url="http://localhost:1234/v1", api_key="test-key")

        assert isinstance(client, LMStudioClient)
        assert client.base_url == "http://localhost:1234/v1"
        assert client.api_key == "test-key"

    @patch("src.lmstudio_client.LMStudioClient.list_models")
    def test_list_models_function(self, mock_list_models):
        """Test list_models convenience function."""
        expected_models = [Mock(spec=Model), Mock(spec=Model)]
        mock_list_models.return_value = expected_models

        models = list_models()

        assert models == expected_models
        mock_list_models.assert_called_once()

    @patch("src.lmstudio_client.LMStudioClient.create_completion_simple")
    def test_complete_function(self, mock_create_completion):
        """Test complete convenience function."""
        expected_response = Mock(spec=CompletionResponse)
        mock_create_completion.return_value = expected_response

        response = complete(model="test-model", prompt="Hello", max_tokens=100)

        assert response == expected_response
        mock_create_completion.assert_called_once_with(
            model="test-model", prompt="Hello", max_tokens=100
        )


class TestIntegration:
    """Integration tests with real HTTP mocking."""

    @patch("src.lmstudio_client.requests.Session")
    def test_full_integration_flow(self, mock_session_class):
        """Test full integration flow."""
        # Setup mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Mock models response
        models_response = Mock()
        models_response.status_code = 200
        models_response.raise_for_status.return_value = None
        models_response.json.return_value = {
            "data": [{"id": "gpt-3.5-turbo", "object": "model"}]
        }

        # Mock completion response
        completion_response = Mock()
        completion_response.status_code = 200
        completion_response.raise_for_status.return_value = None
        completion_response.json.return_value = {
            "id": "cmpl-123",
            "object": "text_completion",
            "created": 1234567890,
            "model": "gpt-3.5-turbo",
            "choices": [
                {
                    "text": "Hello, how can I help you?",
                    "index": 0,
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 10, "total_tokens": 15},
        }

        mock_session.get.return_value = models_response
        mock_session.post.return_value = completion_response

        # Test the flow
        with LMStudioClient() as client:
            # List models
            models = client.list_models()
            assert len(models) == 1
            assert models[0].id == "gpt-3.5-turbo"

            # Create completion
            response = client.create_completion_simple(
                model="gpt-3.5-turbo", prompt="Hello", max_tokens=50
            )

            assert response.id == "cmpl-123"
            assert response.choices[0].text == "Hello, how can I help you?"
            assert response.usage.total_tokens == 15

        # Verify calls
        mock_session.get.assert_called_once()
        mock_session.post.assert_called_once()
