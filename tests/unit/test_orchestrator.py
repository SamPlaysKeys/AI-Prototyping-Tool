"""
Unit tests for the orchestrator module.

Tests orchestration logic, configuration, deliverable generation, etc.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.orchestrator import (
    OrchestrationEngine,
    OrchestrationConfig,
    CompletionMode,
    quick_generate,
)
from src.prompt_schema import DeliverableType


@pytest.mark.unit
class TestOrchestrationEngine:
    """Test orchestration engine functionality."""

    def test_engine_initialization(self, orchestration_config):
        """Test orchestration engine initialization."""
        engine = OrchestrationEngine(orchestration_config)

        assert engine.config == orchestration_config
        assert engine.template_renderer is not None
        assert engine.prompt_generator is not None
        assert engine.schema_processor is not None

    @patch("src.orchestrator.LMStudioClient")
    def test_engine_initialization_success(
        self, mock_client_class, orchestration_config, mock_lm_studio_client
    ):
        """Test successful engine initialization with LM Studio."""
        mock_client_class.return_value = mock_lm_studio_client

        engine = OrchestrationEngine(orchestration_config)
        result = engine.initialize()

        assert result is True
        assert engine.lm_client is not None
        assert engine._selected_model is not None

    @patch("src.orchestrator.LMStudioClient")
    def test_orchestrate_single_deliverable(
        self,
        mock_client_class,
        orchestration_config,
        mock_lm_studio_client,
        sample_user_input,
    ):
        """Test orchestrating a single deliverable."""
        mock_client_class.return_value = mock_lm_studio_client

        engine = OrchestrationEngine(orchestration_config)
        engine.initialize()

        result = engine.orchestrate(
            sample_user_input, [DeliverableType.PROBLEM_STATEMENT]
        )

        assert result.success_count == 1
        assert result.error_count == 0
        assert len(result.deliverable_results) == 1
        assert result.deliverable_results[0].success is True
        assert result.merged_document is not None

    @patch("src.orchestrator.LMStudioClient")
    def test_orchestrate_multiple_deliverables(
        self,
        mock_client_class,
        orchestration_config,
        mock_lm_studio_client,
        sample_user_input,
    ):
        """Test orchestrating multiple deliverables."""
        mock_client_class.return_value = mock_lm_studio_client

        engine = OrchestrationEngine(orchestration_config)
        engine.initialize()

        deliverable_types = [
            DeliverableType.PROBLEM_STATEMENT,
            DeliverableType.PERSONAS,
            DeliverableType.USE_CASES,
        ]

        result = engine.orchestrate(sample_user_input, deliverable_types)

        assert result.success_count == 3
        assert result.error_count == 0
        assert len(result.deliverable_results) == 3
        assert all(dr.success for dr in result.deliverable_results)

    def test_completion_modes(self, orchestration_config):
        """Test different completion modes."""
        modes = [
            CompletionMode.SEQUENTIAL,
            CompletionMode.BATCH,
            CompletionMode.STREAMING,
        ]

        for mode in modes:
            config = orchestration_config
            config.completion_mode = mode
            engine = OrchestrationEngine(config)

            # Should initialize without error
            assert engine.config.completion_mode == mode

    def test_get_available_models(self, orchestration_config, mock_lm_studio_client):
        """Test getting available models."""
        with patch(
            "src.orchestrator.LMStudioClient", return_value=mock_lm_studio_client
        ):
            engine = OrchestrationEngine(orchestration_config)
            engine.initialize()

            models = engine.get_available_models()

            assert isinstance(models, list)
            assert len(models) > 0
            assert "test-model-1" in models

    def test_set_model(self, orchestration_config, mock_lm_studio_client):
        """Test setting a specific model."""
        with patch(
            "src.orchestrator.LMStudioClient", return_value=mock_lm_studio_client
        ):
            engine = OrchestrationEngine(orchestration_config)
            engine.initialize()

            # Test setting valid model
            result = engine.set_model("test-model-1")
            assert result is True
            assert engine._selected_model == "test-model-1"

            # Test setting invalid model
            result = engine.set_model("invalid-model")
            assert result is False

    def test_validate_deliverable_templates(self, orchestration_config):
        """Test template validation."""
        engine = OrchestrationEngine(orchestration_config)

        validation_results = engine.validate_deliverable_templates()

        assert isinstance(validation_results, dict)
        assert len(validation_results) == len(DeliverableType)

        for deliverable_type in DeliverableType:
            assert deliverable_type.value in validation_results


@pytest.mark.unit
class TestQuickGenerate:
    """Test quick generate convenience function."""

    @patch("src.orchestrator.create_orchestrator")
    def test_quick_generate_success(self, mock_create_orchestrator, sample_user_input):
        """Test successful quick generation."""
        # Mock orchestrator
        mock_engine = Mock()
        mock_result = Mock()
        mock_result.success_count = 1
        mock_result.error_count = 0
        mock_engine.orchestrate.return_value = mock_result
        mock_engine.__enter__.return_value = mock_engine
        mock_engine.__exit__.return_value = None

        mock_create_orchestrator.return_value = mock_engine

        result = quick_generate(sample_user_input, [DeliverableType.PROBLEM_STATEMENT])

        assert result == mock_result
        mock_engine.orchestrate.assert_called_once()


@pytest.mark.unit
class TestOrchestrationConfig:
    """Test orchestration configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = OrchestrationConfig()

        assert config.lm_studio_base_url == "http://localhost:1234/v1"
        assert config.max_tokens == 2048
        assert config.temperature == 0.7
        assert config.completion_mode == CompletionMode.SEQUENTIAL
        assert config.merge_into_single_document is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = OrchestrationConfig(
            lm_studio_base_url="http://custom:8080/v1",
            max_tokens=1000,
            temperature=0.5,
            completion_mode=CompletionMode.BATCH,
        )

        assert config.lm_studio_base_url == "http://custom:8080/v1"
        assert config.max_tokens == 1000
        assert config.temperature == 0.5
        assert config.completion_mode == CompletionMode.BATCH
