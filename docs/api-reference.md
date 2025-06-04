# API Reference

Complete API documentation for the AI Prototyping Tool, covering both the Python API and REST API interfaces.

## 🐍 Python API

### Core Classes

#### Orchestrator

Main class for coordinating the generation process.

```python
from src.orchestrator import Orchestrator
from src.prompt_schema import PromptData

# Initialize orchestrator
orchestrator = Orchestrator(config_manager)

# Generate content
result = orchestrator.generate_content(prompt_data)
```

**Methods**:

##### `generate_content(prompt_data: PromptData) -> GenerationResult`

Generates documentation based on the provided prompt data.

**Parameters**:
- `prompt_data` (PromptData): Structured prompt information

**Returns**:
- `GenerationResult`: Object containing generated content and metadata

**Raises**:
- `GenerationError`: If generation fails
- `ValidationError`: If prompt data is invalid

**Example**:
```python
from src.prompt_schema import PromptData

prompt_data = PromptData(
    text="Create a task management app",
    deliverable_types=["problem_statement", "personas"],
    max_tokens=2048,
    temperature=0.7
)

result = orchestrator.generate_content(prompt_data)
print(result.content)
```

##### `get_available_deliverables() -> List[str]`

Returns list of available deliverable types.

**Returns**:
- `List[str]`: Available deliverable type names

**Example**:
```python
deliverables = orchestrator.get_available_deliverables()
print(deliverables)  # ['problem_statement', 'personas', ...]
```

#### LMStudioClient

Client for interacting with LM Studio API.

```python
from src.lmstudio_client import LMStudioClient

# Initialize client
client = LMStudioClient(
    base_url="http://localhost:1234/v1",
    api_key=None  # Optional
)
```

**Methods**:

##### `complete(prompt: str, **kwargs) -> str`

Generates text completion for the given prompt.

**Parameters**:
- `prompt` (str): Input prompt text
- `**kwargs`: Additional generation parameters
  - `max_tokens` (int): Maximum tokens to generate
  - `temperature` (float): Sampling temperature (0.0-1.0)
  - `top_p` (float): Nucleus sampling parameter (0.0-1.0)
  - `stop` (List[str]): Stop sequences

**Returns**:
- `str`: Generated text completion

**Raises**:
- `ConnectionError`: If unable to connect to LM Studio
- `ModelError`: If model is not available
- `APIError`: If API request fails

**Example**:
```python
response = client.complete(
    "Write a problem statement for:",
    max_tokens=1024,
    temperature=0.5
)
print(response)
```

##### `list_models() -> List[Dict[str, Any]]`

Returns list of available models in LM Studio.

**Returns**:
- `List[Dict]`: Model information dictionaries

**Example**:
```python
models = client.list_models()
for model in models:
    print(f"Model: {model['id']}, Object: {model['object']}")
```

##### `health_check() -> bool`

Checks if LM Studio is accessible and responding.

**Returns**:
- `bool`: True if healthy, False otherwise

**Example**:
```python
if client.health_check():
    print("LM Studio is running")
else:
    print("LM Studio is not accessible")
```

##### `stream_completion(prompt: str, **kwargs) -> Iterator[str]`

Streams text completion in real-time.

**Parameters**:
- `prompt` (str): Input prompt text
- `**kwargs`: Generation parameters (same as `complete`)

**Returns**:
- `Iterator[str]`: Stream of text chunks

**Example**:
```python
for chunk in client.stream_completion("Tell me about AI"):
    print(chunk, end="", flush=True)
```

#### TemplateRenderer

Handles template processing and rendering.

```python
from src.template_renderer import TemplateRenderer

# Initialize renderer
renderer = TemplateRenderer(template_dir="templates")
```

**Methods**:

##### `render_deliverable(template_name: str, context: Dict[str, Any]) -> str`

Renders a deliverable template with the provided context.

**Parameters**:
- `template_name` (str): Name of the template file
- `context` (Dict): Template context variables

**Returns**:
- `str`: Rendered template content

**Raises**:
- `TemplateNotFoundError`: If template file doesn't exist
- `TemplateRenderError`: If rendering fails

**Example**:
```python
context = {
    "project_name": "Task Manager",
    "generated_content": "A comprehensive task management solution...",
    "timestamp": "2024-01-15 10:30:00"
}

rendered = renderer.render_deliverable("problem_statement.md", context)
print(rendered)
```

