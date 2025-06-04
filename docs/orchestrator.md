# Orchestration Engine Documentation

The Orchestration Engine (`src/orchestrator.py`) is the core component that coordinates the entire document generation process. It receives structured user prompts, iterates through deliverable templates, calls the LM Studio client with tailored prompts, and merges responses into cohesive Markdown documents.

## Features

- **Multiple Completion Modes**: Sequential, batch, and streaming processing
- **Configurable Parameters**: Temperature, max tokens, retry logic, and timeouts
- **Modular Architecture**: Easy to extend with new deliverable types
- **Error Handling**: Comprehensive error handling with retry logic
- **Document Merging**: Automatic merging of multiple deliverables into a single document
- **Token Tracking**: Monitor token usage across all generations
- **Logging Support**: Configurable logging for debugging and monitoring

## Core Components

### OrchestrationEngine

The main class that coordinates the entire process:

```python
from src.orchestrator import OrchestrationEngine, OrchestrationConfig
from src.prompt_schema import DeliverableType

# Create configuration
config = OrchestrationConfig(
    completion_mode=CompletionMode.SEQUENTIAL,
    max_tokens=2048,
    temperature=0.7
)

# Create and use engine
with OrchestrationEngine(config) as engine:
    if engine.initialize():
        result = engine.orchestrate(
            user_input="Develop a CRM tool for small businesses...",
            deliverable_types=[
                DeliverableType.PROBLEM_STATEMENT,
                DeliverableType.PERSONAS,
                DeliverableType.USE_CASES
            ]
        )
```

### OrchestrationConfig

Configuration class for customizing engine behavior:

```python
@dataclass
class OrchestrationConfig:
    # LM Studio configuration
    lm_studio_base_url: str = "http://localhost:1234/v1"
    lm_studio_api_key: Optional[str] = None
    model_name: Optional[str] = None

    # Generation parameters
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9

    # Orchestration settings
    completion_mode: CompletionMode = CompletionMode.SEQUENTIAL
    merge_into_single_document: bool = True
    include_table_of_contents: bool = True

    # Retry and timeout settings
    max_retries_per_deliverable: int = 3
    request_timeout: float = 60.0
```

### CompletionMode

Three completion modes are supported:

- **SEQUENTIAL**: Process deliverables one by one (default)
- **BATCH**: Process all deliverables together (currently implemented as sequential)
- **STREAMING**: Process with streaming support (future enhancement)

### PromptGenerator

Generates tailored prompts for each deliverable type:

```python
class PromptGenerator:
    def generate_prompt(self, deliverable_type: DeliverableType,
                       user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        # Creates specialized prompts based on deliverable type
```

## Usage Examples

### Basic Usage

```python
from src.orchestrator import quick_generate
from src.prompt_schema import DeliverableType

# Quick generation without manual setup
result = quick_generate(
    user_input="Create a project management tool",
    deliverable_types=[
        DeliverableType.PROBLEM_STATEMENT,
        DeliverableType.TOOL_OUTLINE
    ],
    max_tokens=1500,
    temperature=0.6
)

print(f"Generated {result.success_count} deliverables")
if result.merged_document:
    with open('output.md', 'w') as f:
        f.write(result.merged_document)
```

### Advanced Configuration

```python
from src.orchestrator import OrchestrationEngine, OrchestrationConfig, CompletionMode

config = OrchestrationConfig(
    model_name="specific-model",
    completion_mode=CompletionMode.BATCH,
    max_tokens=3000,
    temperature=0.5,
    max_retries_per_deliverable=5,
    merge_into_single_document=True,
    include_table_of_contents=True,
    enable_logging=True,
    log_level="DEBUG"
)

engine = OrchestrationEngine(config)
if engine.initialize():
    result = engine.orchestrate(user_input, deliverable_types)
```

### Error Handling

```python
try:
    with OrchestrationEngine() as engine:
        if not engine.initialize():
            print("Failed to initialize engine")
            return

        result = engine.orchestrate(user_input, deliverable_types)

        # Check results
        for deliverable_result in result.deliverable_results:
            if not deliverable_result.success:
                print(f"Failed: {deliverable_result.deliverable_type.value}")
                print(f"Error: {deliverable_result.error_message}")

except Exception as e:
    print(f"Orchestration error: {e}")
```

## Data Structures

### OrchestrationResult

The main result object returned by the orchestrator:

