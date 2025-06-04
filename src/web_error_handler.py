"""
Web Error Handler Module

This module provides graceful error handling for web applications with
user-friendly error pages and trace ID support.
"""

import json
import traceback
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify, render_template_string, g
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from structured_logger import get_logger, LogContext, TraceManager, generate_trace_id
from error_handler import handle_error, ErrorInfo, ErrorSeverity


class WebErrorHandler:
    """Web-specific error handler with trace ID support and graceful error pages."""

    def __init__(
        self,
        app: Optional[Any] = None,
        template_dir: Optional[str] = None,
        enable_debug: bool = False,
    ):
        """
        Initialize web error handler.

        Args:
            app: Flask or FastAPI application instance
            template_dir: Directory containing error page templates
            enable_debug: Whether to show debug information in error pages
        """
        self.app = app
        self.template_dir = Path(template_dir) if template_dir else None
        self.enable_debug = enable_debug
        self.logger = get_logger("ai_prototyping_tool.web.errors")

        # Default error templates
        self.default_templates = {
            "html": self._get_default_html_template(),
            "json": self._get_default_json_template(),
        }

        if app:
            self.init_app(app)

    def init_app(self, app: Any) -> None:
        """Initialize error handler with Flask or FastAPI app."""
        self.app = app

        if hasattr(app, "errorhandler"):  # Flask
            self._setup_flask_handlers(app)
        elif hasattr(app, "exception_handler"):  # FastAPI
            self._setup_fastapi_handlers(app)
        else:
            raise ValueError("Unsupported application type. Must be Flask or FastAPI.")

    def _setup_flask_handlers(self, app: Flask) -> None:
        """Setup error handlers for Flask application."""

        @app.before_request
        def before_request():
            """Setup trace ID for request."""
            trace_id = request.headers.get("X-Trace-ID") or generate_trace_id()
            g.trace_id = trace_id

            # Set trace ID in context
            from structured_logger import set_trace_id

            set_trace_id(trace_id)

        @app.errorhandler(Exception)
        def handle_exception(error: Exception):
            """Handle all exceptions with structured logging and graceful pages."""
            return self._handle_web_error(error, request=request)

        @app.errorhandler(404)
        def handle_404(error):
            """Handle 404 errors."""
            return self._handle_http_error(404, "Page not found", request=request)

        @app.errorhandler(500)
        def handle_500(error):
            """Handle 500 errors."""
            return self._handle_http_error(
                500, "Internal server error", request=request
            )

    def _setup_fastapi_handlers(self, app: FastAPI) -> None:
        """Setup error handlers for FastAPI application."""

        @app.middleware("http")
        async def trace_middleware(request: Request, call_next):
            """Add trace ID to request context."""
            trace_id = request.headers.get("x-trace-id") or generate_trace_id()
            request.state.trace_id = trace_id

            # Set trace ID in context
            from structured_logger import set_trace_id

            set_trace_id(trace_id)

            response = await call_next(request)
            response.headers["X-Trace-ID"] = trace_id
            return response

        @app.exception_handler(Exception)
        async def handle_exception(request: Request, exc: Exception):
            """Handle all exceptions with structured logging and graceful pages."""
            return await self._handle_web_error_async(exc, request=request)

        @app.exception_handler(HTTPException)
        async def handle_http_exception(request: Request, exc: HTTPException):
            """Handle HTTP exceptions."""
            return await self._handle_http_error_async(
                exc.status_code, exc.detail, request=request
            )

    def _handle_web_error(
        self, error: Exception, request: Optional[Any] = None
    ) -> Tuple[str, int, Dict[str, str]]:
        """Handle web error for Flask."""
        trace_id = getattr(g, "trace_id", None) if request else None

        # Create request context
        request_context = self._build_request_context(request)

        # Handle the error with structured logging
        error_info = handle_error(error, request_context, trace_id)

        # Log web-specific information
        self._log_web_error(error_info, request, trace_id)

        # Determine response format
        accept_header = request.headers.get("Accept", "") if request else ""
        wants_json = (
            "application/json" in accept_header or "/json" in str(request.path)
            if request
            else False
        )

        status_code = self._get_status_code_from_error(error)

        if wants_json:
            return self._create_json_error_response(error_info, status_code)
        else:
            return self._create_html_error_response(error_info, status_code)

    async def _handle_web_error_async(
        self, error: Exception, request: Optional[Request] = None
    ) -> JSONResponse:
        """Handle web error for FastAPI."""
        trace_id = getattr(request.state, "trace_id", None) if request else None

        # Create request context
        request_context = self._build_request_context_async(request)

        # Handle the error with structured logging
        error_info = handle_error(error, request_context, trace_id)

        # Log web-specific information
        self._log_web_error(error_info, request, trace_id)

        # Determine response format
        accept_header = request.headers.get("accept", "") if request else ""
        wants_json = (
            "application/json" in accept_header or "/json" in str(request.url)
            if request
            else True
        )

        status_code = self._get_status_code_from_error(error)

        if wants_json:
            return self._create_json_error_response_async(error_info, status_code)
        else:
            return self._create_html_error_response_async(error_info, status_code)

    def _handle_http_error(
        self, status_code: int, message: str, request: Optional[Any] = None
    ) -> Tuple[str, int, Dict[str, str]]:
        """Handle HTTP error for Flask."""
        trace_id = getattr(g, "trace_id", None) if request else None

        # Create minimal error info for HTTP errors
        error_info = ErrorInfo(
            error_id=f"HTTP_{status_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            error_type="HTTPError",
            category="network",
            severity=ErrorSeverity.MEDIUM if status_code < 500 else ErrorSeverity.HIGH,
            message=message,
            trace_id=trace_id,
        )

        # Log HTTP error
        request_context = self._build_request_context(request)
        log_context = LogContext(
            trace_id=trace_id,
            component="web_error_handler",
            operation="http_error",
            metadata={
                "status_code": status_code,
                "message": message,
                "path": request.path if request else None,
                "method": request.method if request else None,
            },
        )

        if status_code >= 500:
            self.logger.error(f"HTTP {status_code}: {message}", context=log_context)
        else:
            self.logger.warning(f"HTTP {status_code}: {message}", context=log_context)

        # Determine response format
        accept_header = request.headers.get("Accept", "") if request else ""
        wants_json = "application/json" in accept_header

        if wants_json:
            return self._create_json_error_response(error_info, status_code)
        else:
            return self._create_html_error_response(error_info, status_code)

    async def _handle_http_error_async(
        self, status_code: int, message: str, request: Optional[Request] = None
    ) -> JSONResponse:
        """Handle HTTP error for FastAPI."""
        trace_id = getattr(request.state, "trace_id", None) if request else None

        # Create minimal error info for HTTP errors
        error_info = ErrorInfo(
            error_id=f"HTTP_{status_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            error_type="HTTPError",
            category="network",
            severity=ErrorSeverity.MEDIUM if status_code < 500 else ErrorSeverity.HIGH,
            message=message,
            trace_id=trace_id,
        )

        # Log HTTP error
        request_context = self._build_request_context_async(request)
        log_context = LogContext(
            trace_id=trace_id,
            component="web_error_handler",
            operation="http_error",
            metadata={
                "status_code": status_code,
                "message": message,
                "path": str(request.url.path) if request else None,
                "method": request.method if request else None,
            },
        )

        if status_code >= 500:
            self.logger.error(f"HTTP {status_code}: {message}", context=log_context)
        else:
            self.logger.warning(f"HTTP {status_code}: {message}", context=log_context)

        # Determine response format
        accept_header = request.headers.get("accept", "") if request else ""
        wants_json = "application/json" in accept_header

        if wants_json:
            return self._create_json_error_response_async(error_info, status_code)
        else:
            return self._create_html_error_response_async(error_info, status_code)

    def _build_request_context(self, request: Optional[Any]) -> Dict[str, Any]:
        """Build request context for Flask."""
        if not request:
            return {}

        return {
            "request": {
                "method": getattr(request, "method", None),
                "path": getattr(request, "path", None),
                "url": str(getattr(request, "url", "")),
                "remote_addr": getattr(request, "remote_addr", None),
                "user_agent": (
                    str(request.headers.get("User-Agent", ""))
                    if hasattr(request, "headers")
                    else None
                ),
                "headers": dict(request.headers) if hasattr(request, "headers") else {},
                "args": dict(request.args) if hasattr(request, "args") else {},
                "form": dict(request.form) if hasattr(request, "form") else {},
            }
        }

    def _build_request_context_async(
        self, request: Optional[Request]
    ) -> Dict[str, Any]:
        """Build request context for FastAPI."""
        if not request:
            return {}

        return {
            "request": {
                "method": request.method,
                "path": str(request.url.path),
                "url": str(request.url),
                "client": str(request.client) if request.client else None,
                "user_agent": request.headers.get("user-agent", ""),
                "headers": dict(request.headers),
                "query_params": dict(request.query_params),
            }
        }

    def _log_web_error(
        self, error_info: ErrorInfo, request: Optional[Any], trace_id: Optional[str]
    ) -> None:
        """Log web-specific error information."""
        log_context = LogContext(
            trace_id=trace_id,
            component="web_error_handler",
            operation="handle_web_error",
            metadata={
                "error_id": error_info.error_id,
                "error_type": error_info.error_type,
                "status_code": self._get_status_code_from_error_info(error_info),
            },
        )

        if error_info.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
            self.logger.error(
                f"Web error: {error_info.message}", context=log_context, exc_info=True
            )
        else:
            self.logger.warning(f"Web error: {error_info.message}", context=log_context)

    def _get_status_code_from_error(self, error: Exception) -> int:
        """Get HTTP status code from error."""
        if hasattr(error, "status_code"):
            return error.status_code
        elif isinstance(error, (PermissionError, OSError)):
            return 403
        elif isinstance(error, (ValueError, TypeError)):
            return 400
        elif isinstance(error, FileNotFoundError):
            return 404
        else:
            return 500

    def _get_status_code_from_error_info(self, error_info: ErrorInfo) -> int:
        """Get HTTP status code from error info."""
        if error_info.error_type == "HTTPError":
            return 500  # Default for unspecified HTTP errors
        elif error_info.severity == ErrorSeverity.CRITICAL:
            return 500
        elif error_info.severity == ErrorSeverity.HIGH:
            return 500
        elif error_info.category.value == "validation":
            return 400
        elif error_info.category.value == "network":
            return 503
        else:
            return 500

    def _create_json_error_response(
        self, error_info: ErrorInfo, status_code: int
    ) -> Tuple[str, int, Dict[str, str]]:
        """Create JSON error response for Flask."""
        response_data = {
            "error": {
                "id": error_info.error_id,
                "type": error_info.error_type,
                "message": error_info.get_user_friendly_message(),
                "category": error_info.category.value,
                "severity": error_info.severity.value,
                "timestamp": error_info.timestamp,
                "trace_id": error_info.trace_id,
            }
        }

        if self.enable_debug and error_info.stack_trace:
            response_data["error"]["debug"] = {
                "stack_trace": error_info.stack_trace,
                "details": error_info.details,
            }

        if error_info.recovery_suggestions:
            response_data["error"]["suggestions"] = error_info.recovery_suggestions

        return (
            json.dumps(response_data, indent=2),
            status_code,
            {"Content-Type": "application/json"},
        )

    def _create_json_error_response_async(
        self, error_info: ErrorInfo, status_code: int
    ) -> JSONResponse:
        """Create JSON error response for FastAPI."""
        response_data = {
            "error": {
                "id": error_info.error_id,
                "type": error_info.error_type,
                "message": error_info.get_user_friendly_message(),
                "category": error_info.category.value,
                "severity": error_info.severity.value,
                "timestamp": error_info.timestamp,
                "trace_id": error_info.trace_id,
            }
        }

        if self.enable_debug and error_info.stack_trace:
            response_data["error"]["debug"] = {
                "stack_trace": error_info.stack_trace,
                "details": error_info.details,
            }

        if error_info.recovery_suggestions:
            response_data["error"]["suggestions"] = error_info.recovery_suggestions

        return JSONResponse(
            content=response_data,
            status_code=status_code,
            headers={"X-Trace-ID": error_info.trace_id} if error_info.trace_id else {},
        )

    def _create_html_error_response(
        self, error_info: ErrorInfo, status_code: int
    ) -> Tuple[str, int, Dict[str, str]]:
        """Create HTML error response for Flask."""
        template_vars = {
            "error_id": error_info.error_id,
            "trace_id": error_info.trace_id,
            "title": f"Error {status_code}",
            "message": error_info.get_user_friendly_message(),
            "timestamp": error_info.timestamp,
            "category": error_info.category.value.title(),
            "severity": error_info.severity.value.title(),
            "suggestions": error_info.recovery_suggestions,
            "debug": self.enable_debug,
            "stack_trace": error_info.stack_trace if self.enable_debug else None,
            "details": error_info.details if self.enable_debug else None,
        }

        html_content = render_template_string(
            self.default_templates["html"], **template_vars
        )
        return html_content, status_code, {"Content-Type": "text/html"}

    def _create_html_error_response_async(
        self, error_info: ErrorInfo, status_code: int
    ) -> HTMLResponse:
        """Create HTML error response for FastAPI."""
        template_vars = {
            "error_id": error_info.error_id,
            "trace_id": error_info.trace_id,
            "title": f"Error {status_code}",
            "message": error_info.get_user_friendly_message(),
            "timestamp": error_info.timestamp,
            "category": error_info.category.value.title(),
            "severity": error_info.severity.value.title(),
            "suggestions": error_info.recovery_suggestions,
            "debug": self.enable_debug,
            "stack_trace": error_info.stack_trace if self.enable_debug else None,
            "details": error_info.details if self.enable_debug else None,
        }

        # Simple template rendering for FastAPI
        html_content = self._render_template(
            self.default_templates["html"], **template_vars
        )

        headers = {"X-Trace-ID": error_info.trace_id} if error_info.trace_id else {}
        return HTMLResponse(
            content=html_content, status_code=status_code, headers=headers
        )

    def _render_template(self, template: str, **kwargs) -> str:
        """Simple template rendering."""
        import re

        def replace_var(match):
            var_name = match.group(1)
            return str(kwargs.get(var_name, ""))

        # Simple variable substitution
        return re.sub(r"\{\{\s*(\w+)\s*\}\}", replace_var, template)

    def _get_default_html_template(self) -> str:
        """Get default HTML error page template."""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ title }} - AI Prototyping Tool</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                    color: #333;
                }
                .error-container {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                }
                .error-icon {
                    font-size: 64px;
                    color: #e74c3c;
                    margin-bottom: 20px;
                }
                .error-title {
                    font-size: 32px;
                    margin-bottom: 10px;
                    color: #2c3e50;
                }
                .error-message {
                    font-size: 18px;
                    margin-bottom: 30px;
                    color: #7f8c8d;
                    line-height: 1.5;
                }
                .error-details {
                    background: #ecf0f1;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                    text-align: left;
                }
                .error-id {
                    font-family: monospace;
                    background: #34495e;
                    color: white;
                    padding: 10px;
                    border-radius: 3px;
                    font-size: 14px;
                    word-break: break-all;
                }
                .suggestions {
                    text-align: left;
                    margin: 20px 0;
                }
                .suggestions h3 {
                    color: #2c3e50;
                    margin-bottom: 10px;
                }
                .suggestions ul {
                    list-style-type: none;
                    padding: 0;
                }
                .suggestions li {
                    background: #e8f5e8;
                    margin: 5px 0;
                    padding: 10px;
                    border-left: 4px solid #27ae60;
                    border-radius: 3px;
                }
                .debug-info {
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    text-align: left;
                }
                .stack-trace {
                    background: #2c3e50;
                    color: #ecf0f1;
                    padding: 15px;
                    border-radius: 5px;
                    font-family: monospace;
                    font-size: 12px;
                    overflow-x: auto;
                    white-space: pre-wrap;
                }
                .timestamp {
                    color: #95a5a6;
                    font-size: 14px;
                    margin-top: 20px;
                }
                .back-button {
                    display: inline-block;
                    background: #3498db;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                    transition: background-color 0.3s;
                }
                .back-button:hover {
                    background: #2980b9;
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-icon">⚠️</div>
                <h1 class="error-title">{{ title }}</h1>
                <p class="error-message">{{ message }}</p>

                <div class="error-details">
                    <strong>Error ID:</strong>
                    <div class="error-id">{{ error_id }}</div>
                    {% if trace_id %}
                    <br><strong>Trace ID:</strong>
                    <div class="error-id">{{ trace_id }}</div>
                    {% endif %}
                </div>

                {% if suggestions %}
                <div class="suggestions">
                    <h3>💡 Suggested Solutions:</h3>
                    <ul>
                        {% for suggestion in suggestions %}
                        <li>{{ suggestion }}</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endif %}

                {% if debug and stack_trace %}
                <div class="debug-info">
                    <h3>🐛 Debug Information:</h3>
                    <div class="stack-trace">{{ stack_trace }}</div>
                    {% if details %}
                    <h4>Additional Details:</h4>
                    <pre>{{ details }}</pre>
                    {% endif %}
                </div>
                {% endif %}

                <div class="timestamp">
                    Occurred at: {{ timestamp }}
                </div>

                <a href="/" class="back-button">← Back to Home</a>
            </div>
        </body>
        </html>
        """

    def _get_default_json_template(self) -> str:
        """Get default JSON error template."""
        return """
        {
            "error": {
                "id": "{{ error_id }}",
                "trace_id": "{{ trace_id }}",
                "message": "{{ message }}",
                "category": "{{ category }}",
                "severity": "{{ severity }}",
                "timestamp": "{{ timestamp }}",
                "suggestions": {{ suggestions }}
            }
        }
        """


def create_web_error_handler(app: Any, **kwargs) -> WebErrorHandler:
    """Factory function to create and configure web error handler."""
    return WebErrorHandler(app, **kwargs)


# Global error handler for middleware use
def setup_global_error_handling(app: Any, **kwargs) -> WebErrorHandler:
    """Setup global error handling for web application."""
    error_handler = WebErrorHandler(**kwargs)
    error_handler.init_app(app)
    return error_handler
