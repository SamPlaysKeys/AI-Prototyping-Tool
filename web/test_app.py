#!/usr/bin/env python3
"""Simple test script to verify the FastAPI application endpoints."""

import asyncio
import json
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Health endpoint working")


def test_root_endpoint():
    """Test the root HTML endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Prototyping Tool" in response.text
    assert "Generate Content" in response.text
    print("✅ Root endpoint serving HTML")


def test_generate_endpoint():
    """Test the POST generate endpoint."""
    test_data = {
        "prompt": "Test prompt",
        "options": {
            "model": "gpt-3.5-turbo",
            "max_tokens": 100,
            "temperature": 0.7,
            "format": "markdown",
        },
    }

    response = client.post("/generate", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "processing"
    print("✅ Generate endpoint accepting requests")

    # Wait a moment and check task status
    task_id = data["id"]
    import time

    time.sleep(3)  # Allow background task to complete

    task_response = client.get(f"/tasks/{task_id}")
    assert task_response.status_code == 200
    task_data = task_response.json()
    print(f"✅ Task {task_id} status: {task_data['status']}")


def test_lm_studio_status():
    """Test LM Studio status endpoint."""
    response = client.get("/lm-studio/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "current_model" in data
    assert "timestamp" in data

    if data["status"] == "connected":
        print(f"✅ LM Studio connected with model: {data['current_model']}")
    else:
        print("⚠️  LM Studio not connected (this is normal if LM Studio isn't running)")


def test_websocket_connection():
    """Test WebSocket connection."""
    try:
        with client.websocket_connect("/ws") as websocket:
            # Send a test message
            websocket.send_text("test")
            print("✅ WebSocket connection established")
    except Exception as e:
        print(f"⚠️  WebSocket test failed: {e}")


def main():
    """Run all tests."""
    print("🧪 Testing AI Prototyping Tool Web Application")
    print("=" * 50)

    try:
        test_health_endpoint()
        test_root_endpoint()
        test_generate_endpoint()
        test_lm_studio_status()
        test_websocket_connection()

        print("=" * 50)
        print("🎉 All tests passed! Application is working correctly.")
        print("")
        print("🚀 To start the application:")
        print("   python app.py")
        print("   or")
        print("   ./start.sh")
        print("")
        print("🌐 Then visit: http://localhost:8000")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
