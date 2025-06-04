# Architecture Overview

This document provides a comprehensive overview of the AI Prototyping Tool's architecture, design patterns, and internal components.

## 🏗️ System Architecture

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────┐
│                          User Interfaces                            │
├─────────────────────────────┬──────────────────────────────┤
│        CLI Interface        │       Web Interface         │
│       (cli/main.py)        │      (web/app.py)           │
└─────────────────────────────┴──────────────────────────────┘
                              │
┌────────────────────────────────────────────────────────────┐
│                       Core Business Logic                        │
├─────────────────────────────┬──────────────────────────────┤
│        Orchestrator         │      Template Renderer       │
│    (orchestrator.py)        │   (template_renderer.py)     │
├─────────────────────────────┼──────────────────────────────┤
│      Config Manager         │       Error Handler          │
│   (config_manager.py)       │    (error_handler.py)        │
└─────────────────────────────┴──────────────────────────────┘
                              │
┌────────────────────────────────────────────────────────────┐
│                      AI Provider Layer                          │
├─────────────────────────────┬──────────────────────────────┤
│      LM Studio Client       │       Future Providers        │
│   (lmstudio_client.py)      │    (OpenAI, Anthropic, etc.) │
└─────────────────────────────┴──────────────────────────────┘
                              │
┌────────────────────────────────────────────────────────────┐
│                     Template System                            │
│                   (templates/deliverables/)                   │
└────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Modularity**: Clear separation of concerns between components
2. **Extensibility**: Easy to add new AI providers and deliverable types
3. **Configuration-Driven**: Behavior controlled through configuration files
4. **Error Resilience**: Comprehensive error handling and logging
5. **Template-Based**: Flexible template system for output customization

## 📚 Core Components

### 1. Orchestrator (`src/orchestrator.py`)

**Purpose**: Central coordination of the generation process

**Key Responsibilities**:
- Manages generation workflow and sequencing
- Coordinates between AI provider and template renderer
- Handles different completion modes (sequential, batch, streaming)
- Manages state and progress tracking

**Key Methods**:
```python
class Orchestrator:
    def generate_content(self, prompt_data: PromptData) -> GenerationResult
    def _process_deliverable(self, deliverable_type: str) -> Dict
    def _handle_completion_mode(self, mode: str) -> None
```

### 2. LM Studio Client (`src/lmstudio_client.py`)

**Purpose**: Interface with LM Studio local AI models

**Key Responsibilities**:
- Manages HTTP connections to LM Studio API
- Handles authentication and request formatting
- Provides model discovery and health checking
- Implements retry logic and error handling

**Key Methods**:
```python
class LMStudioClient:
    def complete(self, prompt: str, **kwargs) -> str
    def list_models(self) -> List[Dict]
    def health_check(self) -> bool
    def stream_completion(self, prompt: str) -> Iterator[str]
```

### 3. Template Renderer (`src/template_renderer.py`)

**Purpose**: Processes Jinja2 templates for output generation

**Key Responsibilities**:
- Loads and validates template files
- Renders templates with generated content
- Handles template inheritance and includes
- Manages output formatting (Markdown, HTML, JSON)

**Key Methods**:
```python
class TemplateRenderer:
    def render_deliverable(self, template_name: str, context: Dict) -> str
    def get_available_templates(self) -> List[str]
    def validate_template(self, template_path: str) -> bool
```

### 4. Configuration Manager (`src/config_manager.py`)

**Purpose**: Centralized configuration management

**Key Responsibilities**:
- Loads configuration from multiple sources (files, environment, CLI)
- Validates configuration parameters
- Provides configuration hierarchy and defaults
- Handles configuration persistence

**Configuration Sources** (in priority order):
1. Command-line arguments
2. Environment variables
3. Configuration files (JSON/TOML)
4. Default values

### 5. Error Handler (`src/error_handler.py`)

**Purpose**: Comprehensive error management and logging

**Key Responsibilities**:
- Defines custom exception classes
- Implements retry logic with exponential backoff
- Provides structured logging
- Handles graceful degradation

## 🌐 Web Architecture

### FastAPI Application (`web/app.py`)