```python
@dataclass
class OrchestrationResult:
    deliverable_results: List[DeliverableResult]
    merged_document: Optional[str] = None
    total_execution_time: float = 0.0
    total_tokens_used: int = 0
    success_count: int = 0
    error_count: int = 0
    config_used: Optional[OrchestrationConfig] = None
```

### DeliverableResult

Result for each individual deliverable:

```python
@dataclass
class DeliverableResult:
    deliverable_type: DeliverableType
    content: str
    success: bool
    error_message: Optional[str] = None
    execution_time: float = 0.0
    token_usage: Optional[Dict[str, int]] = None
    prompt_used: Optional[str] = None
```

## Integration Points

### LM Studio Client

The orchestrator integrates with the LM Studio client for AI generation:

- Automatic model discovery and selection
- Health checks and validation
- Retry logic with exponential backoff
- Token usage tracking

### Template Renderer

Integrates with the template rendering system:

- Validates template availability
- Can render using templates (future enhancement)
- Supports multiple output formats

### Prompt Schema

Works with the prompt schema system:

- Uses DeliverableType enumeration
- Supports schema validation
- Processes structured user input

## Extensibility

### Adding New Deliverable Types

1. Add new type to `DeliverableType` enum in `prompt_schema.py`
2. Add instructions in `PromptGenerator._get_deliverable_instructions()`
3. Add template mapping in `TemplateRenderer.template_map`
4. Create corresponding template file

### Custom Prompt Generation

```python
class CustomPromptGenerator(PromptGenerator):
    def _get_deliverable_instructions(self, deliverable_type):
        if deliverable_type == DeliverableType.CUSTOM_TYPE:
            return "Custom instructions for new deliverable type"
        return super()._get_deliverable_instructions(deliverable_type)

# Use custom generator
engine = OrchestrationEngine()
engine.prompt_generator = CustomPromptGenerator()
```

### Custom Processing Modes

You can extend the processing modes by overriding the processing methods:

```python
class CustomOrchestrationEngine(OrchestrationEngine):
    def _process_custom(self, user_input, deliverable_types, context):
        # Custom processing logic
        return results
```

## Performance Considerations

- **Sequential Mode**: Safest, processes one deliverable at a time
- **Batch Mode**: Future enhancement for parallel processing
- **Token Management**: Monitor `total_tokens_used` to manage costs
- **Retry Logic**: Configurable retry attempts with exponential backoff
- **Timeouts**: Adjustable request timeouts for long-running generations

## Monitoring and Debugging

### Logging

```python
config = OrchestrationConfig(
    enable_logging=True,
    log_level="DEBUG"  # DEBUG, INFO, WARNING, ERROR
)
```

### Validation

```python
engine = OrchestrationEngine()

# Validate templates
validation = engine.validate_deliverable_templates()
for deliverable, result in validation.items():
    print(f"{deliverable}: {result['is_valid']}")

# Check available models
models = engine.get_available_models()
print(f"Available models: {models}")
```

### Metrics

Track important metrics:

```python
result = engine.orchestrate(user_input, deliverable_types)

print(f"Execution time: {result.total_execution_time:.2f}s")
print(f"Success rate: {result.success_count}/{len(deliverable_types)}")
print(f"Token usage: {result.total_tokens_used}")
print(f"Average time per deliverable: {result.total_execution_time/len(deliverable_types):.2f}s")
```

## Best Practices

1. **Always use context managers** for proper resource cleanup
2. **Check initialization success** before orchestrating
3. **Handle failures gracefully** by checking individual deliverable results
4. **Monitor token usage** to manage API costs
5. **Use appropriate completion modes** based on your use case
6. **Configure retry logic** based on your reliability requirements
7. **Enable logging** for production deployments
8. **Validate templates** before running orchestration

## Error Handling

The orchestrator includes comprehensive error handling:

- **Network errors**: Automatic retry with exponential backoff
- **API errors**: Detailed error classification and logging
- **Timeout errors**: Configurable timeouts with retry logic
- **Model errors**: Graceful fallback to available models
- **Template errors**: Validation and error reporting

## Future Enhancements

- **True streaming support**: Real-time generation with progress updates
- **Parallel processing**: Concurrent generation of multiple deliverables
- **Caching**: Cache generated content for faster repeated generations
- **Custom output formats**: Support for PDF, DOCX, and other formats
- **Advanced prompt chaining**: Use previous deliverable outputs in subsequent prompts
- **Model comparison**: Generate using multiple models and compare results
