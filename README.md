# AI Prototyping Tool

A powerful tool for rapid AI application prototyping with both CLI and web interfaces.

## Features

- CLI interface for quick prototyping
- Web application for interactive development
- Template system for prompts and outputs
- Integration with multiple AI providers (OpenAI, Anthropic, etc.)
- Extensible architecture

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd AI-Prototyping-Tool
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development

### Directory Structure

- `src/` - Core modules and business logic
- `cli/` - Command-line interface
- `web/` - Web application
- `templates/` - Prompt and output templates
- `tests/` - Test suite

### Running Tests

```bash
pytest
```

### Code Quality

The project uses pre-commit hooks for:
- Code formatting with Black
- Linting with flake8
- Various file checks

Run manually:
```bash
black .
flake8
```

## Usage

### CLI

```bash
# TODO: Add CLI usage examples
```

### Web Interface

```bash
# TODO: Add web interface usage
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure pre-commit hooks pass
5. Submit a pull request

## License

TODO: Add license information
