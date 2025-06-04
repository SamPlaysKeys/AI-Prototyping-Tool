# LM Studio API Client

A comprehensive Python client for LM Studio's OpenAI-compatible HTTP API at `http://localhost:1234/v1/`.

## Features

- **Model enumeration endpoint** - List available models
- **Completion endpoint** - Generate text completions
- **Request building and response parsing** - Type-safe request/response handling
- **Retry logic with exponential backoff** - Robust error handling with configurable retries
- **Error classification** - Distinguishes between network, API, and other error types
- **Type signatures** - Full type hints for better IDE support
- **Comprehensive unit tests** - 31 test cases with mocked HTTP responses

## Quick Start

```python
from src.lmstudio_client import LMStudioClient

# Create a client and use it
with LMStudioClient() as client:
    # List available models
    models = client.list_models()
    print(f"Available models: {[m.id for m in models]}")

    # Generate a completion
    response = client.create_completion_simple(
        model=models[0].id,
        prompt="Hello, how are you?",
        max_tokens=50,
        temperature=0.7
    )

    print(f"Response: {response.choices[0].text}")
```

## API Coverage

✅ **Model enumeration endpoint** (`/v1/models`)
✅ **Completion endpoint** (`/v1/completions`)
✅ **Request building and response parsing**
✅ **Retry logic with exponential backoff**
✅ **Error classification** (network vs API errors)
✅ **Type signatures** throughout
✅ **Unit tests** with mocked HTTP responses

## Testing

Run the test suite:

```bash
python -m pytest tests/test_lmstudio_client.py -v
```

All 31 tests pass, covering:
- Data model serialization/deserialization
- HTTP client configuration
- Error handling and classification
- Retry logic with exponential backoff
- Integration scenarios

See `docs/lmstudio_client.md` for complete documentation.

# LM Studio API Client

A comprehensive Python client for LM Studio's OpenAI-compatible HTTP API at `http://localhost:1234/v1/`.

## Features

- **Model enumeration endpoint** - List available models
- **Completion endpoint** - Generate text completions
- **Request building and response parsing** - Type-safe request/response handling
- **Retry logic with exponential backoff** - Robust error handling with configurable retries
- **Error classification** - Distinguishes between network, API, and other error types
- **Type signatures** - Full type hints for better IDE support
- **Comprehensive unit tests** - 31 test cases with mocked HTTP responses

## Installation

The LM Studio client is part of this project. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from src.lmstudio_client import LMStudioClient, LMStudioError

# Create a client
with LMStudioClient() as client:
    # List available models
    models = client.list_models()
    print(f"Available models: {[m.id for m in models]}")

    # Generate a completion
    response = client.create_completion_simple(
        model=models[0].id,
        prompt="Hello, how are you?",
        max_tokens=50,
        temperature=0.7
    )

    print(f"Response: {response.choices[0].text}")
```

### Convenience Functions

```python
from src.lmstudio_client import list_models, complete

# Quick model listing
models = list_models()

# Quick completion
response = complete(
    model="your-model-id",
    prompt="Tell me a joke",
    max_tokens=100
)
```

## Advanced Usage

### Custom Configuration

```python
from src.lmstudio_client import LMStudioClient, RetryConfig

# Custom retry configuration
retry_config = RetryConfig(
    max_retries=5,
    backoff_factor=2.0,
    max_backoff=120.0,
    retry_on_status=(500, 502, 503, 504, 429)
)

# Client with custom settings
client = LMStudioClient(
    base_url="http://localhost:1234/v1",
    api_key="your-api-key",  # Optional for local LM Studio
    timeout=60.0,
    retry_config=retry_config
)
```

### Detailed Completion Requests

```python
from src.lmstudio_client import CompletionRequest

# Create a detailed completion request
request = CompletionRequest(
    model="your-model-id",
    prompt="Write a short story about AI:",
    max_tokens=200,
    temperature=0.8,
    top_p=0.9,
    frequency_penalty=0.1,
    presence_penalty=0.1,
    stop=["\n\n", "THE END"]
)

response = client.create_completion(request)
```

### Error Handling

```python
from src.lmstudio_client import LMStudioError, ErrorType

try:
    models = client.list_models()
except LMStudioError as e:
    print(f"Error type: {e.error_type.value}")
    print(f"Message: {e.message}")
    if e.status_code:
        print(f"HTTP status: {e.status_code}")
```

## API Reference

### LMStudioClient

Main client class for interacting with LM Studio's API.

#### Constructor

```python
LMStudioClient(
    base_url: str = "http://localhost:1234/v1",
    api_key: Optional[str] = None,
    timeout: float = 30.0,
    retry_config: Optional[RetryConfig] = None
)
```

#### Methods

- **`list_models() -> List[Model]`** - List available models
- **`create_completion(request: CompletionRequest) -> CompletionResponse`** - Create a completion
- **`create_completion_simple(model, prompt, **kwargs) -> CompletionResponse`** - Simplified completion
- **`health_check() -> Dict[str, Any]`** - Check server health
- **`close() -> None`** - Close HTTP session

### Data Classes

#### Model
```python
@dataclass
class Model:
    id: str
    object: str = "model"
    created: Optional[int] = None
    owned_by: Optional[str] = None
    permission: Optional[List[Dict[str, Any]]] = None
    root: Optional[str] = None
    parent: Optional[str] = None
```

#### CompletionRequest
```python
@dataclass
class CompletionRequest:
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
```

#### CompletionResponse
```python
@dataclass
class CompletionResponse:
    id: str
    object: str
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: Optional[CompletionUsage] = None
```

### Error Types

The client classifies errors into the following types:

- **`NETWORK_ERROR`** - Connection issues, DNS failures
- **`API_ERROR`** - General API errors
- **`TIMEOUT_ERROR`** - Request timeouts
- **`AUTHENTICATION_ERROR`** - 401 Unauthorized
- **`RATE_LIMIT_ERROR`** - 429 Too Many Requests
- **`SERVER_ERROR`** - 5xx server errors
- **`CLIENT_ERROR`** - 4xx client errors (except 401, 429)
- **`UNKNOWN_ERROR`** - Unclassified errors

### Retry Configuration

```python
class RetryConfig:
    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        max_backoff: float = 60.0,
        retry_on_status: Tuple[int, ...] = (500, 502, 503, 504, 429)
    ):
```

## Testing

Run the comprehensive test suite:

```bash
python -m pytest tests/test_lmstudio_client.py -v
```

The test suite includes:
- Unit tests for all data classes
- Client initialization and configuration tests
- HTTP request/response handling tests
- Error classification and handling tests
- Retry logic tests with exponential backoff
- Integration tests with mocked HTTP responses

## Example Usage

See the complete example in `examples/lmstudio_example.py`:

```bash
python examples/lmstudio_example.py
```

This example demonstrates:
1. Health checking
2. Model listing
3. Simple completions
4. Advanced completions with custom configuration
5. Error handling

## Prerequisites

Before using the client, ensure:

1. **LM Studio is running** on `http://localhost:1234`
2. **A model is loaded** in LM Studio
3. **The API server is enabled** in LM Studio settings

## Notes

- The client is designed for local LM Studio instances and doesn't require an API key by default
- Streaming completions are not supported in the current implementation
- The client uses exponential backoff with jitter for robust retry handling
- All HTTP operations are handled through a configured session with retry adapters
- Context manager support ensures proper resource cleanup

## Contributing

When contributing to the LM Studio client:

1. Add type hints to all new functions
2. Write unit tests for new functionality
3. Update documentation for new features
4. Follow the existing error handling patterns
5. Ensure backward compatibility
