"""
Comprehensive Testing Framework

This module provides a comprehensive testing framework for the AI Prototyping Tool
with unit tests, integration tests, performance tests, and automated quality assurance.
"""

import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, MagicMock
import json
import time
from dataclasses import dataclass
import logging
from datetime import datetime

# Import modules to test
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prompt_schema import (
    DeliverableType,
    PromptSchemaProcessor,
    ProblemStatementSchema,
    PersonasSchema,
    create_empty_schema,
)
from template_renderer import TemplateRenderer
from lmstudio_client import LMStudioClient, CompletionRequest
from orchestrator import OrchestrationEngine, OrchestrationConfig
from markdown_renderer import MarkdownRenderer, RenderConfig, OutputFormat
from config_manager import ConfigManager, AppConfig
from error_handler import ErrorHandler, AIPrototypingError, ErrorCategory


@dataclass
class TestResult:
    """Result of a test execution."""

    test_name: str
    passed: bool
    execution_time: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = None


class BaseTestCase(unittest.TestCase):
    """Base test case with common utilities."""

    def setUp(self):
        """Setup test environment."""
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.temp_dir = Path(tempfile.mkdtemp())

        # Setup logging
        logging.basicConfig(level=logging.WARNING)

        # Test data
        self.sample_user_input = """
        Project: Customer Management System
        Problem: Manual customer tracking is inefficient
        Stakeholders: Sales team, Customer service
        Goal: Automate customer relationship management
        Industry: Software Services
        Organization Size: 50-100 employees
        """

        self.sample_json_payload = {
            "project_name": "Test Project",
            "executive_summary": "Test executive summary",
            "current_state": "Test current state",
            "problem_description": "Test problem description",
        }

    def tearDown(self):
        """Cleanup test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with content."""
        file_path = self.temp_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def assert_valid_markdown(self, content: str):
        """Assert that content is valid markdown."""
        self.assertIsInstance(content, str)
        self.assertTrue(
            len(content.strip()) > 0, "Markdown content should not be empty"
        )
        # Basic markdown checks
        lines = content.split("\n")
        has_headers = any(line.strip().startswith("#") for line in lines)
        self.assertTrue(has_headers, "Markdown should contain headers")


class TestPromptSchema(BaseTestCase):
    """Test the prompt schema system."""

    def setUp(self):
        super().setUp()
        self.processor = PromptSchemaProcessor()

    def test_parse_user_input(self):
        """Test user input parsing."""
        result = self.processor.parse_user_input(self.sample_user_input)

        self.assertIsInstance(result, dict)
        self.assertIn("extracted_fields", result)
        self.assertIn("confidence_score", result)
        self.assertIn("inferred_deliverable_type", result)

        # Check extracted fields
        fields = result["extracted_fields"]
        self.assertIn("project", fields)
        self.assertIn("problem", fields)

    def test_create_schema(self):
        """Test schema creation."""
        parsed_data = self.processor.parse_user_input(self.sample_user_input)
        schema = self.processor.create_schema(
            DeliverableType.PROBLEM_STATEMENT, parsed_data
        )

        self.assertIsInstance(schema, ProblemStatementSchema)
        self.assertTrue(hasattr(schema, "project_name"))
        self.assertTrue(hasattr(schema, "timestamp"))

    def test_schema_validation(self):
        """Test schema validation."""
        schema = create_empty_schema(DeliverableType.PROBLEM_STATEMENT)
        validation = self.processor.validate_schema(schema)

        self.assertIsInstance(validation, dict)
        self.assertIn("is_valid", validation)
        self.assertIn("completeness_score", validation)
        self.assertIn("warnings", validation)

    def test_json_payload_transformation(self):
        """Test transformation to JSON payload."""
        payload = self.processor.transform_to_json_payload(
            DeliverableType.PROBLEM_STATEMENT, self.sample_user_input
        )

        self.assertIsInstance(payload, dict)
        self.assertIn("_metadata", payload)
        self.assertIn("project_name", payload)
        self.assertIn("timestamp", payload)


