"""
CLI tests using Click's testing utilities.

Tests command-line interface functionality, argument parsing, etc.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

from cli.main import cli, generate, models, deliverables, health


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.mark.cli
class TestCLIMain:
    """Test main CLI functionality."""

    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "AI Prototyping Tool" in result.output
        assert "generate" in result.output
        assert "models" in result.output
        assert "deliverables" in result.output

    def test_cli_version(self, runner):
        """Test CLI version command."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "AI Prototyping Tool" in result.output

    def test_cli_verbose_mode(self, runner):
        """Test CLI verbose mode."""
        result = runner.invoke(cli, ["-v", "--help"])
        assert result.exit_code == 0


@pytest.mark.cli
class TestGenerateCommand:
    """Test generate command functionality."""

    @patch("cli.main.quick_generate")
    @patch("cli.main.test_lm_studio_connection")
    @patch("cli.main.get_available_models")
    def test_generate_with_prompt(
        self,
        mock_get_models,
        mock_test_connection,
        mock_quick_generate,
        runner,
        temp_dir,
    ):
        """Test generate command with text prompt."""
        # Setup mocks
        mock_test_connection.return_value = True
        mock_get_models.return_value = ["test-model"]

        mock_result = Mock()
        mock_result.success_count = 1
        mock_result.error_count = 0
        mock_result.merged_document = "# Generated Content\n\nTest content"
        mock_result.deliverable_results = [Mock(success=True)]
        mock_result.total_tokens_used = 100
        mock_result.total_execution_time = 1.5
        mock_quick_generate.return_value = mock_result

        result = runner.invoke(
            generate,
            [
                "--prompt",
                "Create a test system",
                "--output",
                str(temp_dir),
                "--deliverable-types",
                "problem_statement",
            ],
        )

        assert result.exit_code == 0
        assert "Generated content saved" in result.output
        mock_quick_generate.assert_called_once()

    def test_generate_with_prompt_file(self, runner, temp_dir, create_test_file):
        """Test generate command with prompt file."""
        prompt_file = create_test_file(
            temp_dir, "prompt.txt", "Create a web application"
        )

        with patch("cli.main.quick_generate") as mock_generate, patch(
            "cli.main.test_lm_studio_connection", return_value=True
        ), patch("cli.main.get_available_models", return_value=["test-model"]):

            mock_result = Mock()
            mock_result.success_count = 1
            mock_result.error_count = 0
            mock_result.merged_document = "# Generated Content"
            mock_result.deliverable_results = [Mock(success=True)]
            mock_result.total_tokens_used = 50
            mock_result.total_execution_time = 1.0
            mock_generate.return_value = mock_result

            result = runner.invoke(
                generate, ["--prompt-file", str(prompt_file), "--output", str(temp_dir)]
            )

            assert result.exit_code == 0

    def test_generate_multiple_deliverables(self, runner, temp_dir):
        """Test generate command with multiple deliverable types."""
        with patch("cli.main.quick_generate") as mock_generate, patch(
            "cli.main.test_lm_studio_connection", return_value=True
        ), patch("cli.main.get_available_models", return_value=["test-model"]):

            mock_result = Mock()
            mock_result.success_count = 2
            mock_result.error_count = 0
            mock_result.merged_document = "# Generated Content"
            mock_result.deliverable_results = [Mock(success=True), Mock(success=True)]
            mock_result.total_tokens_used = 200
            mock_result.total_execution_time = 3.0
            mock_generate.return_value = mock_result

            result = runner.invoke(
                generate,
                [
                    "--prompt",
                    "Create a system",
                    "--deliverable-types",
                    "problem_statement",
                    "--deliverable-types",
                    "personas",
                    "--output",
                    str(temp_dir),
                ],
            )

            assert result.exit_code == 0
            assert "2/2" in result.output or "success" in result.output

    def test_generate_dry_run(self, runner):
        """Test generate command with dry run."""
        result = runner.invoke(generate, ["--prompt", "Test prompt", "--dry-run"])

        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "No generation will occur" in result.output

    def test_generate_connection_error(self, runner):
        """Test generate command with LM Studio connection error."""
        with patch("cli.main.test_lm_studio_connection", return_value=False):
            result = runner.invoke(generate, ["--prompt", "Test prompt"])

            assert result.exit_code != 0
            assert "Cannot connect to LM Studio" in result.output

    def test_generate_invalid_deliverable_type(self, runner):
        """Test generate command with invalid deliverable type."""
        result = runner.invoke(
            generate, ["--prompt", "Test prompt", "--deliverable-types", "invalid_type"]
        )

        assert result.exit_code != 0
        assert "Unknown deliverable type" in result.output

    def test_generate_missing_prompt(self, runner):
        """Test generate command without prompt."""
        result = runner.invoke(generate, [])

        assert result.exit_code != 0
        assert "Either --prompt or --prompt-file must be provided" in result.output


