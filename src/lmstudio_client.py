"""LM Studio API client module.

This module provides a Python client for LM Studio's OpenAI-compatible HTTP API.
It includes model enumeration, completion endpoints, retry logic, and error handling.
"""

import json
import time
import random
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ErrorType(Enum):
    """Classification of error types."""

    NETWORK_ERROR = "network_error"
    API_ERROR = "api_error"
    TIMEOUT_ERROR = "timeout_error"
    AUTHENTICATION_ERROR = "authentication_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    SERVER_ERROR = "server_error"
    CLIENT_ERROR = "client_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class LMStudioError(Exception):
    """Custom exception for LM Studio API errors."""

    message: str
    error_type: ErrorType
    status_code: Optional[int] = None
    response_data: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        return f"{self.error_type.value}: {self.message}"


@dataclass
class Model:
    """Represents a model from the models endpoint."""

    id: str
    object: str = "model"
    created: Optional[int] = None
    owned_by: Optional[str] = None
    permission: Optional[List[Dict[str, Any]]] = None
    root: Optional[str] = None
    parent: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Model":
        """Create Model instance from dictionary."""
        return cls(
            id=data["id"],
            object=data.get("object", "model"),
            created=data.get("created"),
            owned_by=data.get("owned_by"),
            permission=data.get("permission"),
            root=data.get("root"),
            parent=data.get("parent"),
        )


@dataclass
class CompletionChoice:
    """Represents a completion choice."""

    text: str
    index: int
    logprobs: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompletionChoice":
        """Create CompletionChoice instance from dictionary."""
        return cls(
            text=data["text"],
            index=data["index"],
            logprobs=data.get("logprobs"),
            finish_reason=data.get("finish_reason"),
        )


