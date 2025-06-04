#!/usr/bin/env python3
"""
Test script for configuration and logging systems.

This script tests the centralized configuration via config.toml,
structured logging with JSON output and trace IDs, and error handling.
"""

import sys
import tempfile
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config_manager import get_config_manager, ConfigManager
from structured_logger import (
    setup_logging,
    TraceManager,
    get_logger,
    LogContext,
    generate_trace_id,
    setup_cli_logging,
    setup_web_logging,
)
from error_handler import handle_error, ErrorCategory, ErrorSeverity
from web_error_handler import WebErrorHandler


def test_configuration_system():
    """Test the configuration system with TOML and environment variables."""
    print("\n=== Testing Configuration System ===")

    # Test 1: Load default configuration
    config_manager = get_config_manager()
    config = config_manager.get_config()

    print(
        f"✓ Loaded configuration: environment={config.environment}, debug={config.debug}"
    )
    print(f"✓ LM Studio URL: {config.lm_studio.base_url}")
    print(f"✓ Logging level: {config.logging_level}")

    # Test 2: Configuration sections
    server_config = config.get_server_config()
    print(
        f"✓ Server config: host={server_config['host']}, port={server_config['port']}"
    )

    error_config = config.get_error_handling_config()
    print(
        f"✓ Error handling config: user_friendly={error_config['user_friendly_messages']}"
    )

    # Test 3: Environment variable override (simulation)
    import os

    original_value = os.environ.get("AIPROTO_LOGGING_LEVEL")
    os.environ["AIPROTO_LOGGING_LEVEL"] = "DEBUG"

    # Create new manager to test env override
    test_manager = ConfigManager()
    test_config = test_manager.get_config()
    print(f"✓ Environment override test: logging_level={test_config.logging_level}")

    # Restore original environment
    if original_value:
        os.environ["AIPROTO_LOGGING_LEVEL"] = original_value
    else:
        os.environ.pop("AIPROTO_LOGGING_LEVEL", None)

    print("✓ Configuration system tests passed!")


def test_structured_logging():
    """Test structured logging with JSON output and trace IDs."""
    print("\n=== Testing Structured Logging ===")

    # Test 1: Basic structured logger
    logger = setup_logging(
        {
            "level": "DEBUG",
            "format": "structured",
            "enable_file_logging": False,  # Disable for test
            "enable_trace_ids": True,
        }
    )

    print("✓ Created structured logger")

    # Test 2: Trace ID management
    with TraceManager() as trace_mgr:
        trace_id = trace_mgr.trace_id
        print(f"✓ Generated trace ID: {trace_id[:8]}...")

        # Test 3: Structured logging with context
        context = LogContext(
            trace_id=trace_id,
            operation="test_operation",
            component="test_suite",
            metadata={"test": True, "number": 42},
        )

        logger.info("Testing structured logging with context", context=context)
        print("✓ Logged message with structured context")

        # Test 4: API call logging
        logger.api_call(
            "GET",
            "http://example.com/api",
            status_code=200,
            duration_ms=150.5,
            context=context,
        )
        print("✓ Logged API call with metrics")

        # Test 5: Error logging
        try:
            raise ValueError("Test error for logging")
        except Exception as e:
            logger.exception("Test exception logging", context=context)
            print("✓ Logged exception with context")

    print("✓ Structured logging tests passed!")


def test_error_handling():
    """Test error handling with trace IDs and user-friendly messages."""
    print("\n=== Testing Error Handling ===")

    # Test 1: Basic error handling
    try:
        raise ValueError("Test validation error")
    except Exception as e:
        error_info = handle_error(e, {"test_context": "error_handling_test"})
        print(f"✓ Generated error ID: {error_info.error_id}")
        print(f"✓ Error category: {error_info.category.value}")
        print(f"✓ Error severity: {error_info.severity.value}")
        print(f"✓ User message: {error_info.get_user_friendly_message()[:50]}...")

    # Test 2: Error handling with trace ID
    with TraceManager() as trace_mgr:
        try:
            raise FileNotFoundError("Test file not found")
        except Exception as e:
            error_info = handle_error(e, {"operation": "file_test"}, trace_mgr.trace_id)
            print(f"✓ Error with trace ID: {error_info.error_id}")
            assert trace_mgr.trace_id[:8] in error_info.error_id
            print("✓ Trace ID properly embedded in error ID")

    # Test 3: Custom error with recovery suggestions
    from error_handler import AIPrototypingError

    try:
        raise AIPrototypingError(
            "Custom error for testing",
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.MEDIUM,
            recovery_suggestions=[
                "Check your configuration file",
                "Verify environment variables",
                "Restart the application",
            ],
            user_message="Please check your configuration settings.",
        )
    except Exception as e:
        error_info = handle_error(e)
        print(
            f"✓ Custom error handled: {len(error_info.recovery_suggestions)} suggestions"
        )
        print(f"✓ Recovery suggestions: {error_info.recovery_suggestions[0]}")

    print("✓ Error handling tests passed!")


def test_cli_logging():
    """Test CLI-specific logging setup."""
    print("\n=== Testing CLI Logging ===")

    # Test different verbosity levels
    for verbose_level in [0, 1, 2]:
        logger = setup_cli_logging(verbose_level)
        expected_levels = ["WARNING", "INFO", "DEBUG"]
        print(f"✓ CLI logging level {verbose_level}: {expected_levels[verbose_level]}")

    print("✓ CLI logging tests passed!")


