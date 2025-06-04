"""
Template Renderer Module

This module provides functionality to render Markdown templates using the schema data.
It integrates Jinja2 templating with the prompt schema system to generate deliverable documents.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template
from prompt_schema import (
    DeliverableType,
    BaseSchema,
    PromptSchemaProcessor,
    get_schema_for_deliverable,
    create_empty_schema,
)


class TemplateRenderer:
    """Main class for rendering deliverable templates using schema data."""

    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize the template renderer.

        Args:
            template_dir: Directory containing template files.
                         Defaults to templates/deliverables/
        """
        if template_dir is None:
            # Get the project root directory
            current_dir = Path(__file__).parent.parent
            self.template_dir = current_dir / "templates" / "deliverables"
        else:
            self.template_dir = Path(template_dir)

        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,  # We're generating Markdown, not HTML
        )

        # Map deliverable types to template files
        self.template_map = {
            DeliverableType.PROBLEM_STATEMENT: "problem_statement.md",
            DeliverableType.PERSONAS: "personas.md",
            DeliverableType.USE_CASES: "use_cases.md",
            DeliverableType.TOOL_OUTLINE: "tool_outline.md",
            DeliverableType.IMPLEMENTATION_INSTRUCTIONS: "implementation_instructions.md",
            DeliverableType.COPILOT365_PRESENTATION_PROMPT: "copilot365_presentation_prompt.md",
            DeliverableType.EFFECTIVENESS_ASSESSMENT: "effectiveness_assessment.md",
        }

        self.schema_processor = PromptSchemaProcessor()

    def render_deliverable(
        self, deliverable_type: DeliverableType, schema_data: BaseSchema
    ) -> str:
        """
        Render a deliverable template using schema data.

        Args:
            deliverable_type: Type of deliverable to render
            schema_data: Schema instance containing the data

        Returns:
            Rendered Markdown content
        """
        template_file = self.template_map.get(deliverable_type)
        if not template_file:
            raise ValueError(
                f"No template found for deliverable type: {deliverable_type}"
            )

        try:
            template = self.jinja_env.get_template(template_file)
        except Exception as e:
            raise FileNotFoundError(
                f"Template file not found: {template_file}. Error: {e}"
            )

        # Convert schema to dictionary for template rendering
        template_data = schema_data.to_dict()

        # Render the template
        try:
            rendered_content = template.render(**template_data)
            return rendered_content
        except Exception as e:
            raise RuntimeError(f"Error rendering template: {e}")

    def render_from_user_input(
        self, deliverable_type: DeliverableType, user_input: str
    ) -> str:
        """
        Parse user input and render the corresponding deliverable template.

        Args:
            deliverable_type: Type of deliverable to generate
            user_input: Raw user input to parse

        Returns:
            Rendered Markdown content
        """
        # Parse user input and create schema
        parsed_data = self.schema_processor.parse_user_input(user_input)
        schema = self.schema_processor.create_schema(deliverable_type, parsed_data)

        # Render the template
        return self.render_deliverable(deliverable_type, schema)

    def render_from_json_payload(
        self, deliverable_type: DeliverableType, json_payload: Dict[str, Any]
    ) -> str:
        """
        Render a deliverable template from a JSON payload.

        Args:
            deliverable_type: Type of deliverable to render
            json_payload: JSON payload containing the data

        Returns:
            Rendered Markdown content
        """
        # Create schema instance and populate with payload data
        schema = create_empty_schema(deliverable_type)

        # Populate schema with JSON data
        for key, value in json_payload.items():
            if hasattr(schema, key) and not key.startswith("_"):
                setattr(schema, key, value)

        # Render the template
        return self.render_deliverable(deliverable_type, schema)

    def save_rendered_deliverable(
        self,
        deliverable_type: DeliverableType,
        schema_data: BaseSchema,
        output_path: str,
    ) -> None:
        """
        Render and save a deliverable to a file.

        Args:
            deliverable_type: Type of deliverable to render
            schema_data: Schema instance containing the data
            output_path: Path where to save the rendered file
        """
        rendered_content = self.render_deliverable(deliverable_type, schema_data)

        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_content)

    def get_available_templates(self) -> Dict[str, str]:
        """
        Get a list of available templates.

        Returns:
            Dictionary mapping deliverable types to template file paths
        """
        available = {}
        for deliverable_type, template_file in self.template_map.items():
            template_path = self.template_dir / template_file
            if template_path.exists():
                available[deliverable_type.value] = str(template_path)
        return available

    def validate_template(self, deliverable_type: DeliverableType) -> Dict[str, Any]:
        """
        Validate that a template exists and can be loaded.

        Args:
            deliverable_type: Type of deliverable to validate

        Returns:
            Validation results
        """
        validation_result = {
            "is_valid": False,
            "exists": False,
            "can_load": False,
            "error": None,
        }

        template_file = self.template_map.get(deliverable_type)
        if not template_file:
            validation_result["error"] = (
                f"No template mapping found for {deliverable_type}"
            )
            return validation_result

        template_path = self.template_dir / template_file
        validation_result["exists"] = template_path.exists()

        if validation_result["exists"]:
            try:
                template = self.jinja_env.get_template(template_file)
                validation_result["can_load"] = True
                validation_result["is_valid"] = True
            except Exception as e:
                validation_result["error"] = str(e)
        else:
            validation_result["error"] = (
                f"Template file does not exist: {template_path}"
            )

        return validation_result

    def preview_template_variables(
        self, deliverable_type: DeliverableType
    ) -> Dict[str, Any]:
        """
        Get a preview of template variables for a deliverable type.

        Args:
            deliverable_type: Type of deliverable

        Returns:
            Dictionary containing variable information
        """
        schema_class = get_schema_for_deliverable(deliverable_type)
        if not schema_class:
            return {"error": f"No schema found for {deliverable_type}"}

        # Create empty schema instance to get all fields
        schema_instance = schema_class()
        schema_dict = schema_instance.to_dict()

        # Extract variable information
        variables = {}
        for field_name, field_value in schema_dict.items():
            field_type = type(field_value).__name__
            variables[field_name] = {
                "type": field_type,
                "default_value": field_value,
                "is_list": isinstance(field_value, list),
                "is_required": field_name in ["project_name", "timestamp"],
            }

        return {
            "deliverable_type": deliverable_type.value,
            "total_variables": len(variables),
            "variables": variables,
        }


