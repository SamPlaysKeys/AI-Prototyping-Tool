"""
Pytest configuration and fixtures for AI Prototyping Tool tests.

This module provides common fixtures, mocks, and utilities for testing.
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, MagicMock
import pytest
from datetime import datetime

# Add src to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def sample_user_input():
    """Sample user input for testing."""
    return """
    Project: Customer Management System
    Problem: Manual customer tracking is inefficient
    Stakeholders: Sales team, Customer service
    Goal: Automate customer relationship management
    Industry: Software Services
    Organization Size: 50-100 employees
    Technical Environment: Cloud-based, REST APIs
    Primary Stakeholders: Sales Manager, Customer Success Team
    Budget: $50,000 - $100,000
    Timeline: 6 months
    """


@pytest.fixture
def sample_json_payload():
    """Sample JSON payload for testing."""
    return {
        "project_name": "Test Project",
        "timestamp": datetime.now().isoformat(),
        "executive_summary": "This is a test executive summary for the project.",
        "current_state": "Current manual processes are inefficient and error-prone.",
        "problem_description": "The main problem is lack of automation in customer management.",
        "impact_analysis": "High impact on customer satisfaction and operational efficiency.",
        "industry_domain": "Software Services",
        "organization_size": "50-100 employees",
        "technical_environment": "Cloud-based with REST APIs",
        "primary_stakeholders": "Sales Manager, Customer Success Team",
        "secondary_stakeholders": "IT Department, Finance",
        "key_performance_indicators": "Customer retention rate, response time",
        "acceptance_criteria": "System must reduce response time by 50%",
        "technical_constraints": "Must integrate with existing CRM",
        "business_constraints": "Budget limit of $100,000",
        "assumptions": "Current staff will be trained on new system",
        "project_duration": "6 months",
        "key_milestones": "Requirements gathering, Development, Testing, Deployment",
    }


@pytest.fixture
def sample_completion_request():
    """Sample completion request for LM Studio testing."""
    from lmstudio_client import CompletionRequest

    return CompletionRequest(
        model="test-model",
        prompt="Generate a test response",
        max_tokens=100,
        temperature=0.7,
        top_p=0.9,
    )


@pytest.fixture
def sample_completion_response():
    """Sample completion response from LM Studio."""
    return {
        "id": "cmpl-test-123",
        "object": "text_completion",
        "created": int(datetime.now().timestamp()),
        "model": "test-model",
        "choices": [
            {
                "text": "This is a test response from the AI model.",
                "index": 0,
                "finish_reason": "stop",
                "logprobs": None,
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25},
    }


@pytest.fixture
def mock_lm_studio_client():
    """Mock LM Studio client for testing."""
    from lmstudio_client import (
        Model,
        CompletionResponse,
        CompletionChoice,
        CompletionUsage,
    )

    mock_client = Mock()

    # Mock models
    mock_models = [
        Model(id="test-model-1", object="model"),
        Model(id="test-model-2", object="model"),
    ]
    mock_client.list_models.return_value = mock_models

    # Mock health check
    mock_client.health_check.return_value = {
        "status": "healthy",
        "models_count": 2,
        "base_url": "http://localhost:1234/v1",
    }

    # Mock completion
    mock_choice = CompletionChoice(
        text="Generated test content from AI model.", index=0, finish_reason="stop"
    )
    mock_usage = CompletionUsage(
        prompt_tokens=10, completion_tokens=15, total_tokens=25
    )
    mock_response = CompletionResponse(
        id="cmpl-test-123",
        object="text_completion",
        created=int(datetime.now().timestamp()),
        model="test-model-1",
        choices=[mock_choice],
        usage=mock_usage,
    )
    mock_client.create_completion.return_value = mock_response
    mock_client.create_completion_simple.return_value = mock_response

    # Mock close method
    mock_client.close.return_value = None

    return mock_client


@pytest.fixture
def mock_requests_session():
    """Mock requests session for HTTP testing."""
    with patch("requests.Session") as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Default successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"data": []}

        mock_session.get.return_value = mock_response
        mock_session.post.return_value = mock_response

        yield mock_session


@pytest.fixture
def orchestration_config():
    """Orchestration configuration for testing."""
    from orchestrator import OrchestrationConfig, CompletionMode

    return OrchestrationConfig(
        lm_studio_base_url="http://localhost:1234/v1",
        max_tokens=100,
        temperature=0.7,
        completion_mode=CompletionMode.SEQUENTIAL,
        merge_into_single_document=True,
        max_retries_per_deliverable=2,
        enable_logging=False,  # Disable logging during tests
    )


@pytest.fixture
def app_config():
    """Application configuration for testing."""
    config_data = {
        "version": "test-1.0.0",
        "environment": "test",
        "debug": True,
        "lm_studio": {
            "base_url": "http://localhost:1234/v1",
            "connection_timeout": 10,
            "max_retries": 2,
        },
        "model": {"temperature": 0.7, "max_tokens": 1000, "top_p": 0.9},
        "paths": {"templates": "templates", "output": "output", "logs": "logs"},
        "server": {"host": "127.0.0.1", "port": 8000, "reload": False, "workers": 1},
    }
    return config_data


@pytest.fixture
def test_markdown_content():
    """Sample markdown content for testing."""
    return """
