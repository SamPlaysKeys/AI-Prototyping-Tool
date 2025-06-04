"""
Error Handling and Logging Module

This module provides comprehensive error handling, logging, and monitoring
for the AI Prototyping Tool with structured error tracking and recovery.
"""

import logging
import traceback
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Type, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from contextlib import contextmanager
from typing import Optional


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""

    CONFIGURATION = "configuration"
    NETWORK = "network"
    API = "api"
    VALIDATION = "validation"
    FILE_SYSTEM = "file_system"
    TEMPLATE = "template"
    MODEL = "model"
    PARSING = "parsing"
    ORCHESTRATION = "orchestration"
    UNKNOWN = "unknown"


@dataclass
class ErrorInfo:
    """Structured error information with trace ID support."""

    error_id: str
    timestamp: str
    error_type: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    recovery_suggestions: List[str] = field(default_factory=list)
    user_message: Optional[str] = None
    trace_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "error_id": self.error_id,
            "timestamp": self.timestamp,
            "error_type": self.error_type,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "stack_trace": self.stack_trace,
            "context": self.context,
            "recovery_suggestions": self.recovery_suggestions,
            "user_message": self.user_message,
        }

        if self.trace_id:
            result["trace_id"] = self.trace_id

        return result

    def get_user_friendly_message(self) -> str:
        """Get user-friendly error message with trace ID."""
        base_message = self.user_message or self.message

        # Add trace ID for support purposes
        if self.trace_id:
            base_message += f" (Error ID: {self.error_id}, Trace: {self.trace_id[:8]})"
        else:
            base_message += f" (Error ID: {self.error_id})"

        return base_message


class AIPrototypingError(Exception):
    """Base exception class for AI Prototyping Tool."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Dict[str, Any] = None,
        recovery_suggestions: List[str] = None,
        user_message: str = None,
    ):
        super().__init__(message)
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.recovery_suggestions = recovery_suggestions or []
        self.user_message = user_message or message


class ConfigurationError(AIPrototypingError):
    """Configuration-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.CONFIGURATION, **kwargs)


class NetworkError(AIPrototypingError):
    """Network-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.NETWORK, **kwargs)


class APIError(AIPrototypingError):
    """API-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.API, **kwargs)


class ValidationError(AIPrototypingError):
    """Validation-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.VALIDATION, **kwargs)


class FileSystemError(AIPrototypingError):
    """File system-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.FILE_SYSTEM, **kwargs)


class TemplateError(AIPrototypingError):
    """Template-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.TEMPLATE, **kwargs)


class ModelError(AIPrototypingError):
    """Model-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.MODEL, **kwargs)


class ParsingError(AIPrototypingError):
    """Parsing-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.PARSING, **kwargs)


class OrchestrationError(AIPrototypingError):
    """Orchestration-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.ORCHESTRATION, **kwargs)


