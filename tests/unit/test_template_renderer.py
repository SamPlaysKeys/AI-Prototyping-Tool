"""
Unit tests for the template rendering module.

Tests template validation, rendering from input, schema integration, etc.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.template_renderer import TemplateRenderer
from src.prompt_schema import DeliverableType, create_empty_schema


@pytest.fixture
def renderer():
    """Create a template renderer instance."""
    return TemplateRenderer()


@pytest.mark.unit
class TestTemplateRenderer:
    """Test template rendering functionality."""

    def test_template_validation_all_deliverables(self, renderer, deliverable_types):
        """Test template validation for all deliverable types."""
        for deliverable_type in deliverable_types:
            validation = renderer.validate_template(deliverable_type)
            assert isinstance(validation, dict)
            assert "is_valid" in validation
            assert "exists" in validation
            assert "can_load" in validation

    def test_render_from_user_input(
        self, renderer, sample_user_input, assert_valid_markdown
    ):
        """Test rendering from user input."""
        rendered = renderer.render_from_user_input(
            DeliverableType.PROBLEM_STATEMENT, sample_user_input
        )

        assert_valid_markdown(rendered)
        assert "Customer Management System" in rendered
        assert "Project:" in rendered or "Project Name" in rendered

    def test_render_from_json_payload(
        self, renderer, sample_json_payload, assert_valid_markdown
    ):
        """Test rendering from JSON payload."""
        rendered = renderer.render_from_json_payload(
            DeliverableType.PROBLEM_STATEMENT, sample_json_payload
        )

        assert_valid_markdown(rendered)
        assert "Test Project" in rendered
        assert "executive summary" in rendered.lower()
