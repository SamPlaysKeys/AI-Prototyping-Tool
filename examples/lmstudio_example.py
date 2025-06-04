#!/usr/bin/env python3
"""Example usage of the LM Studio API client.

This script demonstrates how to use the LMStudioClient to interact with
LM Studio's OpenAI-compatible API running locally.

Before running this script, make sure:
1. LM Studio is running locally on port 1234
2. A model is loaded in LM Studio
3. The server is accessible at http://localhost:1234
"""

import sys
import os

# Add the src directory to Python path so we can import our client
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from lmstudio_client import (
    LMStudioClient,
    LMStudioError,
    CompletionRequest,
    RetryConfig,
    create_client,
    list_models,
    complete,
)


def main():
    """Main example function."""
    print("LM Studio API Client Example")
    print("============================\n")

    # Example 1: Health check
    print("1. Health Check")
    print("-" * 15)
    try:
        with LMStudioClient() as client:
            health = client.health_check()
            print(f"Status: {health['status']}")
            if health["status"] == "healthy":
                print(f"Available models: {health['models_count']}")
            else:
                print(f"Error: {health.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Health check failed: {e}")

    print("\n")

    # Example 2: List models using convenience function
    print("2. List Available Models")
    print("-" * 24)
    try:
        models = list_models()
        if models:
            for i, model in enumerate(models, 1):
                print(f"{i}. {model.id}")
                if model.owned_by:
                    print(f"   Owned by: {model.owned_by}")
        else:
            print("No models available")
    except LMStudioError as e:
        print(f"Failed to list models: {e}")
        return

    print("\n")

    # Example 3: Simple completion using convenience function
    print("3. Simple Completion (Convenience Function)")
    print("-" * 40)
    if models:
        model_id = models[0].id
        prompt = "Hello, how are you?"

        try:
            response = complete(
                model=model_id, prompt=prompt, max_tokens=50, temperature=0.7
            )

            print(f"Prompt: {prompt}")
            print(f"Model: {response.model}")
            print(f"Response: {response.choices[0].text.strip()}")

            if response.usage:
                print(
                    f"Tokens used: {response.usage.total_tokens} "
                    f"(prompt: {response.usage.prompt_tokens}, "
                    f"completion: {response.usage.completion_tokens})"
                )

        except LMStudioError as e:
            print(f"Completion failed: {e}")

    print("\n")

    # Example 4: Advanced completion with custom client
    print("4. Advanced Completion with Custom Configuration")
    print("-" * 49)
    if models:
        # Create client with custom retry configuration
        retry_config = RetryConfig(max_retries=2, backoff_factor=0.5, max_backoff=30.0)

        try:
            with LMStudioClient(
                base_url="http://localhost:1234/v1",
                timeout=60.0,
                retry_config=retry_config,
            ) as client:

                # Create a detailed completion request
                request = CompletionRequest(
                    model=models[0].id,
                    prompt="Write a short poem about artificial intelligence:",
                    max_tokens=100,
                    temperature=0.8,
                    top_p=0.9,
                    frequency_penalty=0.1,
                    presence_penalty=0.1,
                    stop=["\n\n", "---"],
                )

                response = client.create_completion(request)

                print(f"Prompt: {request.prompt}")
                print(f"Model: {response.model}")
                print(f"Response ID: {response.id}")
                print(f"Generated text:\n{response.choices[0].text.strip()}")
                print(f"Finish reason: {response.choices[0].finish_reason}")

                if response.usage:
                    print(f"\nToken usage:")
                    print(f"  Prompt tokens: {response.usage.prompt_tokens}")
                    print(f"  Completion tokens: {response.usage.completion_tokens}")
                    print(f"  Total tokens: {response.usage.total_tokens}")

        except LMStudioError as e:
            print(f"Advanced completion failed: {e}")
            print(f"Error type: {e.error_type.value}")
            if e.status_code:
                print(f"HTTP status: {e.status_code}")

    print("\n")

    # Example 5: Error handling demonstration
    print("5. Error Handling Demonstration")
    print("-" * 32)

    # Try to connect to a non-existent server
    try:
        with LMStudioClient(base_url="http://localhost:9999/v1") as client:
            client.list_models()
    except LMStudioError as e:
        print(f"Expected error caught: {e.error_type.value}")
        print(f"Message: {e.message}")

    # Try an invalid completion request
    if models:
        try:
            with LMStudioClient() as client:
                request = CompletionRequest(
                    model="non-existent-model", prompt="Hello", max_tokens=10
                )
                client.create_completion(request)
        except LMStudioError as e:
            print(f"Expected model error: {e.error_type.value}")
            print(f"Message: {e.message}")

    print("\nExample completed!")


if __name__ == "__main__":
    main()