@pytest.mark.cli
class TestModelsCommand:
    """Test models command functionality."""

    @patch("cli.main.get_available_models")
    @patch("cli.main.test_lm_studio_connection")
    def test_models_list_success(self, mock_test_connection, mock_get_models, runner):
        """Test successful models listing."""
        mock_test_connection.return_value = True
        mock_get_models.return_value = ["model1", "model2", "model3"]

        result = runner.invoke(models)

        assert result.exit_code == 0
        assert "Available models (3):" in result.output
        assert "model1" in result.output
        assert "model2" in result.output
        assert "model3" in result.output

    @patch("cli.main.test_lm_studio_connection")
    def test_models_connection_error(self, mock_test_connection, runner):
        """Test models command with connection error."""
        mock_test_connection.return_value = False

        result = runner.invoke(models)

        assert result.exit_code != 0
        assert "Cannot connect to LM Studio" in result.output

    @patch("cli.main.get_available_models")
    @patch("cli.main.test_lm_studio_connection")
    def test_models_no_models_loaded(
        self, mock_test_connection, mock_get_models, runner
    ):
        """Test models command when no models are loaded."""
        mock_test_connection.return_value = True
        mock_get_models.return_value = []

        result = runner.invoke(models)

        assert result.exit_code == 0
        assert "No models are currently loaded" in result.output
        assert "Please load a model" in result.output


@pytest.mark.cli
class TestDeliverablesCommand:
    """Test deliverables command functionality."""

    def test_deliverables_list(self, runner):
        """Test listing available deliverable types."""
        result = runner.invoke(deliverables)

        assert result.exit_code == 0
        assert "Available deliverable types:" in result.output
        assert "problem_statement" in result.output
        assert "personas" in result.output
        assert "use_cases" in result.output
        assert "Usage example:" in result.output


@pytest.mark.cli
class TestHealthCommand:
    """Test health command functionality."""

    @patch("cli.main.LMStudioClient")
    def test_health_check_success(self, mock_client_class, runner):
        """Test successful health check."""
        mock_client = Mock()
        mock_client.health_check.return_value = {"status": "healthy"}
        mock_client.list_models.return_value = [Mock(), Mock()]
        mock_client_class.return_value = mock_client

        result = runner.invoke(health)

        assert result.exit_code == 0
        assert "LM Studio is healthy" in result.output
        assert "Found 2 available model(s)" in result.output

    @patch("cli.main.LMStudioClient")
    def test_health_check_connection_error(self, mock_client_class, runner):
        """Test health check with connection error."""
        from src.lmstudio_client import LMStudioError, ErrorType

        mock_client = Mock()
        mock_client.health_check.side_effect = LMStudioError(
            "Connection failed", ErrorType.NETWORK_ERROR
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(health)

        assert result.exit_code != 0
        assert "Connection failed" in result.output


@pytest.mark.cli
class TestCLIHelpers:
    """Test CLI helper functions."""

    def test_format_output_markdown(self):
        """Test markdown output formatting."""
        from cli.main import format_output

        content = "# Test\n\nContent"
        result = format_output(content, "markdown")

        assert result == content

    def test_format_output_json(self):
        """Test JSON output formatting."""
        from cli.main import format_output

        content = "Simple text content"
        result = format_output(content, "json")

        assert json.loads(result)
        assert "content" in json.loads(result)

    def test_validate_file_exists(self, temp_dir, create_test_file):
        """Test file validation helper."""
        from cli.main import validate_file_exists, CLIError

        # Test existing file
        test_file = create_test_file(temp_dir, "test.txt", "content")
        result = validate_file_exists(str(test_file))
        assert result == test_file

        # Test non-existing file
        with pytest.raises(CLIError, match="File not found"):
            validate_file_exists(str(temp_dir / "nonexistent.txt"))

    def test_validate_output_dir(self, temp_dir):
        """Test output directory validation."""
        from cli.main import validate_output_dir

        # Test existing directory
        result = validate_output_dir(str(temp_dir))
        assert result == temp_dir

        # Test new directory creation
        new_dir = temp_dir / "new_dir"
        result = validate_output_dir(str(new_dir))
        assert result == new_dir
        assert new_dir.exists()

    def test_parse_deliverable_types(self):
        """Test deliverable types parsing."""
        from cli.main import parse_deliverable_types, CLIError
        from src.prompt_schema import DeliverableType

        # Test valid types
        types = parse_deliverable_types(["problem_statement", "personas"])
        assert len(types) == 2
        assert DeliverableType.PROBLEM_STATEMENT in types
        assert DeliverableType.PERSONAS in types

        # Test invalid type
        with pytest.raises(CLIError, match="Unknown deliverable type"):
            parse_deliverable_types(["invalid_type"])