**Framework**: FastAPI with Uvicorn ASGI server

**Key Features**:
- RESTful API endpoints
- WebSocket support for real-time updates
- Automatic API documentation
- CORS support for cross-origin requests

**API Endpoints**:
```
POST /generate          # Generate documentation
GET  /models            # List available models
GET  /health            # Health check
GET  /deliverables      # List deliverable types
WS   /ws                # WebSocket for real-time updates
```

### Request/Response Flow

```
Client Request → FastAPI Router → Request Validation → Orchestrator
                                                               ↓
JSON Response ← Response Formatter ← Template Renderer ← LM Studio
```

## 📝 Template System

### Template Structure

```
templates/
├── deliverables/           # Deliverable templates
│   ├── problem_statement.md
│   ├── personas.md
│   ├── use_cases.md
│   └── ...
├── base.md                 # Base template
└── README.md               # Template documentation
```

### Template Variables

Each template receives these context variables:
- `project_name`: Generated project name
- `timestamp`: Generation timestamp
- `generated_content`: AI-generated content
- `metadata`: Additional metadata

### Template Inheritance

Templates can extend base templates using Jinja2 inheritance:
```jinja2
{% extends "base.md" %}

{% block content %}
# Problem Statement
{{ generated_content }}
{% endblock %}
```

## 🔄 Data Flow

### Generation Process

1. **Input Processing**
   ```
   User Input → Prompt Validation → Configuration Loading
   ```

2. **Content Generation**
   ```
   Prompt Data → LM Studio Client → AI Model → Generated Text
   ```

3. **Template Rendering**
   ```
   Generated Text → Template Renderer → Formatted Output
   ```

4. **Output Handling**
   ```
   Formatted Output → File Writer → Disk Storage
   ```

### Error Handling Flow

```
Error Occurs → Error Handler → Log Error → Retry Logic
                                ↓
                       Graceful Degradation or Failure
```

## 📊 Performance Considerations

### Optimization Strategies

1. **Caching**
   - Template compilation caching
   - Configuration caching
   - Model metadata caching

2. **Asynchronous Processing**
   - Non-blocking I/O for web interface
   - Streaming responses for large generations
   - Background task processing

3. **Resource Management**
   - Connection pooling for HTTP requests
   - Memory-efficient template rendering
   - Configurable timeout and retry limits

### Scalability

- **Horizontal Scaling**: Multiple web instances behind load balancer
- **Vertical Scaling**: Configurable worker processes and threads
- **Caching Layer**: Redis/Memcached for session and result caching

## 🔒 Security

### Input Validation
- Prompt length limits
- Template injection prevention
- File path validation
- Configuration parameter validation

### Output Sanitization
- Markdown content sanitization
- HTML output escaping
- File name sanitization

### API Security
- Rate limiting
- CORS configuration
- Input size limits
- Request timeout limits

## 🔧 Extension Points

### Adding New AI Providers

1. **Create Provider Class**:
   ```python
   class NewAIProvider(BaseProvider):
       def complete(self, prompt: str) -> str
       def list_models(self) -> List[str]
   ```

2. **Register Provider**:
   ```python
   # In config_manager.py
   PROVIDERS = {
       'lmstudio': LMStudioClient,
       'newai': NewAIProvider
   }
   ```

### Adding New Deliverable Types

1. **Create Template**: Add new template file in `templates/deliverables/`
2. **Update Configuration**: Add to deliverable types list
3. **Add Documentation**: Update help text and documentation

### Custom Template Functions

Extend Jinja2 with custom functions:
```python
# In template_renderer.py
def custom_filter(text):
    return text.upper()

env.filters['custom'] = custom_filter
```

## 📊 Monitoring and Logging

### Logging Levels
- `DEBUG`: Detailed execution information
- `INFO`: General operational messages
- `WARNING`: Potential issues
- `ERROR`: Error conditions
- `CRITICAL`: Serious errors requiring immediate attention

### Metrics Collection
- Generation request count
- Success/failure rates
- Response times
- Model usage statistics
- Error frequency and types

---

*For implementation details, see the [API Reference](api-reference.md) and individual component documentation.*