class TestTemplateRenderer(BaseTestCase):
    """Test the template rendering system."""

    def setUp(self):
        super().setUp()
        self.renderer = TemplateRenderer()

    def test_template_validation(self):
        """Test template validation."""
        for deliverable_type in DeliverableType:
            with self.subTest(deliverable_type=deliverable_type):
                validation = self.renderer.validate_template(deliverable_type)
                self.assertIsInstance(validation, dict)
                self.assertIn("is_valid", validation)

    def test_render_from_input(self):
        """Test rendering from user input."""
        rendered = self.renderer.render_from_user_input(
            DeliverableType.PROBLEM_STATEMENT, self.sample_user_input
        )

        self.assert_valid_markdown(rendered)
        self.assertIn("Project", rendered)

    def test_render_from_json(self):
        """Test rendering from JSON payload."""
        rendered = self.renderer.render_from_json_payload(
            DeliverableType.PROBLEM_STATEMENT, self.sample_json_payload
        )

        self.assert_valid_markdown(rendered)
        self.assertIn("Test Project", rendered)

    def test_save_rendered_deliverable(self):
        """Test saving rendered deliverable."""
        schema = create_empty_schema(DeliverableType.PROBLEM_STATEMENT)
        schema.project_name = "Test Project"

        output_path = self.temp_dir / "test_output.md"
        self.renderer.save_rendered_deliverable(
            DeliverableType.PROBLEM_STATEMENT, schema, str(output_path)
        )

        self.assertTrue(output_path.exists())
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assert_valid_markdown(content)


class TestMarkdownRenderer(BaseTestCase):
    """Test the markdown rendering system."""

    def setUp(self):
        super().setUp()
        self.renderer = MarkdownRenderer()

    def test_render_to_file(self):
        """Test rendering to file."""
        content = "# Test Content\n\nThis is a test."
        config = RenderConfig(
            output_path=str(self.temp_dir),
            filename="test.md",
            output_format=OutputFormat.MARKDOWN,
        )

        file_path = self.renderer.render_to_file(content, config)

        self.assertTrue(Path(file_path).exists())
        with open(file_path, "r", encoding="utf-8") as f:
            saved_content = f.read()
        self.assertIn("Test Content", saved_content)

    def test_render_for_web(self):
        """Test rendering for web display."""
        content = "# Test Content\n\nThis is a test."
        result = self.renderer.render_for_web(content)

        self.assertIsInstance(result, dict)
        self.assertIn("html_content", result)
        self.assertIn("markdown_content", result)
        self.assertIn("download_options", result)

        # Check HTML content
        html = result["html_content"]
        self.assertIn("<h1>", html)
        self.assertIn("Test Content", html)

    def test_css_themes(self):
        """Test different CSS themes."""
        content = "# Test\n\nContent"
        themes = ["default", "github", "minimal", "dark", "professional"]

        for theme in themes:
            with self.subTest(theme=theme):
                config = RenderConfig(output_format=OutputFormat.HTML, css_theme=theme)

                rendered = self.renderer.render_markdown(content, config)
                self.assertIn("<html>", rendered)
                self.assertIn("<style>", rendered)


class TestConfigManager(BaseTestCase):
    """Test the configuration management system."""

    def setUp(self):
        super().setUp()
        self.config_manager = ConfigManager(str(self.temp_dir))

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        config = self.config_manager.get_config()
        config.debug = True
        config.model.temperature = 0.5

        self.config_manager.save_config(config)

        # Create new manager to test loading
        new_manager = ConfigManager(str(self.temp_dir))
        loaded_config = new_manager.get_config()

        self.assertEqual(loaded_config.debug, True)
        self.assertEqual(loaded_config.model.temperature, 0.5)

    def test_export_import_config(self):
        """Test exporting and importing configuration."""
        config = self.config_manager.get_config()
        config.version = "test_version"

        export_file = self.temp_dir / "export_config.json"
        self.config_manager.export_config(str(export_file))
        self.assertTrue(export_file.exists())

        # Modify config and import
        config.version = "different_version"
        self.config_manager.save_config(config)

        self.config_manager.import_config(str(export_file))
        imported_config = self.config_manager.get_config()
        self.assertEqual(imported_config.version, "test_version")

    def test_config_validation(self):
        """Test configuration validation."""
        config = self.config_manager.get_config()

        # Valid config
        validation = self.config_manager.validate_config()
        self.assertTrue(validation["is_valid"])

        # Invalid config
        config.model.temperature = 5.0  # Invalid temperature
        self.config_manager.save_config(config)

        validation = self.config_manager.validate_config()
        self.assertFalse(validation["is_valid"])
        self.assertTrue(len(validation["errors"]) > 0)