##### `get_available_templates() -> List[str]`

Returns list of available template files.

**Returns**:
- `List[str]`: Template file names

**Example**:
```python
templates = renderer.get_available_templates()
print(templates)  # ['problem_statement.md', 'personas.md', ...]
```

#### ConfigManager

Manages application configuration.

```python
from src.config_manager import ConfigManager

# Initialize with configuration sources
config = ConfigManager(
    config_file="config.json",
    env_prefix="AI_PROTO_"
)
```

**Methods**:

##### `get(key: str, default: Any = None) -> Any`

Retrieves configuration value by key.

**Parameters**:
- `key` (str): Configuration key (supports dot notation)
- `default` (Any): Default value if key not found

**Returns**:
- `Any`: Configuration value

**Example**:
```python
lm_studio_url = config.get("lm_studio.url", "http://localhost:1234/v1")
max_tokens = config.get("generation.max_tokens", 2048)
```

##### `set(key: str, value: Any) -> None`

Sets configuration value.

**Parameters**:
- `key` (str): Configuration key
- `value` (Any): Value to set

**Example**:
```python
config.set("generation.temperature", 0.5)
config.set("output.format", "markdown")
```

##### `save(file_path: str) -> None`

Saves current configuration to file.

**Parameters**:
- `file_path` (str): Path to save configuration

**Example**:
```python
config.save("my_config.json")
```

### Data Structures

#### PromptData

Structured representation of generation input.

```python
from src.prompt_schema import PromptData

prompt_data = PromptData(
    text="Create a social media platform",
    deliverable_types=["problem_statement", "personas"],
    max_tokens=4096,
    temperature=0.7,
    top_p=0.9,
    model="mistral-7b-instruct",
    output_format="markdown",
    merge=True
)
```

**Fields**:
- `text` (str): Main prompt text
- `deliverable_types` (List[str]): Types of deliverables to generate
- `max_tokens` (int): Maximum tokens per generation
- `temperature` (float): Sampling temperature
- `top_p` (float): Nucleus sampling parameter
- `model` (str): Model identifier
- `output_format` (str): Output format ("markdown" or "json")
- `merge` (bool): Whether to merge deliverables

#### GenerationResult

Result of a generation operation.

```python
class GenerationResult:
    content: Dict[str, str]      # Generated content by deliverable type
    metadata: Dict[str, Any]     # Generation metadata
    timestamp: datetime          # Generation timestamp
    success: bool                # Whether generation succeeded
    errors: List[str]            # Any errors encountered
```

**Example Usage**:
```python
result = orchestrator.generate_content(prompt_data)

if result.success:
    for deliverable_type, content in result.content.items():
        print(f"\n=== {deliverable_type} ===")
        print(content)
else:
    print("Generation failed:")
    for error in result.errors:
        print(f"- {error}")
```

## 🌐 REST API

### Base URL

```
http://localhost:8000
```

### Authentication

Currently no authentication required for local development.

### Endpoints

#### POST `/generate`

Generates documentation based on a prompt.

**Request Body**:
```json
{
  "prompt": "Create a task management application",
  "deliverable_types": ["problem_statement", "personas"],
  "max_tokens": 2048,
  "temperature": 0.7,
  "top_p": 0.9,
  "model": "mistral-7b-instruct",
  "output_format": "markdown",
  "merge": true
}
```

**Response**:
```json
{
  "success": true,
  "content": {
    "problem_statement": "# Problem Statement\n\n...",
    "personas": "# Personas\n\n..."
  },
  "metadata": {
    "generation_time": 15.3,
    "tokens_used": 1847,
    "model_used": "mistral-7b-instruct"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes**:
- `200 OK`: Generation successful
- `400 Bad Request`: Invalid request parameters
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Generation failed
- `503 Service Unavailable`: LM Studio not available

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a simple blog platform",
    "deliverable_types": ["problem_statement"],
    "max_tokens": 1024
  }'
```

#### GET `/models`

Returns list of available models.

**Response**:
```json
{
  "models": [
    {
      "id": "mistral-7b-instruct",
      "object": "model",
      "created": 1234567890,
      "owned_by": "local"
    }
  ]
}
```

**cURL Example**:
```bash
curl "http://localhost:8000/models"
```