@dataclass
class CompletionUsage:
    """Represents token usage information."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompletionUsage":
        """Create CompletionUsage instance from dictionary."""
        return cls(
            prompt_tokens=data["prompt_tokens"],
            completion_tokens=data["completion_tokens"],
            total_tokens=data["total_tokens"],
        )


@dataclass
class CompletionResponse:
    """Represents a completion response."""

    id: str
    object: str
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: Optional[CompletionUsage] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompletionResponse":
        """Create CompletionResponse instance from dictionary."""
        choices = [CompletionChoice.from_dict(choice) for choice in data["choices"]]
        usage = None
        if "usage" in data and data["usage"]:
            usage = CompletionUsage.from_dict(data["usage"])

        return cls(
            id=data["id"],
            object=data["object"],
            created=data["created"],
            model=data["model"],
            choices=choices,
            usage=usage,
        )


@dataclass
class CompletionRequest:
    """Represents a completion request."""

    model: str
    prompt: Union[str, List[str]]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    n: Optional[int] = None
    stream: Optional[bool] = None
    logprobs: Optional[int] = None
    echo: Optional[bool] = None
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    best_of: Optional[int] = None
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None
    suffix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


class RetryConfig:
    """Configuration for retry logic."""

    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        max_backoff: float = 60.0,
        retry_on_status: Tuple[int, ...] = (500, 502, 503, 504, 429),
    ):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff
        self.retry_on_status = retry_on_status


class LMStudioClient:
    """Client for LM Studio's OpenAI-compatible API."""

    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        retry_config: Optional[RetryConfig] = None,
    ):
        """Initialize the LM Studio client.

        Args:
            base_url: Base URL for the LM Studio API
            api_key: API key (optional for local LM Studio)
            timeout: Request timeout in seconds
            retry_config: Retry configuration
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.retry_config = retry_config or RetryConfig()

        # Setup session with retry adapter
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.retry_config.max_retries,
            status_forcelist=self.retry_config.retry_on_status,
            backoff_factor=self.retry_config.backoff_factor,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "lmstudio-python-client/1.0.0",
            }
        )

        if self.api_key:
            self.session.headers["Authorization"] = f"Bearer {self.api_key}"

    def _classify_error(self, response: requests.Response) -> ErrorType:
        """Classify the type of error based on response."""
        status_code = response.status_code

        if status_code == 401:
            return ErrorType.AUTHENTICATION_ERROR
        elif status_code == 429:
            return ErrorType.RATE_LIMIT_ERROR
        elif 400 <= status_code < 500:
            return ErrorType.CLIENT_ERROR
        elif 500 <= status_code < 600:
            return ErrorType.SERVER_ERROR
        else:
            return ErrorType.API_ERROR

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle HTTP response and extract JSON data."""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            raise LMStudioError(
                message=f"Invalid JSON response: {str(e)}",
                error_type=ErrorType.API_ERROR,
                status_code=response.status_code,
            )
        except requests.exceptions.HTTPError as e:
            error_type = self._classify_error(response)
            try:
                error_data = response.json()
                message = error_data.get("error", {}).get("message", str(e))
            except (json.JSONDecodeError, AttributeError):
                message = str(e)

            raise LMStudioError(
                message=message,
                error_type=error_type,
                status_code=response.status_code,
                response_data=error_data if "error_data" in locals() else None,
            )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic and error handling."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                if method.upper() == "GET":
                    response = self.session.get(
                        url, params=params, timeout=self.timeout
                    )
                elif method.upper() == "POST":
                    response = self.session.post(
                        url, json=data, params=params, timeout=self.timeout
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                return self._handle_response(response)

            except requests.exceptions.ConnectionError as e:
                if attempt == self.retry_config.max_retries:
                    raise LMStudioError(
                        message=f"Connection error: {str(e)}",
                        error_type=ErrorType.NETWORK_ERROR,
                    )
            except requests.exceptions.Timeout as e:
                if attempt == self.retry_config.max_retries:
                    raise LMStudioError(
                        message=f"Request timeout: {str(e)}",
                        error_type=ErrorType.TIMEOUT_ERROR,
                    )
            except LMStudioError as e:
                # Re-raise LMStudioError without retry for client errors
                if e.error_type in [
                    ErrorType.CLIENT_ERROR,
                    ErrorType.AUTHENTICATION_ERROR,
                ]:
                    raise
                if attempt == self.retry_config.max_retries:
                    raise

            # Exponential backoff with jitter
            if attempt < self.retry_config.max_retries:
                backoff_time = min(
                    self.retry_config.backoff_factor * (2**attempt),
                    self.retry_config.max_backoff,
                )
                # Add jitter (±25%)
                jitter = backoff_time * 0.25 * (2 * random.random() - 1)
                time.sleep(backoff_time + jitter)

        raise LMStudioError(
            message="Max retries exceeded", error_type=ErrorType.UNKNOWN_ERROR
        )

    def list_models(self) -> List[Model]:
        """List available models.

        Returns:
            List of Model objects

        Raises:
            LMStudioError: If the request fails
        """
        response_data = self._make_request("GET", "/models")
        models = [
            Model.from_dict(model_data) for model_data in response_data.get("data", [])
        ]
        return models

    def create_completion(self, request: CompletionRequest) -> CompletionResponse:
        """Create a completion.

        Args:
            request: CompletionRequest object with completion parameters

        Returns:
            CompletionResponse object

        Raises:
            LMStudioError: If the request fails
        """
        if request.stream:
            raise ValueError(
                "Streaming is not supported in this method. Use create_completion_stream instead."
            )

        response_data = self._make_request(
            "POST", "/completions", data=request.to_dict()
        )
        return CompletionResponse.from_dict(response_data)

    def create_completion_simple(
        self,
        model: str,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> CompletionResponse:
        """Create a completion with simplified parameters.

        Args:
            model: Model ID to use
            prompt: Text prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional completion parameters

        Returns:
            CompletionResponse object

        Raises:
            LMStudioError: If the request fails
        """
        request = CompletionRequest(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )
        return self.create_completion(request)

    def health_check(self) -> Dict[str, Any]:
        """Check if the LM Studio server is healthy.

        Returns:
            Dictionary with health status

        Raises:
            LMStudioError: If the health check fails
        """
        try:
            models = self.list_models()
            return {
                "status": "healthy",
                "models_count": len(models),
                "base_url": self.base_url,
            }
        except LMStudioError as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "error_type": e.error_type.value,
                "base_url": self.base_url,
            }

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Convenience functions
def create_client(
    base_url: str = "http://localhost:1234/v1", api_key: Optional[str] = None, **kwargs
) -> LMStudioClient:
    """Create and return a new LMStudioClient instance.

    Args:
        base_url: Base URL for the LM Studio API
        api_key: API key (optional for local LM Studio)
        **kwargs: Additional client configuration

    Returns:
        LMStudioClient instance
    """
    return LMStudioClient(base_url=base_url, api_key=api_key, **kwargs)


def list_models(
    base_url: str = "http://localhost:1234/v1", api_key: Optional[str] = None
) -> List[Model]:
    """Quick function to list models without creating a persistent client.

    Args:
        base_url: Base URL for the LM Studio API
        api_key: API key (optional for local LM Studio)

    Returns:
        List of Model objects
    """
    with create_client(base_url=base_url, api_key=api_key) as client:
        return client.list_models()


def complete(
    model: str,
    prompt: str,
    base_url: str = "http://localhost:1234/v1",
    api_key: Optional[str] = None,
    **kwargs,
) -> CompletionResponse:
    """Quick function to create a completion without creating a persistent client.

    Args:
        model: Model ID to use
        prompt: Text prompt
        base_url: Base URL for the LM Studio API
        api_key: API key (optional for local LM Studio)
        **kwargs: Additional completion parameters

    Returns:
        CompletionResponse object
    """
    with create_client(base_url=base_url, api_key=api_key) as client:
        return client.create_completion_simple(model=model, prompt=prompt, **kwargs)
