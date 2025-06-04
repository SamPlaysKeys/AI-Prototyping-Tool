"""FastAPI web application for AI Prototyping Tool."""

import asyncio
import json
import os
import sys
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from structured_logger import (
    get_logger,
    setup_web_logging,
    TraceManager,
    LogContext,
    generate_trace_id,
    set_trace_id,
)
from web_error_handler import setup_global_error_handling
from config_manager import get_config_manager
from error_handler import handle_error

# Initialize configuration and logging
config_manager = get_config_manager()
app_config = config_manager.get_config()

# Setup structured logging for web app
logger = setup_web_logging(debug=app_config.debug, json_logs=True)

# Create FastAPI app with configuration
app = FastAPI(
    title=app_config.version or "AI Prototyping Tool",
    description="Web interface for AI content generation",
    version=app_config.version,
    debug=app_config.debug,
)

# Setup global error handling
setup_global_error_handling(app, enable_debug=app_config.debug)

# Setup CORS if enabled
security_config = app_config.get_security_config()
if security_config.get("enable_cors", True):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=security_config.get("allowed_origins", ["*"]),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount static files (only if static directory exists)
static_dir = "static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Pydantic models
class GenerateRequest(BaseModel):
    prompt: str
    options: Optional[Dict[str, Any]] = {}


class GenerateResponse(BaseModel):
    id: str
    content: str
    status: str
    timestamp: datetime


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)


manager = ConnectionManager()

# LM Studio configuration from app config
LM_STUDIO_BASE_URL = app_config.lm_studio.base_url

# In-memory storage for demo purposes
generation_tasks = {}
current_lm_model = None


# LM Studio API functions
async def get_lm_studio_models():
    """Get available models from LM Studio."""
    try:
        timeout = app_config.lm_studio.connection_timeout
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{LM_STUDIO_BASE_URL}/v1/models",
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                return []
    except Exception as e:
        logger.error(f"Error fetching LM Studio models: {e}")
        return []


async def get_current_lm_model():
    """Get the currently loaded model in LM Studio."""
    models = await get_lm_studio_models()
    if models:
        # Return the first model as LM Studio typically loads one at a time
        return models[0].get("id", "Unknown Model")
    return None


