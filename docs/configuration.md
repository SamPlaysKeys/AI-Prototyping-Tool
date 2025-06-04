# Configuration Guide

Comprehensive guide to configuring the AI Prototyping Tool for optimal performance and customization.

## 📝 Overview

The AI Prototyping Tool uses a hierarchical configuration system that allows settings to be specified through multiple sources, providing flexibility for different deployment scenarios.

### Configuration Hierarchy

Settings are loaded in this priority order (highest to lowest):

1. **Command-line arguments** - Override all other settings
2. **Environment variables** - Runtime configuration
3. **Configuration files** - Persistent settings (JSON/TOML)
4. **Default values** - Built-in fallbacks

## 🛠️ Configuration Sources

### 1. Command-Line Arguments

Direct CLI options take highest priority:

```bash
ai-proto generate \
  --lm-studio-url http://remote:1234/v1 \
  --temperature 0.5 \
  --max-tokens 4096 \
  --model "mistral-7b-instruct"
```

### 2. Environment Variables

Set using the `AI_PROTO_` prefix:

```bash
# LM Studio Configuration
export AI_PROTO_LM_STUDIO_URL="http://localhost:1234/v1"
export AI_PROTO_API_KEY="your-api-key"

# Generation Settings
export AI_PROTO_MODEL="mistral-7b-instruct"
export AI_PROTO_TEMPERATURE="0.7"
export AI_PROTO_MAX_TOKENS="2048"
export AI_PROTO_TOP_P="0.9"

# Output Settings
export AI_PROTO_OUTPUT_FORMAT="markdown"
export AI_PROTO_OUTPUT_DIR="./documentation"
export AI_PROTO_MERGE="true"

# Deliverable Defaults
export AI_PROTO_DELIVERABLE_TYPES="problem_statement,personas,use_cases"
```

### 3. Configuration Files

#### JSON Format

```json
{
  "lm_studio": {
    "url": "http://localhost:1234/v1",
    "api_key": null,
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1.0
  },
  "generation": {
    "model": "mistral-7b-instruct",
    "max_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.9,
    "completion_mode": "sequential",
    "stream": false
  },
  "output": {
    "format": "markdown",
    "directory": "./output",
    "merge": true,
    "show_html": false,
    "filename_template": "{deliverable_type}_{timestamp}"
  },
  "deliverables": {
    "default_types": [
      "problem_statement",
      "personas",
      "use_cases",
      "tool_outline"
    ],
    "custom_templates": {}
  },
  "logging": {
    "level": "INFO",
    "file": "logs/ai-proto.log",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "max_size": "10MB",
    "backup_count": 5
  },
  "web": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": false,
    "cors_origins": ["*"],
    "websocket_timeout": 300,
    "max_prompt_length": 5000
  }
}
```

#### TOML Format

```toml
[lm_studio]
url = "http://localhost:1234/v1"
api_key = ""
timeout = 30
retry_attempts = 3
retry_delay = 1.0

[generation]
model = "mistral-7b-instruct"
max_tokens = 2048
temperature = 0.7
top_p = 0.9
completion_mode = "sequential"
stream = false

[output]
format = "markdown"
directory = "./output"
merge = true
show_html = false
filename_template = "{deliverable_type}_{timestamp}"

[deliverables]
default_types = [
  "problem_statement",
  "personas",
  "use_cases",
  "tool_outline"
]

[logging]
level = "INFO"
file = "logs/ai-proto.log"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
max_size = "10MB"
backup_count = 5

[web]
host = "0.0.0.0"
port = 8000
debug = false
cors_origins = ["*"]
websocket_timeout = 300
max_prompt_length = 5000
```

### Loading Configuration Files

```bash
# Specify configuration file
ai-proto generate --config-file my-config.json -p "My project"

# Multiple configuration files (merged)
ai-proto generate \
  --config-file base-config.json \
  --config-file project-config.json \
  -p "My project"

# Save current configuration
ai-proto generate -p "Test" \
  --temperature 0.5 \
  --save-config production-config.json
```

## 🔩 Configuration Sections

### LM Studio Configuration

```json
{
  "lm_studio": {
    "url": "http://localhost:1234/v1",
    "api_key": null,
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1.0,
    "verify_ssl": true,
    "headers": {
      "User-Agent": "AI-Prototyping-Tool/1.0"
    }
  }
}
```

**Parameters**:
- `url` (str): LM Studio API base URL
- `api_key` (str|null): API key if authentication required
- `timeout` (int): Request timeout in seconds
- `retry_attempts` (int): Number of retry attempts on failure
- `retry_delay` (float): Delay between retries in seconds
- `verify_ssl` (bool): Enable SSL certificate verification
- `headers` (dict): Additional HTTP headers

### Generation Configuration

```json
{
  "generation": {
    "model": "mistral-7b-instruct",
    "max_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "completion_mode": "sequential",
    "stream": false,
    "stop_sequences": [],
    "seed": null
  }
}
```