# Test Document

## Overview
This is a test document for validating markdown rendering.

### Features
- Feature 1: Basic text rendering
- Feature 2: Code blocks
- Feature 3: Tables

### Code Example
```python
def hello_world():
    print("Hello, World!")
```

### Table
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Data A   | Data B   | Data C   |

## Conclusion
This document demonstrates various markdown elements.
"""


@pytest.fixture
def deliverable_types():
    """List of deliverable types for testing."""
    from prompt_schema import DeliverableType

    return [
        DeliverableType.PROBLEM_STATEMENT,
        DeliverableType.PERSONAS,
        DeliverableType.USE_CASES,
        DeliverableType.TOOL_OUTLINE,
        DeliverableType.IMPLEMENTATION_INSTRUCTIONS,
        DeliverableType.COPILOT365_PRESENTATION_PROMPT,
        DeliverableType.EFFECTIVENESS_ASSESSMENT,
    ]


@pytest.fixture
def mock_fastapi_request():
    """Mock FastAPI request for web testing."""
    from fastapi import Request

    mock_request = Mock(spec=Request)
    mock_request.method = "POST"
    mock_request.url = Mock()
    mock_request.url.path = "/test"
    mock_request.url.scheme = "http"
    mock_request.headers = {"content-type": "application/json"}
    mock_request.client = Mock()
    mock_request.client.host = "127.0.0.1"
    mock_request.query_params = {}
    mock_request.state = Mock()
    mock_request.state.trace_id = "test-trace-123"
    return mock_request


@pytest.fixture
def mock_websocket():
    """Mock WebSocket for testing."""
    mock_ws = Mock()
    mock_ws.accept = Mock()
    mock_ws.send_text = Mock()
    mock_ws.receive_text = Mock()
    mock_ws.close = Mock()
    return mock_ws


@pytest.fixture(autouse=True)
def cleanup_environment():
    """Automatically cleanup environment variables after each test."""
    original_env = os.environ.copy()
    yield
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def create_test_file():
    """Factory fixture for creating test files."""

    def _create_file(temp_dir: Path, filename: str, content: str) -> Path:
        file_path = temp_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    return _create_file


@pytest.fixture
def assert_valid_markdown():
    """Utility fixture for validating markdown content."""

    def _assert_valid_markdown(content: str):
        assert isinstance(content, str), "Content must be a string"
        assert len(content.strip()) > 0, "Markdown content should not be empty"

        lines = content.split("\n")
        has_headers = any(line.strip().startswith("#") for line in lines)
        assert has_headers, "Markdown should contain headers"

        # Check for common markdown elements
        has_content = any(
            line.strip() and not line.strip().startswith("#") for line in lines
        )
        assert has_content, "Markdown should contain content beyond headers"

        return True

    return _assert_valid_markdown


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for async HTTP testing."""
    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        # Mock response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = Mock()
        mock_response.text = Mock()

        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session.post.return_value.__aenter__.return_value = mock_response

        yield mock_session


# Performance testing fixtures
@pytest.fixture
def performance_threshold():
    """Performance thresholds for testing."""
    return {
        "template_rendering": 1.0,  # seconds
        "schema_processing": 0.1,  # seconds
        "markdown_rendering": 2.0,  # seconds
        "api_response": 5.0,  # seconds
        "file_operations": 0.5,  # seconds
    }


