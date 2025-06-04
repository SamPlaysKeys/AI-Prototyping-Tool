"""Mock LM Studio API server for testing and development.

This service mimics the LM Studio OpenAI-compatible API to allow
development and testing without requiring a full LM Studio installation.
"""

import json
import time
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# FastAPI app
app = FastAPI(
    title="LM Studio Mock API",
    description="Mock implementation of LM Studio's OpenAI-compatible API",
    version="1.0.0",
)

# Mock models
MOCK_MODELS = [
    {
        "id": "llama-2-7b-chat",
        "object": "model",
        "created": int(time.time()),
        "owned_by": "mock-lmstudio",
        "permission": [],
        "root": "llama-2-7b-chat",
        "parent": None,
    },
    {
        "id": "codellama-7b-instruct",
        "object": "model",
        "created": int(time.time()),
        "owned_by": "mock-lmstudio",
        "permission": [],
        "root": "codellama-7b-instruct",
        "parent": None,
    },
    {
        "id": "mistral-7b-instruct",
        "object": "model",
        "created": int(time.time()),
        "owned_by": "mock-lmstudio",
        "permission": [],
        "root": "mistral-7b-instruct",
        "parent": None,
    },
]


# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    stop: Optional[List[str]] = None
    stream: Optional[bool] = False


class CompletionRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    stop: Optional[List[str]] = None
    stream: Optional[bool] = False


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Choice(BaseModel):
    index: int
    text: Optional[str] = None
    message: Optional[ChatMessage] = None
    finish_reason: str


class CompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Usage


# Mock response generators
def generate_mock_response(prompt: str, model: str, is_chat: bool = False) -> str:
    """Generate a mock AI response based on the prompt."""

    # Simple response patterns based on prompt keywords
    prompt_lower = prompt.lower()

    if "code" in prompt_lower or "python" in prompt_lower or "function" in prompt_lower:
        return '''Here's a simple Python function example:

```python
def greet(name):
    """A simple greeting function."""
    return f"Hello, {name}! Welcome to the AI Prototyping Tool."

# Usage example
result = greet("Developer")
print(result)
```

This function demonstrates basic Python syntax and can be easily extended for more complex use cases.'''

    elif "poem" in prompt_lower or "poetry" in prompt_lower:
        return """Here's a short poem about AI:

Silicon dreams and circuits bright,
Processing data day and night.
Algorithms learn and grow,
Helping humans as they go.

Artificial minds create,
Innovation at rapid rate.
Technology's gentle hand,
Guiding us to understand."""

    elif "story" in prompt_lower or "tale" in prompt_lower:
        return """Once upon a time, in a world where artificial intelligence and humans worked hand in hand, there was a young developer who discovered the power of prototyping. With each iteration, their ideas became clearer, their code more elegant, and their understanding deeper. The AI tools served as faithful companions, helping to transform abstract thoughts into concrete reality."""

    elif "explain" in prompt_lower or "what is" in prompt_lower:
        return f"""Based on your question, I can provide some insights.

This is a mock response from the LM Studio simulation service. In a real scenario, a large language model would analyze your prompt and generate a contextually appropriate response based on its training data.

Key points:
- This is running in {model} simulation mode
- Real LM Studio would use actual AI models
- The response quality depends on the model used
- This mock service helps with development and testing

For production use, connect to actual LM Studio with a loaded model."""

    else:
        return f"""Thank you for your message! This is a mock response from the {model} model simulation.

I understand you're asking about: "{prompt[:100]}{'...' if len(prompt) > 100 else ''}"

In a real LM Studio environment, I would provide a more detailed and contextually appropriate response based on the specific model's capabilities. This mock service is designed to help with development and testing of the AI Prototyping Tool.

To get actual AI responses, please:
1. Install and run LM Studio
2. Load a compatible language model
3. Ensure the API server is running on port 1234
4. Update your configuration to point to the real LM Studio instance"""


# API Endpoints
@app.get("/v1/models")
async def list_models():
    """List available models."""
    return {"object": "list", "data": MOCK_MODELS}


@app.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    """Create a chat completion."""

    # Validate model
    if request.model not in [model["id"] for model in MOCK_MODELS]:
        raise HTTPException(status_code=400, detail=f"Model {request.model} not found")

    # Extract prompt from messages
    prompt = ""
    for message in request.messages:
        if message.role == "user":
            prompt += message.content + " "

    # Generate mock response
    response_text = generate_mock_response(prompt.strip(), request.model, is_chat=True)

    # Simulate processing time
    time.sleep(0.5)

    # Calculate token usage (mock)
    prompt_tokens = len(prompt.split()) * 1.3  # Rough estimation
    completion_tokens = len(response_text.split()) * 1.3

    return CompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
        object="chat.completion",
        created=int(time.time()),
        model=request.model,
        choices=[
            Choice(
                index=0,
                message=ChatMessage(role="assistant", content=response_text),
                finish_reason="stop",
            )
        ],
        usage=Usage(
            prompt_tokens=int(prompt_tokens),
            completion_tokens=int(completion_tokens),
            total_tokens=int(prompt_tokens + completion_tokens),
        ),
    )


@app.post("/v1/completions")
async def create_completion(request: CompletionRequest):
    """Create a text completion."""

    # Validate model
    if request.model not in [model["id"] for model in MOCK_MODELS]:
        raise HTTPException(status_code=400, detail=f"Model {request.model} not found")

    # Generate mock response
    response_text = generate_mock_response(request.prompt, request.model, is_chat=False)

    # Simulate processing time
    time.sleep(0.5)

    # Calculate token usage (mock)
    prompt_tokens = len(request.prompt.split()) * 1.3
    completion_tokens = len(response_text.split()) * 1.3

    return CompletionResponse(
        id=f"cmpl-{uuid.uuid4().hex[:8]}",
        object="text_completion",
        created=int(time.time()),
        model=request.model,
        choices=[Choice(index=0, text=response_text, finish_reason="stop")],
        usage=Usage(
            prompt_tokens=int(prompt_tokens),
            completion_tokens=int(completion_tokens),
            total_tokens=int(prompt_tokens + completion_tokens),
        ),
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "lmstudio-mock",
        "timestamp": datetime.now().isoformat(),
        "models_available": len(MOCK_MODELS),
    }


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "LM Studio Mock API",
        "version": "1.0.0",
        "description": "Mock implementation for development and testing",
        "endpoints": {
            "models": "/v1/models",
            "chat_completions": "/v1/chat/completions",
            "completions": "/v1/completions",
            "health": "/health",
        },
        "available_models": [model["id"] for model in MOCK_MODELS],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=1234)
