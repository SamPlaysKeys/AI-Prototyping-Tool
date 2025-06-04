"""
Structured Logging Module

This module provides structured JSON logging with trace IDs, context management,
and log level control via CLI/web flags for the AI Prototyping Tool.
"""

import json
import logging
import logging.handlers
import os
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, asdict, field
import threading

# Context variable for trace ID
trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)


@dataclass
class LogContext:
    """Log context information."""

    trace_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    operation: Optional[str] = None
    component: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        result = {}
        for key, value in asdict(self).items():
            if value is not None:
                result[key] = value
        return result


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def __init__(
        self,
        include_trace_id: bool = True,
        extra_fields: Optional[Dict[str, Any]] = None,
    ):
        super().__init__()
        self.include_trace_id = include_trace_id
        self.extra_fields = extra_fields or {}

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        # Base log data
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": os.getpid(),
            "thread_id": threading.get_ident(),
        }

        # Add trace ID if available and enabled
        if self.include_trace_id:
            trace_id = trace_id_var.get()
            if trace_id:
                log_data["trace_id"] = trace_id

        # Add exception information
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        # Add extra fields from record
        extra_data = {}
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "exc_info",
                "exc_text",
                "stack_info",
            }:
                extra_data[key] = value

        if extra_data:
            log_data["extra"] = extra_data

        # Add configured extra fields
        if self.extra_fields:
            log_data.update(self.extra_fields)

        # Add context if available
        if hasattr(record, "context") and record.context:
            log_data["context"] = record.context

        return json.dumps(log_data, default=str, ensure_ascii=False)


class SimpleFormatter(logging.Formatter):
    """Simple text formatter with optional trace ID."""

    def __init__(self, include_trace_id: bool = True):
        super().__init__()
        self.include_trace_id = include_trace_id

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as simple text."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        base_format = (
            f"{timestamp} - {record.levelname} - {record.name} - {record.getMessage()}"
        )

        # Add trace ID if available and enabled
        if self.include_trace_id:
            trace_id = trace_id_var.get()
            if trace_id:
                base_format = f"[{trace_id}] {base_format}"

        # Add exception information
        if record.exc_info:
            base_format += "\n" + self.formatException(record.exc_info)

        return base_format


