# CLI Reference

Comprehensive command-line interface documentation for the AI Prototyping Tool.

## 📝 Overview

The `ai-proto` command-line interface provides powerful tools for generating professional documentation using AI models. The CLI is built with Click and offers both simple and advanced usage patterns.

## 🛠️ Installation and Setup

### Basic Installation

```bash
# Install the package
pip install -e .

# Verify installation
ai-proto --version
```

### Shell Completions

Enable auto-completion for your shell:

```bash
# Auto-detect and install for current shell
./install_completions.sh

# Or install manually for specific shells
./install_completions.sh bash
./install_completions.sh zsh
./install_completions.sh fish
```

## 📚 Commands Reference

### Global Options

These options are available for all commands:

```bash
ai-proto [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

**Global Options**:
- `--version` - Show version and exit
- `--help` - Show help message and exit
- `-v, --verbose` - Increase verbosity (use multiple times: -v, -vv, -vvv)
- `--config-file PATH` - Specify configuration file path

### `generate` - Generate Documentation

The primary command for generating AI-powered documentation.

#### Basic Syntax

```bash
ai-proto generate [OPTIONS]
```

#### Required Input (choose one)

**Option 1: Text Prompt**
```bash
ai-proto generate -p "Create a customer management system for restaurants"
```

**Option 2: File Input**
```bash
ai-proto generate -f requirements.txt
```

#### Complete Options Reference

##### Input Options

| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--prompt` | `-p` | TEXT | Text prompt for generation |
| `--prompt-file` | `-f` | PATH | File containing prompt text |

##### Deliverable Selection

| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--deliverable-types` | `-t` | CHOICE | Deliverable types to generate (multiple allowed) |
| `--all-deliverables` | | FLAG | Generate all available deliverable types |

**Available Deliverable Types**:
- `problem_statement` - Problem Statement
- `personas` - User Personas
- `use_cases` - Use Cases and Scenarios
- `tool_outline` - Technical Tool Outline
- `implementation_instructions` - Implementation Guide
- `copilot365_presentation_prompt` - Copilot365 Presentation
- `effectiveness_assessment` - Effectiveness Assessment

##### Model Configuration

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--model` | `-m` | TEXT | auto | LM Studio model to use |
| `--lm-studio-url` | | URL | http://localhost:1234/v1 | LM Studio base URL |
| `--api-key` | | TEXT | None | API key (if required) |

##### Generation Parameters

| Option | Short | Type | Default | Range | Description |
|--------|-------|------|---------|-------|-------------|
| `--max-tokens` | | INT | 2048 | 1-8192 | Maximum tokens per generation |
| `--temperature` | | FLOAT | 0.7 | 0.0-1.0 | Sampling temperature |
| `--top-p` | | FLOAT | 0.9 | 0.0-1.0 | Nucleus sampling |
| `--completion-mode` | | CHOICE | sequential | | Completion strategy |

**Completion Modes**:
- `sequential` - Generate deliverables one by one
- `batch` - Generate all deliverables in parallel
- `streaming` - Stream responses in real-time

##### Output Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--output` | `-o` | PATH | ./output | Output directory |
| `--output-format` | | CHOICE | markdown | Output format |
| `--merge/--no-merge` | | FLAG | --merge | Merge deliverables into single file |
| `--show-html` | | FLAG | False | Generate HTML preview |
| `--raw` | | FLAG | False | Output raw content without formatting |

**Output Formats**:
- `markdown` - Markdown format (.md files)
- `json` - JSON format (.json files)

##### Utility Options

| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--save-config` | | PATH | Save current configuration to file |
| `--dry-run` | | FLAG | Show what would be generated without generating |
| `--quiet` | `-q` | FLAG | Suppress non-error output |

#### Usage Examples

##### Basic Generation

```bash
# Simple generation with default settings
ai-proto generate -p "Create a mobile fitness tracking app"

# Generate from file
ai-proto generate -f project_brief.txt

# Generate specific deliverables
ai-proto generate -p "Healthcare portal" \
  -t problem_statement \
  -t personas \
  -t use_cases
```

##### Advanced Configuration

```bash
# Custom model and parameters
ai-proto generate -p "E-commerce platform" \
  -m "mistral-7b-instruct" \
  --temperature 0.5 \
  --max-tokens 4096 \
  --completion-mode batch \
  -o ./ecommerce-docs

# Generate with specific output format
ai-proto generate -p "API Gateway" \
  --output-format json \
  --no-merge \
  --show-html

# Use remote LM Studio instance
ai-proto generate -p "Data pipeline" \
  --lm-studio-url http://192.168.1.100:1234/v1 \
  --api-key your-key-here
```

##### Configuration Management

```bash
# Save configuration for reuse
ai-proto generate -p "Social platform" \
  --temperature 0.3 \
  --max-tokens 3000 \
  --save-config social-config.json

# Use saved configuration
ai-proto generate -p "New social feature" \
  --config-file social-config.json

# Dry run to preview
ai-proto generate -p "Test project" \
  --dry-run \
  -t tool_outline
```

#### Configuration File Format

Save frequently used settings in JSON format:

```json
{
  "lm_studio_url": "http://localhost:1234/v1",
  "model": "mistral-7b-instruct",
  "max_tokens": 3000,
  "temperature": 0.5,
  "top_p": 0.9,
  "completion_mode": "sequential",
  "output_format": "markdown",
  "merge": true,
  "deliverable_types": [
    "problem_statement",
    "personas",
    "use_cases",
    "tool_outline"
  ]
}
```

### `models` - List Available Models

Display models currently loaded in LM Studio.

#### Syntax

```bash
ai-proto models [OPTIONS]
```

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--lm-studio-url` | URL | http://localhost:1234/v1 | LM Studio URL |
| `--format` | CHOICE | table | Output format |