**Parameters**:
- `model` (str): Model identifier ("auto" for automatic selection)
- `max_tokens` (int): Maximum tokens per generation (1-8192)
- `temperature` (float): Sampling temperature (0.0-1.0)
- `top_p` (float): Nucleus sampling parameter (0.0-1.0)
- `frequency_penalty` (float): Frequency penalty (-2.0 to 2.0)
- `presence_penalty` (float): Presence penalty (-2.0 to 2.0)
- `completion_mode` (str): "sequential", "batch", or "streaming"
- `stream` (bool): Enable streaming responses
- `stop_sequences` (list): Stop generation at these sequences
- `seed` (int|null): Random seed for reproducible results

### Output Configuration

```json
{
  "output": {
    "format": "markdown",
    "directory": "./output",
    "merge": true,
    "show_html": false,
    "filename_template": "{deliverable_type}_{timestamp}",
    "timestamp_format": "%Y%m%d_%H%M%S",
    "encoding": "utf-8",
    "line_endings": "auto",
    "create_subdirs": true
  }
}
```

**Parameters**:
- `format` (str): "markdown" or "json"
- `directory` (str): Output directory path
- `merge` (bool): Merge all deliverables into single file
- `show_html` (bool): Generate HTML preview
- `filename_template` (str): Template for output filenames
- `timestamp_format` (str): Timestamp format string
- `encoding` (str): File encoding
- `line_endings` (str): "auto", "lf", or "crlf"
- `create_subdirs` (bool): Create subdirectories for organization

### Deliverables Configuration

```json
{
  "deliverables": {
    "default_types": [
      "problem_statement",
      "personas",
      "use_cases",
      "tool_outline"
    ],
    "available_types": {
      "problem_statement": {
        "name": "Problem Statement",
        "description": "Executive summary and problem analysis",
        "template": "problem_statement.md",
        "enabled": true
      },
      "personas": {
        "name": "Personas",
        "description": "User profiles and characteristics",
        "template": "personas.md",
        "enabled": true
      }
    },
    "custom_templates": {
      "custom_deliverable": {
        "name": "Custom Deliverable",
        "template": "custom_template.md",
        "prompt": "Generate custom content for: {prompt}"
      }
    }
  }
}
```

### Logging Configuration

```json
{
  "logging": {
    "level": "INFO",
    "file": "logs/ai-proto.log",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "max_size": "10MB",
    "backup_count": 5,
    "console": true,
    "structured": false,
    "filters": []
  }
}
```

**Parameters**:
- `level` (str): "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
- `file` (str): Log file path
- `format` (str): Log message format string
- `date_format` (str): Date format for log timestamps
- `max_size` (str): Maximum log file size before rotation
- `backup_count` (int): Number of backup files to keep
- `console` (bool): Also log to console
- `structured` (bool): Use structured JSON logging
- `filters` (list): Additional log filters

### Web Interface Configuration

```json
{
  "web": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": false,
    "reload": false,
    "workers": 1,
    "cors_origins": ["*"],
    "cors_methods": ["GET", "POST"],
    "cors_headers": ["*"],
    "websocket_timeout": 300,
    "max_prompt_length": 5000,
    "rate_limit": {
      "requests_per_minute": 60,
      "concurrent_generations": 10
    },
    "static_files": {
      "directory": "static",
      "cache_max_age": 3600
    }
  }
}
```

## 📏 Configuration Profiles

### Development Profile

```json
{
  "_profile": "development",
  "lm_studio": {
    "url": "http://localhost:1234/v1",
    "timeout": 10
  },
  "generation": {
    "max_tokens": 1024,
    "temperature": 0.8
  },
  "output": {
    "directory": "./dev-output",
    "show_html": true
  },
  "logging": {
    "level": "DEBUG",
    "console": true
  },
  "web": {
    "debug": true,
    "reload": true
  }
}
```

### Production Profile

```json
{
  "_profile": "production",
  "lm_studio": {
    "url": "http://lm-studio-server:1234/v1",
    "timeout": 60,
    "retry_attempts": 5
  },
  "generation": {
    "max_tokens": 4096,
    "temperature": 0.5
  },
  "output": {
    "directory": "/var/lib/ai-proto/output",
    "create_subdirs": true
  },
  "logging": {
    "level": "INFO",
    "file": "/var/log/ai-proto/app.log",
    "structured": true
  },
  "web": {
    "host": "0.0.0.0",
    "port": 80,
    "workers": 4,
    "rate_limit": {
      "requests_per_minute": 30,
      "concurrent_generations": 5
    }
  }
}
```

### Testing Profile

```json
{
  "_profile": "testing",
  "lm_studio": {
    "url": "http://mock-lm-studio:1234/v1",
    "timeout": 5
  },
  "generation": {
    "max_tokens": 512,
    "temperature": 0.0
  },
  "output": {
    "directory": "./test-output",
    "merge": false
  },
  "logging": {
    "level": "DEBUG",
    "console": true,
    "file": null
  }
}
```

## 📊 Environment-Specific Settings

### Docker Environment