class StructuredLogger:
    """Structured logger with trace ID support and configurable output."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize structured logger.

        Args:
            name: Logger name
            config: Logger configuration dict
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Setup logger with handlers and formatters."""
        # Clear existing handlers
        self.logger.handlers.clear()

        # Set level
        level = self.config.get("level", "INFO")
        self.logger.setLevel(getattr(logging, level.upper()))

        # Determine format type
        format_type = self.config.get("format", "structured")
        include_trace_id = self.config.get("enable_trace_ids", True)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        if format_type == "structured":
            console_formatter = JSONFormatter(include_trace_id=include_trace_id)
        else:
            console_formatter = SimpleFormatter(include_trace_id=include_trace_id)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handlers if enabled
        if self.config.get("enable_file_logging", True):
            self._setup_file_handlers(include_trace_id, format_type)

        # Prevent propagation to root logger
        self.logger.propagate = False

    def _setup_file_handlers(self, include_trace_id: bool, format_type: str) -> None:
        """Setup file logging handlers."""
        log_dir = Path(self.config.get("log_directory", "logs"))
        log_dir.mkdir(parents=True, exist_ok=True)

        max_bytes = self.config.get("max_file_size_mb", 10) * 1024 * 1024
        backup_count = self.config.get("max_files", 5)

        # Application log file (all levels)
        app_log_file = log_dir / "app.log"
        app_handler = logging.handlers.RotatingFileHandler(
            app_log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        app_handler.setLevel(logging.DEBUG)

        # Error log file (warnings and above)
        error_log_file = log_dir / "error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.WARNING)

        # API log file (for API calls and external interactions)
        api_log_file = log_dir / "api.log"
        api_handler = logging.handlers.RotatingFileHandler(
            api_log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        api_handler.setLevel(logging.INFO)
        api_handler.addFilter(
            lambda record: "api" in record.name.lower()
            or hasattr(record, "component")
            and "api" in str(record.component).lower()
        )

        # Set formatters
        if format_type == "structured":
            formatter = JSONFormatter(include_trace_id=include_trace_id)
        else:
            formatter = SimpleFormatter(include_trace_id=include_trace_id)

        app_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        api_handler.setFormatter(formatter)

        self.logger.addHandler(app_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(api_handler)

    def _log_with_context(
        self, level: int, message: str, context: Optional[LogContext] = None, **kwargs
    ) -> None:
        """Log message with context information."""
        # Separate logging args from extra args
        log_kwargs = {}
        extra = {}

        # Reserved logging keywords
        reserved_keys = {"exc_info", "stack_info", "stacklevel", "extra"}

        for key, value in kwargs.items():
            if key in reserved_keys:
                log_kwargs[key] = value
            else:
                extra[key] = value

        # Add context if provided
        if context:
            extra["context"] = context.to_dict()

        # Only pass extra if it's not empty
        if extra:
            log_kwargs["extra"] = extra

        self.logger.log(level, message, **log_kwargs)

    def debug(
        self, message: str, context: Optional[LogContext] = None, **kwargs
    ) -> None:
        """Log debug message."""
        self._log_with_context(logging.DEBUG, message, context, **kwargs)

    def info(
        self, message: str, context: Optional[LogContext] = None, **kwargs
    ) -> None:
        """Log info message."""
        self._log_with_context(logging.INFO, message, context, **kwargs)

    def warning(
        self, message: str, context: Optional[LogContext] = None, **kwargs
    ) -> None:
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, context, **kwargs)

    def error(
        self,
        message: str,
        context: Optional[LogContext] = None,
        exc_info: bool = False,
        **kwargs,
    ) -> None:
        """Log error message."""
        self._log_with_context(
            logging.ERROR, message, context, exc_info=exc_info, **kwargs
        )

    def critical(
        self,
        message: str,
        context: Optional[LogContext] = None,
        exc_info: bool = False,
        **kwargs,
    ) -> None:
        """Log critical message."""
        self._log_with_context(
            logging.CRITICAL, message, context, exc_info=exc_info, **kwargs
        )

    def api_call(
        self,
        method: str,
        url: str,
        status_code: Optional[int] = None,
        duration_ms: Optional[float] = None,
        context: Optional[LogContext] = None,
        **kwargs,
    ) -> None:
        """Log API call with structured data."""
        api_context = context or LogContext()
        api_context.component = "api"
        api_context.metadata.update(
            {
                "method": method,
                "url": url,
                "status_code": status_code,
                "duration_ms": duration_ms,
                **kwargs,
            }
        )

        message = f"{method} {url}"
        if status_code:
            message += f" - {status_code}"
        if duration_ms:
            message += f" ({duration_ms:.2f}ms)"

        level = logging.INFO
        if status_code and status_code >= 400:
            level = logging.WARNING if status_code < 500 else logging.ERROR

        self._log_with_context(level, message, api_context)

    def exception(
        self, message: str, context: Optional[LogContext] = None, **kwargs
    ) -> None:
        """Log exception with traceback."""
        self._log_with_context(logging.ERROR, message, context, exc_info=True, **kwargs)


class TraceManager:
    """Context manager for trace ID management."""

    def __init__(
        self, trace_id: Optional[str] = None, context: Optional[LogContext] = None
    ):
        self.trace_id = trace_id or str(uuid.uuid4())
        self.context = context or LogContext(trace_id=self.trace_id)
        self.token = None

    def __enter__(self) -> "TraceManager":
        self.token = trace_id_var.set(self.trace_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.token:
            trace_id_var.reset(self.token)


def generate_trace_id() -> str:
    """Generate a new trace ID."""
    return str(uuid.uuid4())


def set_trace_id(trace_id: str) -> None:
    """Set the current trace ID."""
    trace_id_var.set(trace_id)


def get_trace_id() -> Optional[str]:
    """Get the current trace ID."""
    return trace_id_var.get()


def setup_logging(
    config: Optional[Dict[str, Any]] = None, logger_name: str = "ai_prototyping_tool"
) -> StructuredLogger:
    """Setup structured logging with configuration."""
    default_config = {
        "level": "INFO",
        "format": "structured",
        "enable_file_logging": True,
        "log_directory": "logs",
        "max_file_size_mb": 10,
        "max_files": 5,
        "enable_trace_ids": True,
    }

    if config:
        default_config.update(config)

    return StructuredLogger(logger_name, default_config)


def setup_cli_logging(verbose: int = 0) -> StructuredLogger:
    """Setup logging for CLI with verbosity levels."""
    level_map = {0: "WARNING", 1: "INFO", 2: "DEBUG"}

    level = level_map.get(verbose, "DEBUG")

    config = {
        "level": level,
        "format": "simple",  # CLI prefers simple format
        "enable_file_logging": True,
        "enable_trace_ids": verbose > 1,  # Only show trace IDs in debug mode
    }

    return setup_logging(config, "ai_prototyping_tool.cli")


def setup_web_logging(debug: bool = False, json_logs: bool = True) -> StructuredLogger:
    """Setup logging for web application."""
    config = {
        "level": "DEBUG" if debug else "INFO",
        "format": "structured" if json_logs else "simple",
        "enable_file_logging": True,
        "enable_trace_ids": True,
    }

    return setup_logging(config, "ai_prototyping_tool.web")


# Global logger instance
_global_logger: Optional[StructuredLogger] = None


def get_logger(name: Optional[str] = None) -> StructuredLogger:
    """Get a structured logger instance."""
    global _global_logger

    if name:
        # Create a new logger for specific component
        from config_manager import get_config

        config = get_config()
        logging_config = {
            "level": config.logging_level,
            "format": "structured",
            "enable_file_logging": True,
            "enable_trace_ids": True,
        }
        return StructuredLogger(name, logging_config)

    if _global_logger is None:
        # Initialize global logger with default config
        _global_logger = setup_logging()

    return _global_logger


def configure_global_logging(config: Dict[str, Any]) -> None:
    """Configure global logging settings."""
    global _global_logger
    _global_logger = setup_logging(config)