def render_deliverable_from_input(
    deliverable_type: DeliverableType,
    user_input: str,
    template_dir: Optional[str] = None,
) -> str:
    """
    Convenience function to render a deliverable from user input.

    Args:
        deliverable_type: Type of deliverable to generate
        user_input: Raw user input to parse
        template_dir: Optional custom template directory

    Returns:
        Rendered Markdown content
    """
    renderer = TemplateRenderer(template_dir)
    return renderer.render_from_user_input(deliverable_type, user_input)


def render_deliverable_from_json(
    deliverable_type: DeliverableType,
    json_payload: Dict[str, Any],
    template_dir: Optional[str] = None,
) -> str:
    """
    Convenience function to render a deliverable from JSON payload.

    Args:
        deliverable_type: Type of deliverable to generate
        json_payload: JSON payload containing the data
        template_dir: Optional custom template directory

    Returns:
        Rendered Markdown content
    """
    renderer = TemplateRenderer(template_dir)
    return renderer.render_from_json_payload(deliverable_type, json_payload)


def create_deliverable_package(
    user_input: str,
    output_dir: str,
    selected_deliverables: Optional[list] = None,
    template_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a complete package of deliverables based on user input.

    Args:
        user_input: Raw user input to parse
        output_dir: Directory to save all deliverables
        selected_deliverables: List of deliverable types to generate.
                              If None, generates all available deliverables.
        template_dir: Optional custom template directory

    Returns:
        Dictionary containing generation results
    """
    renderer = TemplateRenderer(template_dir)
    processor = PromptSchemaProcessor()

    # Parse user input once
    parsed_data = processor.parse_user_input(user_input)

    # Determine which deliverables to generate
    if selected_deliverables is None:
        deliverables_to_generate = list(DeliverableType)
    else:
        deliverables_to_generate = selected_deliverables

    results = {
        "generated": [],
        "failed": [],
        "output_directory": output_dir,
        "input_confidence_score": parsed_data["confidence_score"],
        "inferred_type": parsed_data["inferred_deliverable_type"],
    }

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Generate each deliverable
    for deliverable_type in deliverables_to_generate:
        try:
            # Create schema for this deliverable type
            schema = processor.create_schema(deliverable_type, parsed_data)

            # Generate filename
            filename = f"{deliverable_type.value}.md"
            output_path = Path(output_dir) / filename

            # Render and save
            renderer.save_rendered_deliverable(
                deliverable_type, schema, str(output_path)
            )

            results["generated"].append(
                {
                    "type": deliverable_type.value,
                    "filename": filename,
                    "path": str(output_path),
                }
            )

        except Exception as e:
            results["failed"].append({"type": deliverable_type.value, "error": str(e)})

    return results
