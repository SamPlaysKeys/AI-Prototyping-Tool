#!/usr/bin/env python3
"""
Example Usage of Template and Schema System

This script demonstrates how to use the prompt schema and template rendering system
to generate deliverable documents from raw user input.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prompt_schema import DeliverableType, PromptSchemaProcessor, create_empty_schema
from template_renderer import (
    TemplateRenderer,
    render_deliverable_from_input,
    create_deliverable_package,
)


def example_basic_usage():
    """Demonstrate basic template rendering."""
    print("=== Basic Template Rendering Example ===")

    # Sample user input
    user_input = """
    Project Name: AI-Powered Customer Support System
    Problem: Our customer support team is overwhelmed with repetitive inquiries
    Current State: Manual ticket handling, 24-hour response time average
    Stakeholders: Customer service team, IT department, customers
    Goal: Reduce response time to under 2 hours and improve customer satisfaction
    Industry: E-commerce retail
    Organization Size: 500+ employees
    """

    try:
        # Render problem statement
        rendered_content = render_deliverable_from_input(
            DeliverableType.PROBLEM_STATEMENT, user_input
        )

        print("Generated Problem Statement:")
        print("-" * 50)
        print(
            rendered_content[:500] + "..."
            if len(rendered_content) > 500
            else rendered_content
        )
        print("-" * 50)

    except Exception as e:
        print(f"Error: {e}")


def example_schema_processing():
    """Demonstrate schema processing and validation."""
    print("\n=== Schema Processing Example ===")

    processor = PromptSchemaProcessor()

    user_input = """
    Tool Name: Project Management Dashboard
    Tool Category: Web Application
    Primary Users: Project managers, team leads, developers
    Core Features: Task tracking, time management, reporting
    Technology Stack: React frontend, Node.js backend, PostgreSQL database
    """

    # Parse user input
    parsed_data = processor.parse_user_input(user_input)
    print(f"Extracted fields: {list(parsed_data['extracted_fields'].keys())}")
    print(f"Inferred deliverable type: {parsed_data['inferred_deliverable_type']}")
    print(f"Confidence score: {parsed_data['confidence_score']:.2f}")

    # Create and validate schema
    if parsed_data["inferred_deliverable_type"]:
        schema = processor.create_schema(
            parsed_data["inferred_deliverable_type"], parsed_data
        )

        validation = processor.validate_schema(schema)
        print(f"Schema completeness: {validation['completeness_score']:.2f}")
        print(f"Warnings: {validation['warnings']}")


def example_template_validation():
    """Demonstrate template validation and introspection."""
    print("\n=== Template Validation Example ===")

    renderer = TemplateRenderer()

    # Check available templates
    available = renderer.get_available_templates()
    print(f"Available templates: {len(available)}")

    # Validate each template
    for deliverable_type in DeliverableType:
        validation = renderer.validate_template(deliverable_type)
        status = "✓" if validation["is_valid"] else "✗"
        print(f"{status} {deliverable_type.value}: {validation.get('error', 'OK')}")

    # Preview variables for personas template
    variables = renderer.preview_template_variables(DeliverableType.PERSONAS)
    if "variables" in variables:
        print(f"\nPersonas template has {variables['total_variables']} variables")
        # Show first few variables
        for i, (name, info) in enumerate(list(variables["variables"].items())[:5]):
            print(
                f"  {name}: {info['type']} {'(required)' if info['is_required'] else ''}"
            )


def example_multiple_deliverables():
    """Demonstrate generating multiple deliverables."""
    print("\n=== Multiple Deliverables Example ===")

    user_input = """
    Project: Mobile Fitness Tracking App
    Problem: Users struggle to maintain consistent workout routines
    Target Users: Fitness enthusiasts, casual gym-goers, personal trainers
    Key Features: Workout tracking, progress analytics, social sharing
    Platform: iOS and Android mobile app
    Goal: Increase user workout frequency by 40%
    """

    # Create output directory
    output_dir = "./example_output"

    # Generate selected deliverables
    selected_deliverables = [
        DeliverableType.PROBLEM_STATEMENT,
        DeliverableType.PERSONAS,
        DeliverableType.TOOL_OUTLINE,
    ]

    try:
        results = create_deliverable_package(
            user_input=user_input,
            output_dir=output_dir,
            selected_deliverables=selected_deliverables,
        )

        print(f"Output directory: {results['output_directory']}")
        print(f"Successfully generated: {len(results['generated'])} deliverables")
        for item in results["generated"]:
            print(f"  - {item['type']}: {item['filename']}")

        if results["failed"]:
            print(f"Failed to generate: {len(results['failed'])} deliverables")
            for item in results["failed"]:
                print(f"  - {item['type']}: {item['error']}")

    except Exception as e:
        print(f"Error generating deliverables: {e}")


def example_custom_schema_population():
    """Demonstrate manual schema population and rendering."""
    print("\n=== Custom Schema Population Example ===")

    # Create empty schema
    schema = create_empty_schema(DeliverableType.USE_CASES)

    # Manually populate schema
    schema.project_name = "Online Learning Platform"
    schema.use_cases_overview = "Core user interactions for the learning platform"

    # Add sample use case data
    from prompt_schema import UseCaseData, AlternativeFlow

    use_case = UseCaseData(
        id="UC001",
        title="Student Login",
        priority="High",
        complexity="Low",
        category="Authentication",
        status="Completed",
        primary_actors="Student",
        description="Student logs into the platform to access courses",
        preconditions="Student has valid account credentials",
        main_scenario=[
            "Student navigates to login page",
            "Student enters username and password",
            "System validates credentials",
            "Student is redirected to dashboard",
        ],
        acceptance_criteria=[
            "Login completes within 3 seconds",
            "Invalid credentials show appropriate error message",
            "Account lockout after 5 failed attempts",
        ],
    )

    schema.use_cases = [use_case]

    # Render template
    renderer = TemplateRenderer()
    try:
        rendered_content = renderer.render_deliverable(
            DeliverableType.USE_CASES, schema
        )

        print("Generated Use Cases Document (first 600 chars):")
        print("-" * 50)
        print(rendered_content[:600] + "...")
        print("-" * 50)

    except Exception as e:
        print(f"Error rendering template: {e}")


def main():
    """Run all examples."""
    print("Deliverable Template System Examples")
    print("====================================")

    try:
        example_basic_usage()
        example_schema_processing()
        example_template_validation()
        example_multiple_deliverables()
        example_custom_schema_population()

        print("\n=== All examples completed successfully! ===")

    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running from the project root directory")
        print("and that all dependencies are installed.")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