async def check_lm_studio_status():
    """Check if LM Studio is running and accessible."""
    try:
        timeout = app_config.lm_studio.connection_timeout
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{LM_STUDIO_BASE_URL}/v1/models",
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as response:
                return response.status == 200
    except Exception:
        return False


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML frontend."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Prototyping Tool</title>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #555;
            }
            textarea, input, select {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                box-sizing: border-box;
            }
            textarea {
                height: 120px;
                resize: vertical;
            }
            button {
                background-color: #007bff;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #0056b3;
            }
            button:disabled {
                background-color: #ccc;
                cursor: not-allowed;
            }
            .results {
                margin-top: 30px;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 5px;
                border-left: 4px solid #007bff;
            }
            .status {
                margin-top: 20px;
                padding: 10px;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            .status.processing {
                background-color: #fff3cd;
                color: #856404;
                border: 1px solid #ffeeba;
            }
            .status.completed {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .status.error {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .options-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }
            .loading-spinner {
                display: none;
                width: 20px;
                height: 20px;
                border: 2px solid #f3f3f3;
                border-top: 2px solid #007bff;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI Prototyping Tool</h1>

            <!-- LM Studio Status Panel -->
            <div id="lmStudioStatus" class="status" style="margin-bottom: 20px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span id="statusText">Checking LM Studio...</span>
                    <button type="button" id="refreshStatus" onclick="checkLMStudioStatus()" style="padding: 5px 10px; font-size: 12px;">Refresh</button>
                </div>
                <div id="currentModel" style="margin-top: 10px; font-size: 14px; opacity: 0.8;"></div>
            </div>

            <form id="generateForm">
                <div class="form-group">
                    <label for="prompt">Prompt:</label>
                    <textarea id="prompt" name="prompt" placeholder="Enter your prompt here..." required></textarea>
                </div>

                <div class="options-grid">
                    <div class="form-group">
                        <label for="model">Model:</label>
                        <select id="model" name="model">
                            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                            <option value="gpt-4">GPT-4</option>
                            <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="max_tokens">Max Tokens:</label>
                        <input type="number" id="max_tokens" name="max_tokens" value="1000" min="1" max="4000">
                    </div>

                    <div class="form-group">
                        <label for="temperature">Temperature:</label>
                        <input type="number" id="temperature" name="temperature" value="0.7" min="0" max="2" step="0.1">
                    </div>

                    <div class="form-group">
                        <label for="format">Output Format:</label>
                        <select id="format" name="format">
                            <option value="markdown">Markdown</option>
                            <option value="text">Plain Text</option>
                            <option value="json">JSON</option>
                        </select>
                    </div>
                </div>

                <button type="submit" id="submitBtn">Generate Content</button>
            </form>

            <div id="status" class="status" style="display: none;"></div>
            <div class="loading-spinner" id="loadingSpinner"></div>

            <div id="results" class="results" style="display: none;">
                <h3>Generated Content:</h3>
                <div id="content"></div>
            </div>
        </div>

        <script>
            // WebSocket connection for live updates
            let ws = null;
            let currentTaskId = null;

            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

                ws.onopen = function(event) {
                    console.log('WebSocket connected');
                };

                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    updateStatus(data);
                };

                ws.onclose = function(event) {
                    console.log('WebSocket disconnected');
                    setTimeout(connectWebSocket, 3000); // Reconnect after 3 seconds
                };

                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                };
            }

            function updateStatus(data) {
                const statusDiv = document.getElementById('status');
                const loadingSpinner = document.getElementById('loadingSpinner');
                const resultsDiv = document.getElementById('results');
                const contentDiv = document.getElementById('content');

                if (data.task_id !== currentTaskId) {
                    return; // Ignore updates for other tasks
                }

                statusDiv.style.display = 'block';
                statusDiv.className = `status ${data.status}`;
                statusDiv.textContent = data.message;

                if (data.status === 'processing') {
                    loadingSpinner.style.display = 'block';
                } else {
                    loadingSpinner.style.display = 'none';
                }

                if (data.status === 'completed' && data.content) {
                    resultsDiv.style.display = 'block';

                    // Render content based on format
                    if (data.format === 'markdown') {
                        contentDiv.innerHTML = marked.parse(data.content);
                    } else {
                        contentDiv.innerHTML = `<pre>${escapeHtml(data.content)}</pre>`;
                    }
                }
            }

            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }

            // Form submission
            document.getElementById('generateForm').addEventListener('submit', async function(e) {
                e.preventDefault();

                const formData = new FormData(e.target);
                const prompt = formData.get('prompt');
                const options = {
                    model: formData.get('model'),
                    max_tokens: parseInt(formData.get('max_tokens')),
                    temperature: parseFloat(formData.get('temperature')),
                    format: formData.get('format')
                };

                try {
                    const submitBtn = document.getElementById('submitBtn');
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Generating...';

                    const response = await fetch('/generate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ prompt, options })
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const result = await response.json();
                    currentTaskId = result.id;

                } catch (error) {
                    console.error('Error:', error);
                    const statusDiv = document.getElementById('status');
                    statusDiv.style.display = 'block';
                    statusDiv.className = 'status error';
                    statusDiv.textContent = `Error: ${error.message}`;
                } finally {
                    const submitBtn = document.getElementById('submitBtn');
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Generate Content';
                }
            });

            // LM Studio status checking
            async function checkLMStudioStatus() {
                const statusText = document.getElementById('statusText');
                const currentModel = document.getElementById('currentModel');
                const lmStudioStatus = document.getElementById('lmStudioStatus');

                statusText.textContent = 'Checking LM Studio...';
                lmStudioStatus.className = 'status processing';

                try {
                    const response = await fetch('/lm-studio/status');
                    const data = await response.json();

                    if (data.status === 'connected') {
                        statusText.textContent = '🟢 LM Studio Connected';
                        lmStudioStatus.className = 'status completed';
                        currentModel.textContent = data.current_model ? `Model: ${data.current_model}` : 'No model loaded';

                        // Update model dropdown with LM Studio model
                        if (data.current_model) {
                            const modelSelect = document.getElementById('model');
                            modelSelect.innerHTML = `<option value="${data.current_model}">${data.current_model} (LM Studio)</option>`;
                        }
                    } else {
                        statusText.textContent = '🔴 LM Studio Disconnected';
                        lmStudioStatus.className = 'status error';
                        currentModel.textContent = 'Start LM Studio and load a model';

                        // Restore default model options
                        const modelSelect = document.getElementById('model');
                        modelSelect.innerHTML = `
                            <option value="mock-model">Mock Model (LM Studio not available)</option>
                        `;
                    }
                } catch (error) {
                    statusText.textContent = '🔴 Connection Error';
                    lmStudioStatus.className = 'status error';
                    currentModel.textContent = 'Error checking LM Studio status';
                    console.error('LM Studio status check failed:', error);
                }
            }

            // Initialize WebSocket connection
            connectWebSocket();

            // Check LM Studio status on load
            checkLMStudioStatus();

            // Auto-refresh LM Studio status every 30 seconds
            setInterval(checkLMStudioStatus, 30000);
        </script>
    </body>
    </html>
    """
    return html_content


@app.post("/generate", response_model=GenerateResponse)
async def generate_content(request_obj: Request, generate_request: GenerateRequest):
    """Generate content based on the provided prompt and options."""
    # Get or create trace ID
    trace_id = getattr(request_obj.state, "trace_id", generate_trace_id())

    with TraceManager(trace_id) as trace_mgr:
        task_id = str(uuid.uuid4())

        # Create log context
        log_context = LogContext(
            trace_id=trace_mgr.trace_id,
            operation="generate_content",
            component="web_api",
            metadata={
                "task_id": task_id,
                "prompt_length": len(generate_request.prompt),
                "options": generate_request.options,
            },
        )

        logger.info("Starting content generation request", context=log_context)

        try:
            # Store task info
            generation_tasks[task_id] = {
                "id": task_id,
                "prompt": generate_request.prompt,
                "options": generate_request.options,
                "status": "processing",
                "created_at": datetime.now(),
                "trace_id": trace_mgr.trace_id,
            }

            # Start background task
            asyncio.create_task(
                process_generation(
                    task_id,
                    generate_request.prompt,
                    generate_request.options,
                    trace_mgr.trace_id,
                )
            )

            logger.info("Generation task created successfully", context=log_context)

            return GenerateResponse(
                id=task_id, content="", status="processing", timestamp=datetime.now()
            )

        except Exception as e:
            error_info = handle_error(
                e,
                {"operation": "generate_content", "task_id": task_id},
                trace_mgr.trace_id,
            )
            logger.error(
                f"Failed to create generation task: {error_info.message}",
                context=log_context,
                exc_info=True,
            )
            raise HTTPException(
                status_code=500, detail=error_info.get_user_friendly_message()
            )


async def process_generation(
    task_id: str, prompt: str, options: Dict[str, Any], trace_id: Optional[str] = None
):
    """Background task to process content generation using LM Studio."""
    with TraceManager(trace_id) as trace_mgr:
        log_context = LogContext(
            trace_id=trace_mgr.trace_id,
            operation="process_generation",
            component="web_background",
            metadata={
                "task_id": task_id,
                "model": options.get("model"),
                "max_tokens": options.get("max_tokens"),
            },
        )

        logger.info("Starting background content generation", context=log_context)

        try:
            # Notify clients that processing has started
            await manager.broadcast(
                json.dumps(
                    {
                        "task_id": task_id,
                        "status": "processing",
                        "message": "Connecting to LM Studio...",
                        "format": options.get("format", "markdown"),
                        "trace_id": trace_mgr.trace_id,
                    }
                )
            )

            logger.debug("Notified clients of processing start", context=log_context)

            # Check if LM Studio is available
            logger.info("Checking LM Studio connection", context=log_context)
            is_connected = await check_lm_studio_status()

            if not is_connected:
                logger.warning(
                    "LM Studio not available, using mock generation",
                    context=log_context,
                )
                # Fall back to mock generation if LM Studio is not available
                await manager.broadcast(
                    json.dumps(
                        {
                            "task_id": task_id,
                            "status": "processing",
                            "message": "LM Studio not available, using mock generation...",
                            "format": options.get("format", "markdown"),
                            "trace_id": trace_mgr.trace_id,
                        }
                    )
                )

                await asyncio.sleep(2)  # Simulate processing time

                generated_content = f"""# Mock AI Response (LM Studio Unavailable)

**Trace ID:** {trace_mgr.trace_id}

**Prompt:** {prompt}

**Configuration:**
- Model: {options.get('model', 'unknown')}
- Temperature: {options.get('temperature', 0.7)}
- Max Tokens: {options.get('max_tokens', 1000)}
- Format: {options.get('format', 'markdown')}

## Generated Content

This is a mock response because LM Studio is not currently running or accessible.

### To use LM Studio:
1. Start LM Studio application
2. Load a model in LM Studio
3. Ensure the local server is running on port 1234
4. Refresh the connection status above

**Note:** Once LM Studio is connected, this will generate real AI responses using your local model.
"""
            else:
                # Use LM Studio for actual generation
                logger.info(
                    "Using LM Studio for content generation", context=log_context
                )
                await manager.broadcast(
                    json.dumps(
                        {
                            "task_id": task_id,
                            "status": "processing",
                            "message": "Generating content with LM Studio...",
                            "format": options.get("format", "markdown"),
                            "trace_id": trace_mgr.trace_id,
                        }
                    )
                )

                # Get current model
                current_model = await get_current_lm_model()
                logger.debug(
                    f"Using LM Studio model: {current_model}", context=log_context
                )

                # Prepare the request for LM Studio API
                payload = {
                    "model": current_model or "default",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": options.get("max_tokens", 1000),
                    "temperature": options.get("temperature", 0.7),
                    "stream": False,
                }

                logger.debug(
                    "Prepared LM Studio API request",
                    context=log_context,
                    payload=payload,
                )

                try:
                    # Log API call start
                    start_time = datetime.now()
                    logger.api_call(
                        "POST",
                        f"{LM_STUDIO_BASE_URL}/v1/chat/completions",
                        context=log_context,
                    )

                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"{LM_STUDIO_BASE_URL}/v1/chat/completions",
                            json=payload,
                            timeout=aiohttp.ClientTimeout(
                                total=120
                            ),  # 2 minute timeout
                        ) as response:
                            duration_ms = (
                                datetime.now() - start_time
                            ).total_seconds() * 1000

                            if response.status == 200:
                                result = await response.json()
                                generated_content = result["choices"][0]["message"][
                                    "content"
                                ]

                                # Log successful API call
                                logger.api_call(
                                    "POST",
                                    f"{LM_STUDIO_BASE_URL}/v1/chat/completions",
                                    status_code=200,
                                    duration_ms=duration_ms,
                                    context=log_context,
                                )

                                # Add metadata header
                                metadata = f"""# AI Generated Response

**Trace ID:** {trace_mgr.trace_id}
**Model:** {current_model}
**Temperature:** {options.get('temperature', 0.7)}
**Max Tokens:** {options.get('max_tokens', 1000)}

---

"""
                                generated_content = metadata + generated_content
                                logger.info(
                                    "Content generation completed successfully",
                                    context=log_context,
                                )
                            else:
                                error_text = await response.text()
                                logger.api_call(
                                    "POST",
                                    f"{LM_STUDIO_BASE_URL}/v1/chat/completions",
                                    status_code=response.status,
                                    duration_ms=duration_ms,
                                    context=log_context,
                                )
                                raise Exception(
                                    f"LM Studio API error {response.status}: {error_text}"
                                )

                except asyncio.TimeoutError:
                    logger.error("LM Studio request timed out", context=log_context)
                    raise Exception(
                        "LM Studio request timed out (2 minutes). The model might be too large or slow."
                    )
                except Exception as api_error:
                    logger.error(
                        f"LM Studio API error: {str(api_error)}",
                        context=log_context,
                        exc_info=True,
                    )
                    raise Exception(f"LM Studio API error: {str(api_error)}")

            # Update task status
            generation_tasks[task_id].update(
                {
                    "content": generated_content,
                    "status": "completed",
                    "completed_at": datetime.now(),
                }
            )

            # Notify clients of completion
            await manager.broadcast(
                json.dumps(
                    {
                        "task_id": task_id,
                        "status": "completed",
                        "message": "Content generation completed!",
                        "content": generated_content,
                        "format": options.get("format", "markdown"),
                        "trace_id": trace_mgr.trace_id,
                    }
                )
            )

            logger.info(
                "Background generation completed successfully", context=log_context
            )

        except Exception as e:
            # Handle errors with structured logging
            error_info = handle_error(
                e,
                {
                    "operation": "process_generation",
                    "task_id": task_id,
                    "prompt": prompt[:100],
                    "options": options,
                },
                trace_mgr.trace_id,
            )

            generation_tasks[task_id].update(
                {
                    "status": "error",
                    "error": str(e),
                    "error_id": error_info.error_id,
                    "completed_at": datetime.now(),
                }
            )

            await manager.broadcast(
                json.dumps(
                    {
                        "task_id": task_id,
                        "status": "error",
                        "message": error_info.get_user_friendly_message(),
                        "error_id": error_info.error_id,
                        "trace_id": trace_mgr.trace_id,
                        "format": options.get("format", "markdown"),
                    }
                )
            )

            logger.error(
                "Background generation failed", context=log_context, exc_info=True
            )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for live status updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str, request: Request):
    """Get the status of a specific generation task."""
    trace_id = getattr(request.state, "trace_id", generate_trace_id())

    log_context = LogContext(
        trace_id=trace_id,
        operation="get_task_status",
        component="web_api",
        metadata={"requested_task_id": task_id},
    )

    logger.debug(f"Task status requested for: {task_id}", context=log_context)

    if task_id not in generation_tasks:
        logger.warning(f"Task not found: {task_id}", context=log_context)
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

    task_data = generation_tasks[task_id].copy()
    task_data["trace_id"] = task_data.get("trace_id", trace_id)

    return task_data


@app.get("/lm-studio/status")
async def lm_studio_status(request: Request):
    """Check LM Studio connection status and current model."""
    trace_id = getattr(request.state, "trace_id", generate_trace_id())

    log_context = LogContext(
        trace_id=trace_id, operation="lm_studio_status", component="web_api"
    )

    logger.info("Checking LM Studio status", context=log_context)

    try:
        is_connected = await check_lm_studio_status()
        current_model = None

        if is_connected:
            current_model = await get_current_lm_model()
            logger.info(
                f"LM Studio connected with model: {current_model}", context=log_context
            )
        else:
            logger.warning("LM Studio not connected", context=log_context)

        return {
            "status": "connected" if is_connected else "disconnected",
            "current_model": current_model,
            "timestamp": datetime.now(),
            "trace_id": trace_id,
        }

    except Exception as e:
        error_info = handle_error(e, {"operation": "lm_studio_status"}, trace_id)
        logger.error(
            f"Failed to check LM Studio status: {error_info.message}",
            context=log_context,
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail=error_info.get_user_friendly_message()
        )


@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint."""
    trace_id = getattr(request.state, "trace_id", generate_trace_id())

    log_context = LogContext(
        trace_id=trace_id, operation="health_check", component="web_api"
    )

    logger.debug("Health check requested", context=log_context)

    # Get monitoring configuration
    monitoring_config = app_config.get_monitoring_config()

    health_data = {
        "status": "healthy",
        "timestamp": datetime.now(),
        "trace_id": trace_id,
        "version": app_config.version,
        "environment": app_config.environment,
    }

    # Add metrics if enabled
    if monitoring_config.get("enable_metrics", True):
        health_data["metrics"] = {
            "active_tasks": len(generation_tasks),
            "completed_tasks": len(
                [t for t in generation_tasks.values() if t.get("status") == "completed"]
            ),
            "failed_tasks": len(
                [t for t in generation_tasks.values() if t.get("status") == "error"]
            ),
        }

    return health_data


# Add metrics endpoint if enabled
monitoring_config = app_config.get_monitoring_config()
if monitoring_config.get("enable_metrics", True):

    @app.get(monitoring_config.get("metrics_endpoint", "/metrics"))
    async def metrics(request: Request):
        """Metrics endpoint for monitoring."""
        trace_id = getattr(request.state, "trace_id", generate_trace_id())

        return {
            "timestamp": datetime.now(),
            "trace_id": trace_id,
            "tasks": {
                "total": len(generation_tasks),
                "processing": len(
                    [
                        t
                        for t in generation_tasks.values()
                        if t.get("status") == "processing"
                    ]
                ),
                "completed": len(
                    [
                        t
                        for t in generation_tasks.values()
                        if t.get("status") == "completed"
                    ]
                ),
                "failed": len(
                    [t for t in generation_tasks.values() if t.get("status") == "error"]
                ),
            },
            "websocket_connections": len(manager.active_connections),
        }


if __name__ == "__main__":
    # Get server configuration
    server_config = app_config.get_server_config()

    logger.info(
        f"Starting web server on {server_config['host']}:{server_config['port']}"
    )

    uvicorn.run(
        app,
        host=server_config.get("host", "0.0.0.0"),
        port=server_config.get("port", 8000),
        reload=server_config.get("reload", True),
        workers=server_config.get("workers", 1),
    )