@pytest.fixture
def measure_time():
    """Utility fixture for measuring execution time."""
    import time

    def _measure_time(func, *args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        return result, execution_time

    return _measure_time


# CLI testing fixtures
@pytest.fixture
def cli_runner():
    """Click CLI test runner."""
    from click.testing import CliRunner

    return CliRunner()


@pytest.fixture
def mock_click_context():
    """Mock Click context for CLI testing."""
    from click import Context

    mock_ctx = Mock(spec=Context)
    mock_ctx.obj = {}
    mock_ctx.params = {}
    mock_ctx.exit = Mock()
    mock_ctx.get_help = Mock(return_value="Test help text")
    return mock_ctx


# Database/Storage mocking
@pytest.fixture
def mock_file_operations():
    """Mock file operations for testing."""
    with patch("pathlib.Path.exists") as mock_exists, patch(
        "pathlib.Path.mkdir"
    ) as mock_mkdir, patch("builtins.open", create=True) as mock_open:

        mock_exists.return_value = True
        mock_mkdir.return_value = None

        # Mock file content
        mock_file = Mock()
        mock_file.read.return_value = "test file content"
        mock_file.write.return_value = None
        mock_file.__enter__.return_value = mock_file
        mock_file.__exit__.return_value = None
        mock_open.return_value = mock_file

        yield {
            "exists": mock_exists,
            "mkdir": mock_mkdir,
            "open": mock_open,
            "file": mock_file,
        }


# Error simulation fixtures
@pytest.fixture
def simulate_network_error():
    """Simulate network errors for testing."""

    def _simulate_error(error_type="connection"):
        if error_type == "connection":
            from requests.exceptions import ConnectionError

            return ConnectionError("Simulated connection error")
        elif error_type == "timeout":
            from requests.exceptions import Timeout

            return Timeout("Simulated timeout error")
        elif error_type == "http":
            from requests.exceptions import HTTPError

            return HTTPError("Simulated HTTP error")
        else:
            return Exception("Simulated generic error")

    return _simulate_error


# Logging fixtures
@pytest.fixture
def capture_logs(caplog):
    """Enhanced log capturing with filtering."""
    import logging

    def _get_logs(level=logging.INFO, logger_name=None):
        if logger_name:
            return [
                record
                for record in caplog.records
                if record.levelno >= level and record.name.startswith(logger_name)
            ]
        return [record for record in caplog.records if record.levelno >= level]

    caplog.get_logs = _get_logs
    return caplog


# Parameterized test data
@pytest.fixture(
    params=["simple_prompt", "complex_prompt", "technical_prompt", "business_prompt"]
)
def test_prompts(request):
    """Parameterized test prompts for comprehensive testing."""
    prompts = {
        "simple_prompt": "Create a basic web application",
        "complex_prompt": """
        Project: Enterprise Resource Planning System
        Industry: Manufacturing
        Users: 500+ employees
        Integration: SAP, Oracle, Salesforce
        Compliance: SOX, GDPR
        Budget: $1M+
        Timeline: 18 months
        """,
        "technical_prompt": """
        Develop a microservices architecture
        Technology: Docker, Kubernetes, Python, React
        Database: PostgreSQL, Redis
        Cloud: AWS
        Monitoring: Prometheus, Grafana
        CI/CD: GitHub Actions
        """,
        "business_prompt": """
        Business Problem: Customer churn is 25%
        Goal: Reduce churn to 10%
        Solution: Predictive analytics platform
        Stakeholders: Marketing, Sales, Data Science
        ROI: $2M annually
        Success Metrics: Churn rate, Customer lifetime value
        """,
    }
    return prompts[request.param]


# Cleanup utilities
def pytest_runtest_teardown(item, nextitem):
    """Cleanup after each test."""
    # Clear any module-level caches
    import gc

    gc.collect()


def pytest_sessionstart(session):
    """Session start hook."""
    print("\n🧪 Starting AI Prototyping Tool Test Suite")
    print("=" * 50)


def pytest_sessionfinish(session, exitstatus):
    """Session finish hook."""
    print("\n" + "=" * 50)
    if exitstatus == 0:
        print("✅ All tests passed successfully!")
    else:
        print("❌ Some tests failed. Check the output above.")
    print("🧪 Test session completed")