class TestErrorHandler(BaseTestCase):
    """Test the error handling system."""

    def setUp(self):
        super().setUp()
        self.error_handler = ErrorHandler(str(self.temp_dir))

    def test_handle_custom_error(self):
        """Test handling custom AI prototyping errors."""
        error = AIPrototypingError(
            "Test error",
            category=ErrorCategory.CONFIGURATION,
            details={"test": "value"},
        )

        error_info = self.error_handler.handle_error(error)

        self.assertEqual(error_info.category, ErrorCategory.CONFIGURATION)
        self.assertEqual(error_info.message, "Test error")
        self.assertIn("test", error_info.details)

    def test_handle_standard_error(self):
        """Test handling standard Python errors."""
        error = ValueError("Test value error")

        error_info = self.error_handler.handle_error(error)

        self.assertEqual(error_info.error_type, "ValueError")
        self.assertEqual(error_info.message, "Test value error")
        self.assertIsNotNone(error_info.stack_trace)

    def test_error_stats(self):
        """Test error statistics."""
        # Generate some errors
        errors = [
            ValueError("Error 1"),
            AIPrototypingError("Error 2", category=ErrorCategory.API),
            TypeError("Error 3"),
        ]

        for error in errors:
            self.error_handler.handle_error(error)

        stats = self.error_handler.get_error_stats()
        self.assertEqual(stats["total_errors"], 3)
        self.assertIn("by_category", stats)
        self.assertIn("by_severity", stats)

    def test_error_context(self):
        """Test error context manager."""
        context = {"operation": "test_operation", "user": "test_user"}

        with self.assertRaises(ValueError):
            with self.error_handler.error_context(context):
                raise ValueError("Test error with context")

        # Check that error was recorded with context
        stats = self.error_handler.get_error_stats()
        self.assertEqual(stats["total_errors"], 1)

        recent_error = stats["recent_errors"][0]
        # Context should be saved in error details file