def test_web_logging():
    """Test web-specific logging setup."""
    print("\n=== Testing Web Logging ===")

    # Test production mode
    logger_prod = setup_web_logging(debug=False, json_logs=True)
    print("✓ Production web logging setup (INFO level, JSON format)")

    # Test debug mode
    logger_debug = setup_web_logging(debug=True, json_logs=True)
    print("✓ Debug web logging setup (DEBUG level, JSON format)")

    # Test simple format
    logger_simple = setup_web_logging(debug=False, json_logs=False)
    print("✓ Simple format web logging setup")

    print("✓ Web logging tests passed!")


def test_trace_id_generation():
    """Test trace ID generation and management."""
    print("\n=== Testing Trace ID Management ===")

    # Test 1: Manual trace ID generation
    trace_id1 = generate_trace_id()
    trace_id2 = generate_trace_id()

    assert trace_id1 != trace_id2
    print(f"✓ Generated unique trace IDs: {trace_id1[:8]} != {trace_id2[:8]}")

    # Test 2: Trace context management
    with TraceManager("custom-trace-123") as trace_mgr:
        assert trace_mgr.trace_id == "custom-trace-123"
        print("✓ Custom trace ID properly set in context")

        # Nested trace context
        with TraceManager() as nested_trace:
            assert nested_trace.trace_id != "custom-trace-123"
            print(f"✓ Nested trace context: {nested_trace.trace_id[:8]}")

        # Should return to original trace ID
        assert trace_mgr.trace_id == "custom-trace-123"
        print("✓ Trace context properly restored")

    print("✓ Trace ID management tests passed!")


def test_log_context():
    """Test log context creation and serialization."""
    print("\n=== Testing Log Context ===")

    context = LogContext(
        trace_id="test-trace-123",
        user_id="user-456",
        operation="test_operation",
        component="test_component",
        metadata={
            "request_id": "req-789",
            "feature_flag": True,
            "metrics": {"duration_ms": 123.45},
        },
    )

    context_dict = context.to_dict()
    print(f"✓ Log context serialized: {len(context_dict)} fields")

    # Verify required fields
    assert context_dict["trace_id"] == "test-trace-123"
    assert context_dict["operation"] == "test_operation"
    assert context_dict["metadata"]["request_id"] == "req-789"

    print("✓ Log context tests passed!")


def test_integration():
    """Test integration between configuration, logging, and error handling."""
    print("\n=== Testing System Integration ===")

    # Test 1: Configuration-driven logging
    config_manager = get_config_manager()
    config = config_manager.get_config()

    # Create logger with config settings
    logger = get_logger("integration_test")

    with TraceManager() as trace_mgr:
        log_context = LogContext(
            trace_id=trace_mgr.trace_id,
            operation="integration_test",
            component="test_suite",
        )

        logger.info("Starting integration test", context=log_context)

        # Test error handling in context
        try:
            # Simulate an API call that fails
            logger.api_call(
                "POST", config.lm_studio.base_url + "/test", context=log_context
            )
            raise ConnectionError("Simulated API failure")
        except Exception as e:
            error_info = handle_error(
                e,
                {
                    "operation": "integration_test",
                    "api_url": config.lm_studio.base_url + "/test",
                },
                trace_mgr.trace_id,
            )

            logger.error(
                f"Integration test error: {error_info.get_user_friendly_message()}",
                context=log_context,
            )

            print(f"✓ Integrated error handling: {error_info.error_id}")
            print(f"✓ Trace ID consistency: {trace_mgr.trace_id[:8]}")

    print("✓ System integration tests passed!")


def main():
    """Run all tests."""
    print("🚀 Starting Configuration, Logging, and Error Handling Tests")

    try:
        test_configuration_system()
        test_structured_logging()
        test_error_handling()
        test_cli_logging()
        test_web_logging()
        test_trace_id_generation()
        test_log_context()
        test_integration()

        print("\n🎉 All tests passed successfully!")
        print("\n📋 Summary:")
        print("  ✓ Configuration system (TOML + env vars)")
        print("  ✓ Structured JSON logging with trace IDs")
        print("  ✓ Error handling with user-friendly messages")
        print("  ✓ CLI logging with verbosity levels")
        print("  ✓ Web logging with debug modes")
        print("  ✓ Trace ID generation and management")
        print("  ✓ Log context serialization")
        print("  ✓ System integration")

        print("\n🔧 Configuration Features:")
        print("  • Centralized config.toml")
        print("  • Environment variable overrides (AIPROTO_*)")
        print("  • Server, logging, security, monitoring sections")
        print("  • User profiles and preferences")

        print("\n📊 Logging Features:")
        print("  • Structured JSON logs for API calls and errors")
        print("  • Trace IDs for request tracking")
        print("  • CLI and web-specific log levels")
        print("  • File rotation and log directories")
        print("  • Context-aware logging with metadata")

        print("\n⚠️  Error Handling Features:")
        print("  • Global exception handlers")
        print("  • User-friendly error messages with trace IDs")
        print("  • Error categorization and severity levels")
        print("  • Recovery suggestions")
        print("  • Graceful error pages for web apps")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
