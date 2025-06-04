#!/usr/bin/env python3
"""
Orchestrator Example

This example demonstrates how to use the OrchestrationEngine to generate
multiple deliverables from user input.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.orchestrator import (
    OrchestrationEngine,
    OrchestrationConfig,
    CompletionMode,
    quick_generate,
)
from src.prompt_schema import DeliverableType


def basic_orchestration_example():
    """Basic example of orchestrating multiple deliverables."""
    print("=== Basic Orchestration Example ===")

    # Define user input
    user_input = """
    I need to develop a customer relationship management (CRM) tool for small businesses.
    The tool should help them track leads, manage customer interactions, and generate reports.
    It should be web-based, easy to use, and integrate with email systems.
    """

    # Define which deliverables to generate
    deliverable_types = [
        DeliverableType.PROBLEM_STATEMENT,
        DeliverableType.PERSONAS,
        DeliverableType.USE_CASES,
        DeliverableType.TOOL_OUTLINE,
    ]

    # Create configuration
    config = OrchestrationConfig(
        completion_mode=CompletionMode.SEQUENTIAL,
        max_tokens=1500,
        temperature=0.7,
        merge_into_single_document=True,
        include_table_of_contents=True,
    )

    try:
        # Create and use orchestrator
        with OrchestrationEngine(config) as engine:
            print("Initializing orchestration engine...")

            if not engine.initialize():
                print("Failed to initialize orchestration engine")
                return

            print(f"Available models: {engine.get_available_models()}")

            print(
                f"\nStarting orchestration for {len(deliverable_types)} deliverables..."
            )
            result = engine.orchestrate(user_input, deliverable_types)

            # Print results
            print(f"\n=== Orchestration Results ===")
            print(f"Total execution time: {result.total_execution_time:.2f} seconds")
            print(f"Successful deliverables: {result.success_count}")
            print(f"Failed deliverables: {result.error_count}")
            print(f"Total tokens used: {result.total_tokens_used}")

            # Print individual results
            print("\n=== Individual Results ===")
            for deliverable_result in result.deliverable_results:
                status = "✓" if deliverable_result.success else "✗"
                print(
                    f"{status} {deliverable_result.deliverable_type.value}: {deliverable_result.execution_time:.2f}s"
                )
                if not deliverable_result.success:
                    print(f"   Error: {deliverable_result.error_message}")

            # Save merged document if available
            if result.merged_document:
                output_path = "output/orchestrator_example_output.md"
                os.makedirs("output", exist_ok=True)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(result.merged_document)

                print(f"\nMerged document saved to: {output_path}")
                print(f"Document length: {len(result.merged_document)} characters")

    except Exception as e:
        print(f"Error during orchestration: {e}")
        import traceback

        traceback.print_exc()


def quick_generate_example():
    """Example using the quick_generate convenience function."""
    print("\n\n=== Quick Generate Example ===")

    user_input = """
    Create a mobile app for fitness tracking that includes workout logging,
    progress tracking, and social features.
    """

    deliverable_types = [DeliverableType.PROBLEM_STATEMENT, DeliverableType.PERSONAS]

    try:
        print("Using quick_generate function...")
        result = quick_generate(
            user_input=user_input,
            deliverable_types=deliverable_types,
            max_tokens=1000,
            temperature=0.6,
        )

        print(f"\nQuick generation completed:")
        print(f"Success: {result.success_count}/{len(deliverable_types)}")
        print(f"Time: {result.total_execution_time:.2f}s")

        if result.merged_document:
            print(f"\nFirst 200 characters of output:")
            print(result.merged_document[:200] + "...")

    except Exception as e:
        print(f"Error in quick generation: {e}")


def config_examples():
    """Examples of different configuration options."""
    print("\n\n=== Configuration Examples ===")

    # Example 1: Batch mode configuration
    batch_config = OrchestrationConfig(
        completion_mode=CompletionMode.BATCH,
        max_tokens=2048,
        temperature=0.5,
        merge_into_single_document=False,
        enable_logging=True,
        log_level="DEBUG",
    )
    print(f"Batch config: {batch_config}")

    # Example 2: Streaming mode configuration
    streaming_config = OrchestrationConfig(
        completion_mode=CompletionMode.STREAMING,
        max_tokens=1024,
        temperature=0.8,
        max_retries_per_deliverable=5,
        request_timeout=120.0,
    )
    print(f"Streaming config: {streaming_config}")

    # Example 3: Custom model configuration
    custom_config = OrchestrationConfig(
        model_name="custom-model",
        lm_studio_base_url="http://custom-server:1234/v1",
        completion_mode=CompletionMode.SEQUENTIAL,
    )
    print(f"Custom config: {custom_config}")


def validation_example():
    """Example of validating the orchestration setup."""
    print("\n\n=== Validation Example ===")

    try:
        engine = OrchestrationEngine()

        print("Validating deliverable templates...")
        validation_results = engine.validate_deliverable_templates()

        for deliverable_type, result in validation_results.items():
            status = "✓" if result["is_valid"] else "✗"
            print(f"{status} {deliverable_type}: {result}")

        print("\nTrying to initialize...")
        if engine.initialize():
            print("✓ Engine initialization successful")
            print(f"Available models: {engine.get_available_models()}")
        else:
            print("✗ Engine initialization failed")

        engine.close()

    except Exception as e:
        print(f"Validation error: {e}")


if __name__ == "__main__":
    print("Orchestrator Example Script")
    print("===========================")

    # Run validation first
    validation_example()

    # Show configuration examples
    config_examples()

    # Try basic orchestration (requires LM Studio to be running)
    try:
        basic_orchestration_example()
    except Exception as e:
        print(f"\nSkipping basic orchestration (LM Studio not available): {e}")

    # Try quick generate (requires LM Studio to be running)
    try:
        quick_generate_example()
    except Exception as e:
        print(f"\nSkipping quick generate (LM Studio not available): {e}")

    print("\n=== Example Complete ===")