class MockLMStudioClient:
    """Mock LM Studio client for testing."""

    def __init__(self):
        self.healthy = True
        self.models = [
            Mock(id="test-model-1", object="model"),
            Mock(id="test-model-2", object="model"),
        ]

    def health_check(self):
        return {"status": "healthy" if self.healthy else "unhealthy"}

    def list_models(self):
        return self.models

    def create_completion(self, request):
        return Mock(
            choices=[Mock(text="Generated test content")],
            usage=Mock(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        )

    def close(self):
        pass


class TestOrchestrationEngine(BaseTestCase):
    """Test the orchestration engine."""

    def setUp(self):
        super().setUp()
        self.config = OrchestrationConfig(
            lm_studio_base_url="http://localhost:1234/v1",
            max_tokens=100,
            temperature=0.7,
        )

    @patch("orchestrator.LMStudioClient")
    def test_orchestration_initialization(self, mock_client_class):
        """Test orchestration engine initialization."""
        mock_client = MockLMStudioClient()
        mock_client_class.return_value = mock_client

        engine = OrchestrationEngine(self.config)
        self.assertTrue(engine.initialize())
        self.assertIsNotNone(engine.lm_client)

    @patch("orchestrator.LMStudioClient")
    def test_orchestrate_deliverables(self, mock_client_class):
        """Test orchestrating multiple deliverables."""
        mock_client = MockLMStudioClient()
        mock_client_class.return_value = mock_client

        engine = OrchestrationEngine(self.config)
        engine.initialize()

        deliverable_types = [
            DeliverableType.PROBLEM_STATEMENT,
            DeliverableType.PERSONAS,
        ]

        result = engine.orchestrate(self.sample_user_input, deliverable_types)

        self.assertEqual(len(result.deliverable_results), 2)
        self.assertEqual(result.success_count, 2)
        self.assertEqual(result.error_count, 0)
        self.assertIsNotNone(result.merged_document)


class PerformanceTestCase(BaseTestCase):
    """Performance testing utilities."""

    def measure_execution_time(self, func, *args, **kwargs):
        """Measure function execution time."""
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        return result, execution_time

    def test_template_rendering_performance(self):
        """Test template rendering performance."""
        renderer = TemplateRenderer()

        # Test rendering performance
        _, execution_time = self.measure_execution_time(
            renderer.render_from_user_input,
            DeliverableType.PROBLEM_STATEMENT,
            self.sample_user_input,
        )

        # Should complete within 1 second
        self.assertLess(execution_time, 1.0, "Template rendering should be fast")

    def test_schema_processing_performance(self):
        """Test schema processing performance."""
        processor = PromptSchemaProcessor()

        # Test parsing performance
        _, execution_time = self.measure_execution_time(
            processor.parse_user_input, self.sample_user_input
        )

        # Should complete within 0.1 seconds
        self.assertLess(execution_time, 0.1, "Schema processing should be fast")

    def test_markdown_rendering_performance(self):
        """Test markdown rendering performance."""
        renderer = MarkdownRenderer()
        content = "# Test\n\n" + "This is test content. " * 1000  # Large content

        _, execution_time = self.measure_execution_time(
            renderer.render_for_web, content
        )

        # Should complete within 2 seconds
        self.assertLess(
            execution_time,
            2.0,
            "Markdown rendering should handle large content efficiently",
        )


class IntegrationTestCase(BaseTestCase):
    """Integration tests for end-to-end workflows."""

    @patch("orchestrator.LMStudioClient")
    def test_end_to_end_workflow(self, mock_client_class):
        """Test complete end-to-end workflow."""
        mock_client = MockLMStudioClient()
        mock_client_class.return_value = mock_client

        # 1. Parse user input
        processor = PromptSchemaProcessor()
        parsed_data = processor.parse_user_input(self.sample_user_input)

        # 2. Create schema
        schema = processor.create_schema(DeliverableType.PROBLEM_STATEMENT, parsed_data)

        # 3. Render template
        renderer = TemplateRenderer()
        rendered_content = renderer.render_deliverable(
            DeliverableType.PROBLEM_STATEMENT, schema
        )

        # 4. Process with markdown renderer
        md_renderer = MarkdownRenderer()
        web_result = md_renderer.render_for_web(rendered_content)

        # 5. Save to file
        output_file = md_renderer.render_to_file(
            rendered_content,
            RenderConfig(
                output_path=str(self.temp_dir), filename="integration_test.md"
            ),
        )

        # Verify all steps completed successfully
        self.assertIsInstance(parsed_data, dict)
        self.assertIsNotNone(schema)
        self.assert_valid_markdown(rendered_content)
        self.assertIn("html_content", web_result)
        self.assertTrue(Path(output_file).exists())


class QualityAssuranceTestSuite:
    """Quality assurance test suite runner."""

    def __init__(self):
        self.test_results: List[TestResult] = []
        self.setup_logging()

    def setup_logging(self):
        """Setup logging for test execution."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites and return results."""
        test_suites = [
            TestPromptSchema,
            TestTemplateRenderer,
            TestMarkdownRenderer,
            TestConfigManager,
            TestErrorHandler,
            TestOrchestrationEngine,
            PerformanceTestCase,
            IntegrationTestCase,
        ]

        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        execution_time = 0

        for suite_class in test_suites:
            suite_name = suite_class.__name__
            self.logger.info(f"Running test suite: {suite_name}")

            suite = unittest.TestLoader().loadTestsFromTestCase(suite_class)
            start_time = time.time()
            result = unittest.TextTestRunner(
                verbosity=0, stream=open(os.devnull, "w")
            ).run(suite)
            suite_time = time.time() - start_time

            execution_time += suite_time
            total_tests += result.testsRun
            passed_tests += result.testsRun - len(result.failures) - len(result.errors)
            failed_tests += len(result.failures) + len(result.errors)

            # Record test results
            for test, error in result.failures + result.errors:
                test_result = TestResult(
                    test_name=f"{suite_name}.{test._testMethodName}",
                    passed=False,
                    execution_time=(
                        suite_time / result.testsRun if result.testsRun > 0 else 0
                    ),
                    error_message=error,
                )
                self.test_results.append(test_result)

        # Calculate quality metrics
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        results = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "execution_time": execution_time,
            "quality_score": self._calculate_quality_score(),
            "test_results": [result.__dict__ for result in self.test_results],
            "recommendations": self._generate_recommendations(),
        }

        self.logger.info(
            f"Test execution completed: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)"
        )
        return results

    def _calculate_quality_score(self) -> float:
        """Calculate overall quality score."""
        if not self.test_results:
            return 100.0

        passed_count = sum(1 for result in self.test_results if result.passed)
        total_count = len(self.test_results)

        base_score = (passed_count / total_count) * 100

        # Adjust for performance
        avg_execution_time = (
            sum(result.execution_time for result in self.test_results) / total_count
        )
        performance_penalty = min(avg_execution_time * 10, 20)  # Max 20 point penalty

        return max(0, base_score - performance_penalty)

    def _generate_recommendations(self) -> List[str]:
        """Generate quality improvement recommendations."""
        recommendations = []

        failed_tests = [result for result in self.test_results if not result.passed]
        if failed_tests:
            recommendations.append(f"Fix {len(failed_tests)} failing tests")

        slow_tests = [
            result for result in self.test_results if result.execution_time > 1.0
        ]
        if slow_tests:
            recommendations.append(f"Optimize {len(slow_tests)} slow-running tests")

        if len(self.test_results) < 50:
            recommendations.append("Increase test coverage by adding more test cases")

        return recommendations


def run_quality_assurance():
    """Run complete quality assurance suite."""
    qa_suite = QualityAssuranceTestSuite()
    return qa_suite.run_all_tests()


if __name__ == "__main__":
    # Run quality assurance when executed directly
    results = run_quality_assurance()
    print(json.dumps(results, indent=2))