```bash
# docker-compose.yml environment section
environment:
  - AI_PROTO_LM_STUDIO_URL=http://host.docker.internal:1234/v1
  - AI_PROTO_OUTPUT_DIR=/app/output
  - AI_PROTO_LOG_FILE=/app/logs/app.log
  - AI_PROTO_LOG_LEVEL=INFO
  - AI_PROTO_WEB_HOST=0.0.0.0
  - AI_PROTO_WEB_PORT=8000
```

### Kubernetes Environment

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-proto-config
data:
  AI_PROTO_LM_STUDIO_URL: "http://lm-studio-service:1234/v1"
  AI_PROTO_OUTPUT_DIR: "/data/output"
  AI_PROTO_LOG_LEVEL: "INFO"
  AI_PROTO_WEB_WORKERS: "4"
---
apiVersion: v1
kind: Secret
metadata:
  name: ai-proto-secrets
data:
  AI_PROTO_API_KEY: <base64-encoded-key>
```

### Systemd Service

```ini
# /etc/systemd/system/ai-proto.service
[Unit]
Description=AI Prototyping Tool
After=network.target

[Service]
Type=simple
User=ai-proto
WorkingDirectory=/opt/ai-proto
Environment=AI_PROTO_CONFIG_FILE=/etc/ai-proto/config.json
Environment=AI_PROTO_LOG_LEVEL=INFO
ExecStart=/opt/ai-proto/venv/bin/python -m web.app
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🔍 Configuration Validation

### Built-in Validation

The system automatically validates configuration:

```bash
# Validate configuration file
ai-proto validate-config config.json

# Check current configuration
ai-proto config --show

# Test configuration with dry run
ai-proto generate --dry-run -p "test" --config-file config.json
```

### Custom Validation Rules

```python
# Custom validation in config_manager.py
def validate_custom_config(config):
    errors = []

    # Validate temperature range
    temp = config.get('generation.temperature', 0.7)
    if not 0.0 <= temp <= 1.0:
        errors.append(f"Temperature {temp} outside valid range [0.0, 1.0]")

    # Validate max_tokens
    max_tokens = config.get('generation.max_tokens', 2048)
    if max_tokens < 1 or max_tokens > 8192:
        errors.append(f"Max tokens {max_tokens} outside valid range [1, 8192]")

    return errors
```

## 📝 Configuration Templates

### Minimal Configuration

```json
{
  "lm_studio": {
    "url": "http://localhost:1234/v1"
  },
  "generation": {
    "max_tokens": 2048
  }
}
```

### High-Performance Configuration

```json
{
  "lm_studio": {
    "url": "http://localhost:1234/v1",
    "timeout": 120,
    "retry_attempts": 5
  },
  "generation": {
    "max_tokens": 8192,
    "temperature": 0.3,
    "completion_mode": "batch"
  },
  "output": {
    "format": "json",
    "merge": false
  },
  "web": {
    "workers": 8,
    "rate_limit": {
      "requests_per_minute": 120
    }
  }
}
```

### Security-Focused Configuration

```json
{
  "lm_studio": {
    "url": "https://secure-lm-studio.internal:1234/v1",
    "verify_ssl": true,
    "headers": {
      "Authorization": "Bearer ${AI_PROTO_API_KEY}"
    }
  },
  "web": {
    "cors_origins": ["https://approved-domain.com"],
    "rate_limit": {
      "requests_per_minute": 30,
      "concurrent_generations": 3
    }
  },
  "logging": {
    "level": "WARNING",
    "structured": true,
    "filters": ["security_filter"]
  }
}
```

## 🔧 Configuration Management

### Configuration Backup

```bash
# Backup current configuration
ai-proto config --export > config-backup-$(date +%Y%m%d).json

# Restore from backup
ai-proto config --import config-backup-20240115.json
```

### Configuration Migration

```python
# Migration script for config format changes
def migrate_v1_to_v2(old_config):
    new_config = {
        "version": "2.0",
        "lm_studio": {
            "url": old_config.get("lm_studio_url", "http://localhost:1234/v1")
        },
        "generation": {
            "model": old_config.get("model", "auto"),
            "max_tokens": old_config.get("max_tokens", 2048)
        }
    }
    return new_config
```

### Dynamic Configuration Updates

```bash
# Update configuration at runtime (web interface)
curl -X PATCH http://localhost:8000/config \
  -H "Content-Type: application/json" \
  -d '{
    "generation.temperature": 0.5,
    "generation.max_tokens": 3000
  }'
```

## 🔍 Troubleshooting Configuration

### Common Issues

**Issue**: Configuration not loading
```bash
# Check file permissions
ls -la config.json

# Validate JSON syntax
python -m json.tool config.json

# Check environment variables
env | grep AI_PROTO_
```

**Issue**: Conflicting settings
```bash
# Show effective configuration
ai-proto config --show --verbose

# Show configuration sources
ai-proto config --sources
```

**Issue**: Invalid parameter values
```bash
# Validate configuration
ai-proto validate-config --strict config.json

# Show parameter ranges
ai-proto config --help-parameters
```

### Debug Mode

```bash
# Enable configuration debugging
export AI_PROTO_DEBUG_CONFIG=true
ai-proto generate -p "test"
```

---

*For specific configuration examples, see the [examples/configs/](../examples/configs/) directory.*