**Output Formats**:
- `table` - Formatted table display
- `json` - JSON format
- `simple` - Simple list

#### Examples

```bash
# List models in table format
ai-proto models

# JSON output
ai-proto models --format json

# Check remote instance
ai-proto models --lm-studio-url http://remote-server:1234/v1
```

#### Sample Output

```
┌────────────────────────────────┬───────────┬────────────────────┐
│ Model ID                     │ Object    │ Created            │
├────────────────────────────────┼───────────┼────────────────────┤
│ mistral-7b-instruct          │ model     │ 2024-01-15 10:30   │
│ llama-2-7b-chat              │ model     │ 2024-01-15 09:15   │
└────────────────────────────────┴───────────┴────────────────────┘
```

### `deliverables` - List Available Deliverable Types

Show all supported deliverable types with descriptions.

#### Syntax

```bash
ai-proto deliverables [OPTIONS]
```

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--format` | CHOICE | table | Output format |
| `--detailed` | FLAG | False | Show detailed descriptions |

#### Examples

```bash
# List deliverables
ai-proto deliverables

# Detailed view
ai-proto deliverables --detailed

# JSON format
ai-proto deliverables --format json
```

### `health` - Check System Health

Verify connectivity and status of LM Studio and related services.

#### Syntax

```bash
ai-proto health [OPTIONS]
```

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--lm-studio-url` | URL | http://localhost:1234/v1 | LM Studio URL |
| `--timeout` | INT | 10 | Connection timeout in seconds |
| `--detailed` | FLAG | False | Show detailed health information |

#### Examples

```bash
# Basic health check
ai-proto health

# Detailed health check
ai-proto health --detailed

# Check remote instance
ai-proto health --lm-studio-url http://remote:1234/v1
```

#### Sample Output

```
✅ LM Studio Health Check

✅ Connection: OK
   URL: http://localhost:1234/v1
   Response Time: 45ms

✅ Models: 2 available
   - mistral-7b-instruct
   - llama-2-7b-chat

✅ Templates: 7 available
   - problem_statement
   - personas
   - use_cases
   - tool_outline
   - implementation_instructions
   - copilot365_presentation_prompt
   - effectiveness_assessment

✅ Configuration: Valid
   Max Tokens: 2048
   Temperature: 0.7
   Output Format: markdown
```

## 📊 Advanced Usage

### Environment Variables

Set default values using environment variables:

```bash
# LM Studio configuration
export AI_PROTO_LM_STUDIO_URL="http://localhost:1234/v1"
export AI_PROTO_API_KEY="your-api-key"

# Generation defaults
export AI_PROTO_MODEL="mistral-7b-instruct"
export AI_PROTO_TEMPERATURE="0.7"
export AI_PROTO_MAX_TOKENS="2048"
export AI_PROTO_OUTPUT_FORMAT="markdown"

# Output settings
export AI_PROTO_OUTPUT_DIR="./documentation"
export AI_PROTO_MERGE="true"
```

### Batch Processing

Process multiple prompts efficiently:

```bash
# Process multiple files
for file in requirements/*.txt; do
  ai-proto generate -f "$file" \
    -o "./output/$(basename "$file" .txt)" \
    --quiet
done

# Using configuration files
ai-proto generate -f project1.txt --config-file config1.json
ai-proto generate -f project2.txt --config-file config2.json
```

### Scripting and Automation

```bash
#!/bin/bash
# Generate documentation for a new project

set -e  # Exit on error

PROJECT_NAME="$1"
PROMPT="$2"
OUTPUT_DIR="./projects/${PROJECT_NAME}"

if [ -z "$PROJECT_NAME" ] || [ -z "$PROMPT" ]; then
  echo "Usage: $0 <project-name> <prompt>"
  exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Generate documentation
echo "Generating documentation for $PROJECT_NAME..."
ai-proto generate \
  -p "$PROMPT" \
  -o "$OUTPUT_DIR" \
  --temperature 0.5 \
  --max-tokens 3000 \
  --show-html \
  -v

# Create summary
echo "# $PROJECT_NAME" > "$OUTPUT_DIR/README.md"
echo "" >> "$OUTPUT_DIR/README.md"
echo "Generated on: $(date)" >> "$OUTPUT_DIR/README.md"
echo "Prompt: $PROMPT" >> "$OUTPUT_DIR/README.md"

echo "Documentation generated in $OUTPUT_DIR"
```

### Exit Codes

The CLI uses specific exit codes for different conditions:

| Code | Condition |
|------|----------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | LM Studio connection error |
| 4 | Validation error |
| 5 | File system error |
| 6 | Model error |

**Example**:
```bash
ai-proto generate -p "test" > /dev/null 2>&1
case $? in
  0) echo "Success" ;;
  3) echo "LM Studio not available" ;;
  *) echo "Other error occurred" ;;
esac
```

## 🛠️ Troubleshooting

### Common Issues

**Issue**: Command not found
```bash
# Solution: Ensure package is installed
pip install -e .
which ai-proto
```

**Issue**: LM Studio connection failed
```bash
# Solution: Check LM Studio status
ai-proto health --detailed
curl http://localhost:1234/v1/models
```

**Issue**: Generation taking too long
```bash
# Solution: Reduce token count or use smaller model
ai-proto generate -p "test" \
  --max-tokens 1024 \
  --temperature 0.5
```

### Debug Mode

```bash
# Enable maximum verbosity
ai-proto -vvv generate -p "debug test"

# Save debug output
ai-proto -vvv generate -p "test" 2> debug.log

# Dry run for debugging
ai-proto generate -p "test" --dry-run -vv
```

---

*For more information, see the [Getting Started Guide](getting-started.md) and [API Reference](api-reference.md).*