#### GET `/health`

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "lm_studio": {
    "connected": true,
    "url": "http://localhost:1234/v1",
    "models_available": 1
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes**:
- `200 OK`: Service healthy
- `503 Service Unavailable`: Service unhealthy

#### GET `/deliverables`

Returns available deliverable types.

**Response**:
```json
{
  "deliverable_types": [
    {
      "name": "problem_statement",
      "description": "Problem Statement",
      "template": "problem_statement.md"
    },
    {
      "name": "personas",
      "description": "Personas",
      "template": "personas.md"
    }
  ]
}
```

#### WebSocket `/ws`

Real-time updates during generation.

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

**Message Format**:
```json
{
  "type": "status",
  "data": {
    "status": "generating",
    "progress": 0.5,
    "current_deliverable": "problem_statement",
    "message": "Generating problem statement..."
  }
}
```

**Message Types**:
- `status`: Generation status updates
- `progress`: Progress percentage (0.0-1.0)
- `complete`: Generation completed
- `error`: Error occurred

### Error Responses

Standardized error response format:

```json
{
  "error": {
    "type": "ValidationError",
    "message": "Invalid deliverable type: invalid_type",
    "details": {
      "field": "deliverable_types",
      "valid_values": ["problem_statement", "personas", ...]
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Rate Limiting

Default rate limits:
- 60 requests per minute per IP
- 10 concurrent generations per IP

Rate limit headers included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642249800
```

## 📚 SDK Examples

### Python SDK Usage

```python
import asyncio
from src.orchestrator import Orchestrator
from src.config_manager import ConfigManager
from src.prompt_schema import PromptData

async def generate_documentation():
    # Initialize components
    config = ConfigManager()
    orchestrator = Orchestrator(config)

    # Create prompt data
    prompt_data = PromptData(
        text="Create a customer relationship management system",
        deliverable_types=["problem_statement", "personas", "use_cases"],
        max_tokens=3000,
        temperature=0.6
    )

    # Generate content
    try:
        result = await orchestrator.generate_content(prompt_data)

        if result.success:
            print(f"Generation completed in {result.metadata['generation_time']:.2f}s")

            # Save results
            for deliverable_type, content in result.content.items():
                filename = f"{deliverable_type}.md"
                with open(filename, 'w') as f:
                    f.write(content)
                print(f"Saved {filename}")
        else:
            print("Generation failed:")
            for error in result.errors:
                print(f"- {error}")

    except Exception as e:
        print(f"Error: {e}")

# Run the example
asyncio.run(generate_documentation())
```

### JavaScript/Node.js SDK Usage

```javascript
const axios = require('axios');
const WebSocket = require('ws');

class AIPrototypingClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    async generate(prompt, options = {}) {
        const response = await axios.post(`${this.baseUrl}/generate`, {
            prompt,
            ...options
        });

        return response.data;
    }

    async getModels() {
        const response = await axios.get(`${this.baseUrl}/models`);
        return response.data.models;
    }

    async healthCheck() {
        const response = await axios.get(`${this.baseUrl}/health`);
        return response.data;
    }

    streamGeneration(prompt, options = {}) {
        return new Promise((resolve, reject) => {
            const ws = new WebSocket(`${this.baseUrl.replace('http', 'ws')}/ws`);

            ws.on('open', () => {
                ws.send(JSON.stringify({ prompt, ...options }));
            });

            ws.on('message', (data) => {
                const message = JSON.parse(data);

                if (message.type === 'complete') {
                    resolve(message.data);
                    ws.close();
                } else if (message.type === 'error') {
                    reject(new Error(message.data.message));
                    ws.close();
                } else {
                    console.log('Progress:', message.data);
                }
            });

            ws.on('error', reject);
        });
    }
}

// Usage example
async function example() {
    const client = new AIPrototypingClient();

    try {
        // Check health
        const health = await client.healthCheck();
        console.log('Service status:', health.status);

        // Generate documentation
        const result = await client.generate(
            "Create a social media analytics dashboard",
            {
                deliverable_types: ['problem_statement', 'personas'],
                max_tokens: 2048,
                temperature: 0.7
            }
        );

        console.log('Generation successful!');
        console.log('Content:', result.content);

    } catch (error) {
        console.error('Error:', error.message);
    }
}

example();
```

---

*For more examples and advanced usage, see the [examples/](../examples/) directory.*