class ErrorHandler:
    """Central error handling and logging system."""

    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialize the error handler.

        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir) if log_dir else self._get_default_log_dir()
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Error tracking
        self.error_history: List[ErrorInfo] = []
        self.error_counts: Dict[str, int] = {}
        self.max_history = 1000

        # Setup logging
        self._setup_logging()

        # Error recovery strategies
        self.recovery_strategies = self._init_recovery_strategies()

    def _get_default_log_dir(self) -> Path:
        """Get default log directory."""
        if os.name == "nt":  # Windows
            base_dir = Path(os.environ.get("APPDATA", Path.home()))
        else:  # Unix-like
            base_dir = Path.home() / ".local" / "share"

        return base_dir / "ai-prototyping-tool" / "logs"

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        # Create formatters
        detailed_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )

        simple_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

        # Setup file handlers
        error_log_file = self.log_dir / "error.log"
        app_log_file = self.log_dir / "app.log"

        # Error file handler (ERROR and above)
        error_handler = logging.FileHandler(error_log_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)

        # Application file handler (INFO and above)
        app_handler = logging.FileHandler(app_log_file)
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(detailed_formatter)

        # Console handler (WARNING and above)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(simple_formatter)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(error_handler)
        root_logger.addHandler(app_handler)
        root_logger.addHandler(console_handler)

        # Create specific logger for this module
        self.logger = logging.getLogger(__name__)

    def _init_recovery_strategies(self) -> Dict[ErrorCategory, List[str]]:
        """Initialize recovery strategies for different error categories."""
        return {
            ErrorCategory.CONFIGURATION: [
                "Check configuration file syntax and values",
                "Reset configuration to defaults",
                "Verify file permissions",
                "Check environment variables",
            ],
            ErrorCategory.NETWORK: [
                "Check internet connectivity",
                "Verify firewall settings",
                "Try different network connection",
                "Check proxy settings",
            ],
            ErrorCategory.API: [
                "Verify API endpoints and credentials",
                "Check API rate limits",
                "Retry with exponential backoff",
                "Check service status",
            ],
            ErrorCategory.VALIDATION: [
                "Review input data format",
                "Check required fields",
                "Verify data types and ranges",
                "Use example/template data",
            ],
            ErrorCategory.FILE_SYSTEM: [
                "Check file permissions",
                "Verify disk space",
                "Check file path validity",
                "Create missing directories",
            ],
            ErrorCategory.TEMPLATE: [
                "Verify template syntax",
                "Check variable names",
                "Validate template structure",
                "Reset template to default",
            ],
            ErrorCategory.MODEL: [
                "Check model availability",
                "Verify model parameters",
                "Try different model",
                "Check LM Studio status",
            ],
            ErrorCategory.PARSING: [
                "Check input format",
                "Verify encoding",
                "Simplify input structure",
                "Use alternative parser",
            ],
            ErrorCategory.ORCHESTRATION: [
                "Check component dependencies",
                "Verify system resources",
                "Review orchestration configuration",
                "Restart components",
            ],
        }

    def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any] = None,
        trace_id: Optional[str] = None,
    ) -> ErrorInfo:
        """Handle and log an error with trace ID support."""
        # Import here to avoid circular imports
        from structured_logger import get_trace_id, LogContext

        # Use provided trace_id or get from context
        if not trace_id:
            trace_id = get_trace_id()

        # Generate unique error ID (include trace_id if available)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        if trace_id:
            error_id = f"ERR_{timestamp_str}_{trace_id[:8]}_{id(error) % 10000:04d}"
        else:
            error_id = f"ERR_{timestamp_str}_{id(error) % 10000:04d}"

        # Determine error category and severity
        if isinstance(error, AIPrototypingError):
            category = error.category
            severity = error.severity
            user_message = error.user_message
            details = error.details
            recovery_suggestions = error.recovery_suggestions
        else:
            category = self._classify_error(error)
            severity = self._assess_severity(error)
            user_message = str(error)
            details = {}
            recovery_suggestions = self.recovery_strategies.get(category, [])

        # Create error info
        error_info = ErrorInfo(
            error_id=error_id,
            timestamp=datetime.now().isoformat(),
            error_type=type(error).__name__,
            category=category,
            severity=severity,
            message=str(error),
            details=details,
            stack_trace=traceback.format_exc(),
            context=context or {},
            recovery_suggestions=recovery_suggestions,
            user_message=user_message,
        )

        # Add trace_id to error info if available
        if trace_id:
            error_info.details["trace_id"] = trace_id

        # Log the error with structured logging
        self._log_error_structured(error_info, trace_id)

        # Track error
        self._track_error(error_info)

        # Save error details
        self._save_error_details(error_info)

        return error_info

    def _classify_error(self, error: Exception) -> ErrorCategory:
        """Classify error by type and message."""
        error_type = type(error).__name__
        error_message = str(error).lower()

        # Classification rules
        if any(
            keyword in error_message for keyword in ["config", "setting", "parameter"]
        ):
            return ErrorCategory.CONFIGURATION
        elif any(
            keyword in error_message for keyword in ["network", "connection", "timeout"]
        ):
            return ErrorCategory.NETWORK
        elif any(
            keyword in error_message
            for keyword in ["api", "http", "request", "response"]
        ):
            return ErrorCategory.API
        elif any(
            keyword in error_message
            for keyword in ["validation", "invalid", "required"]
        ):
            return ErrorCategory.VALIDATION
        elif any(
            keyword in error_message
            for keyword in ["file", "directory", "path", "permission"]
        ):
            return ErrorCategory.FILE_SYSTEM
        elif any(
            keyword in error_message for keyword in ["template", "jinja", "render"]
        ):
            return ErrorCategory.TEMPLATE
        elif any(
            keyword in error_message
            for keyword in ["model", "completion", "generation"]
        ):
            return ErrorCategory.MODEL
        elif any(keyword in error_message for keyword in ["parse", "syntax", "format"]):
            return ErrorCategory.PARSING
        elif any(
            keyword in error_message
            for keyword in ["orchestrat", "workflow", "process"]
        ):
            return ErrorCategory.ORCHESTRATION
        else:
            return ErrorCategory.UNKNOWN

    def _assess_severity(self, error: Exception) -> ErrorSeverity:
        """Assess error severity."""
        error_type = type(error).__name__
        error_message = str(error).lower()

        # Critical errors
        if any(keyword in error_message for keyword in ["critical", "fatal", "system"]):
            return ErrorSeverity.CRITICAL

        # High severity errors
        if error_type in ["SystemError", "MemoryError", "OSError"]:
            return ErrorSeverity.HIGH

        # Medium severity errors
        if error_type in ["ValueError", "TypeError", "KeyError", "AttributeError"]:
            return ErrorSeverity.MEDIUM

        # Low severity by default
        return ErrorSeverity.LOW

    def _log_error(self, error_info: ErrorInfo) -> None:
        """Log error information (legacy method)."""
        log_message = f"[{error_info.error_id}] {error_info.category.value.upper()}: {error_info.message}"

        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

        # Log additional details
        if error_info.details:
            self.logger.debug(
                f"Error details: {json.dumps(error_info.details, indent=2)}"
            )

        if error_info.context:
            self.logger.debug(
                f"Error context: {json.dumps(error_info.context, indent=2)}"
            )

    def _log_error_structured(
        self, error_info: ErrorInfo, trace_id: Optional[str] = None
    ) -> None:
        """Log error information using structured logging."""
        from structured_logger import get_logger, LogContext

        # Get structured logger
        structured_logger = get_logger("ai_prototyping_tool.errors")

        # Create log context
        log_context = LogContext(
            trace_id=trace_id,
            component="error_handler",
            operation="handle_error",
            metadata={
                "error_id": error_info.error_id,
                "error_type": error_info.error_type,
                "category": error_info.category.value,
                "severity": error_info.severity.value,
                "details": error_info.details,
                "context": error_info.context,
                "recovery_suggestions": error_info.recovery_suggestions,
            },
        )

        # Log based on severity
        log_message = f"[{error_info.error_id}] {error_info.category.value.upper()}: {error_info.message}"

        if error_info.severity == ErrorSeverity.CRITICAL:
            structured_logger.critical(log_message, context=log_context, exc_info=True)
        elif error_info.severity == ErrorSeverity.HIGH:
            structured_logger.error(log_message, context=log_context, exc_info=True)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            structured_logger.warning(log_message, context=log_context)
        else:
            structured_logger.info(log_message, context=log_context)

    def _track_error(self, error_info: ErrorInfo) -> None:
        """Track error in history."""
        # Add to history
        self.error_history.append(error_info)

        # Maintain history size
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history :]

        # Update counts
        error_key = f"{error_info.category.value}:{error_info.error_type}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

    def _save_error_details(self, error_info: ErrorInfo) -> None:
        """Save detailed error information to file."""
        error_file = self.log_dir / f"error_{error_info.error_id}.json"

        try:
            with open(error_file, "w", encoding="utf-8") as f:
                json.dump(error_info.to_dict(), f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save error details: {e}")

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        if not self.error_history:
            return {
                "total_errors": 0,
                "by_category": {},
                "by_severity": {},
                "recent_errors": [],
            }

        # Count by category
        by_category = {}
        for error in self.error_history:
            category = error.category.value
            by_category[category] = by_category.get(category, 0) + 1

        # Count by severity
        by_severity = {}
        for error in self.error_history:
            severity = error.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1

        # Recent errors (last 10)
        recent_errors = [
            {
                "error_id": err.error_id,
                "timestamp": err.timestamp,
                "category": err.category.value,
                "severity": err.severity.value,
                "message": err.message,
            }
            for err in self.error_history[-10:]
        ]

        return {
            "total_errors": len(self.error_history),
            "by_category": by_category,
            "by_severity": by_severity,
            "recent_errors": recent_errors,
            "error_counts": self.error_counts,
        }

    def get_recovery_suggestions(self, category: ErrorCategory) -> List[str]:
        """Get recovery suggestions for an error category."""
        return self.recovery_strategies.get(category, [])

    def clear_error_history(self) -> None:
        """Clear error history."""
        self.error_history.clear()
        self.error_counts.clear()
        self.logger.info("Error history cleared")

    @contextmanager
    def error_context(self, context: Dict[str, Any]):
        """Context manager for error handling with additional context."""
        try:
            yield
        except Exception as e:
            self.handle_error(e, context)
            raise

    def create_user_friendly_message(self, error_info: ErrorInfo) -> str:
        """Create a user-friendly error message."""
        base_message = error_info.user_message or error_info.message

        suggestions = "\n".join(
            [f"• {suggestion}" for suggestion in error_info.recovery_suggestions[:3]]
        )

        if suggestions:
            return f"{base_message}\n\nSuggested solutions:\n{suggestions}"
        else:
            return base_message


# Global error handler instance
_error_handler = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def handle_error(
    error: Exception, context: Dict[str, Any] = None, trace_id: Optional[str] = None
) -> ErrorInfo:
    """Handle an error using the global error handler."""
    return get_error_handler().handle_error(error, context, trace_id)


def get_error_stats() -> Dict[str, Any]:
    """Get error statistics from the global error handler."""
    return get_error_handler().get_error_stats()


@contextmanager
def error_context(context: Dict[str, Any]):
    """Context manager for error handling with additional context."""
    with get_error_handler().error_context(context):
        yield
