"""
Orchestration Engine Module

This module provides the core orchestration logic that coordinates between
user input processing, template rendering, and LM Studio API calls to generate
complete deliverable documents.
"""

import json
import time
import logging
from typing import Dict, Any, List, Optional, Union, Callable, Iterator
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from prompt_schema import (
    DeliverableType,
    BaseSchema,
    PromptSchemaProcessor,
    get_schema_for_deliverable,
    create_empty_schema,
)
from template_renderer import TemplateRenderer
from lmstudio_client import (
    LMStudioClient,
    CompletionRequest,
    CompletionResponse,
    LMStudioError,
    Model,
)


class CompletionMode(Enum):
    """Completion modes for the orchestrator."""

    BATCH = "batch"  # Complete all deliverables at once
    STREAMING = "streaming"  # Complete deliverables one by one with streaming
    SEQUENTIAL = "sequential"  # Complete deliverables one by one without streaming


@dataclass
class OrchestrationConfig:
    """Configuration for the orchestration engine."""

    # LM Studio configuration
    lm_studio_base_url: str = "http://localhost:1234/v1"
    lm_studio_api_key: Optional[str] = None
    model_name: Optional[str] = None  # If None, will use first available model

    # Generation parameters
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9

    # Orchestration settings
    completion_mode: CompletionMode = CompletionMode.SEQUENTIAL
    template_dir: Optional[str] = None

    # Output settings
    merge_into_single_document: bool = True
    include_table_of_contents: bool = True
    output_format: str = "markdown"  # Currently only markdown supported

    # Retry and timeout settings
    max_retries_per_deliverable: int = 3
    request_timeout: float = 60.0

    # Logging
    enable_logging: bool = True
    log_level: str = "INFO"


@dataclass
class DeliverableResult:
    """Result of generating a single deliverable."""

    deliverable_type: DeliverableType
    content: str
    success: bool
    error_message: Optional[str] = None
    execution_time: float = 0.0
    token_usage: Optional[Dict[str, int]] = None
    prompt_used: Optional[str] = None


@dataclass
class OrchestrationResult:
    """Result of the complete orchestration process."""

    deliverable_results: List[DeliverableResult]
    merged_document: Optional[str] = None
    total_execution_time: float = 0.0
    total_tokens_used: int = 0
    success_count: int = 0
    error_count: int = 0
    config_used: Optional[OrchestrationConfig] = None


class PromptGenerator:
    """Generates tailored prompts for each deliverable type."""

    def __init__(self):
        self.base_system_prompt = """
You are an expert business analyst and technical writer. Your task is to generate
high-quality, professional documentation based on the user's requirements.

Please generate content that is:
- Clear and well-structured
- Professional and business-appropriate
- Comprehensive yet concise
- Actionable and practical
- Following industry best practices

Format your response in clean Markdown with appropriate headers, bullet points,
and formatting as needed.
"""

    def generate_prompt(
        self,
        deliverable_type: DeliverableType,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a tailored prompt for a specific deliverable type."""

        # Get deliverable-specific instructions
        deliverable_instructions = self._get_deliverable_instructions(deliverable_type)

        # Build the complete prompt
        prompt_parts = [
            self.base_system_prompt,
            f"\n\n## Task: Generate {deliverable_type.value.replace('_', ' ').title()}",
            deliverable_instructions,
            "\n\n## User Requirements:",
            user_input,
        ]

        # Add context if provided
        if context:
            prompt_parts.extend(
                ["\n\n## Additional Context:", json.dumps(context, indent=2)]
            )

        prompt_parts.append("\n\n## Generated Content:")

        return "\n".join(prompt_parts)

    def _get_deliverable_instructions(self, deliverable_type: DeliverableType) -> str:
        """Get specific instructions for each deliverable type."""
        instructions = {
            DeliverableType.PROBLEM_STATEMENT: """
Generate a comprehensive problem statement that includes:
- Clear definition of the business problem or opportunity
- Current state analysis
- Desired future state
- Impact assessment
- Success criteria
- Key stakeholders
""",
            DeliverableType.PERSONAS: """
Create detailed user personas that include:
- Demographics and background
- Goals and motivations
- Pain points and challenges
- Technology proficiency
- Behavior patterns
- Needs and expectations
Generate 3-5 distinct personas that represent the target user base.
""",
            DeliverableType.USE_CASES: """
Develop comprehensive use cases that include:
- Primary and secondary actors
- Preconditions and postconditions
- Main success scenarios
- Alternative flows
- Exception handling
- Business rules
Include both high-level and detailed use cases.
""",
            DeliverableType.TOOL_OUTLINE: """
Create a detailed tool outline that includes:
- Tool overview and purpose
- Key features and capabilities
- Technical architecture
- User interface design
- Integration points
- Implementation considerations
""",
            DeliverableType.IMPLEMENTATION_INSTRUCTIONS: """
Provide comprehensive implementation instructions that include:
- Step-by-step implementation plan
- Technical requirements
- Dependencies and prerequisites
- Resource allocation
- Timeline and milestones
- Risk mitigation strategies
- Quality assurance procedures
""",
            DeliverableType.COPILOT365_PRESENTATION_PROMPT: """
Generate a presentation prompt for Microsoft Copilot 365 that includes:
- Executive summary
- Key business benefits
- Implementation roadmap
- ROI projections
- Change management considerations
- Next steps and recommendations
Format for a business audience and executive presentation.
""",
            DeliverableType.EFFECTIVENESS_ASSESSMENT: """
Create an effectiveness assessment framework that includes:
- Key performance indicators (KPIs)
- Measurement methodologies
- Success metrics
- Evaluation criteria
- Reporting mechanisms
- Continuous improvement recommendations
""",
        }

        return instructions.get(
            deliverable_type,
            "Generate comprehensive documentation for this deliverable.",
        )


class OrchestrationEngine:
    """Main orchestration engine that coordinates the entire process."""

    def __init__(self, config: Optional[OrchestrationConfig] = None):
        """
        Initialize the orchestration engine.

        Args:
            config: Configuration for the orchestration process
        """
        self.config = config or OrchestrationConfig()

        # Setup logging
        if self.config.enable_logging:
            logging.basicConfig(
                level=getattr(logging, self.config.log_level.upper()),
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.lm_client = None
        self.template_renderer = TemplateRenderer(self.config.template_dir)
        self.prompt_generator = PromptGenerator()
        self.schema_processor = PromptSchemaProcessor()

        # State tracking
        self._available_models: List[Model] = []
        self._selected_model: Optional[str] = None

    def initialize(self) -> bool:
        """Initialize the orchestration engine and validate setup."""
        try:
            # Initialize LM Studio client
            self.lm_client = LMStudioClient(
                base_url=self.config.lm_studio_base_url,
                api_key=self.config.lm_studio_api_key,
                timeout=self.config.request_timeout,
            )

            # Check health and get models
            health = self.lm_client.health_check()
            if health["status"] != "healthy":
                self.logger.error(f"LM Studio is not healthy: {health}")
                return False

            self._available_models = self.lm_client.list_models()
            if not self._available_models:
                self.logger.error("No models available in LM Studio")
                return False

            # Select model
            if self.config.model_name:
                model_ids = [m.id for m in self._available_models]
                if self.config.model_name in model_ids:
                    self._selected_model = self.config.model_name
                else:
                    self.logger.warning(
                        f"Requested model '{self.config.model_name}' not found. Available: {model_ids}"
                    )
                    self._selected_model = self._available_models[0].id
            else:
                self._selected_model = self._available_models[0].id

            self.logger.info(f"Initialized with model: {self._selected_model}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize orchestration engine: {e}")
            return False

    def orchestrate(
        self,
        user_input: str,
        deliverable_types: List[DeliverableType],
        context: Optional[Dict[str, Any]] = None,
    ) -> OrchestrationResult:
        """
        Main orchestration method that coordinates the entire process.

        Args:
            user_input: Raw user input describing requirements
            deliverable_types: List of deliverable types to generate
            context: Additional context for generation

        Returns:
            OrchestrationResult with all deliverable results
        """
        start_time = time.time()

        if not self.lm_client or not self._selected_model:
            if not self.initialize():
                return OrchestrationResult(
                    deliverable_results=[],
                    error_count=len(deliverable_types),
                    total_execution_time=time.time() - start_time,
                )

        self.logger.info(
            f"Starting orchestration for {len(deliverable_types)} deliverables"
        )

        deliverable_results = []
        total_tokens = 0

        # Process deliverables based on completion mode
        if self.config.completion_mode == CompletionMode.BATCH:
            deliverable_results = self._process_batch(
                user_input, deliverable_types, context
            )
        elif self.config.completion_mode == CompletionMode.STREAMING:
            deliverable_results = self._process_streaming(
                user_input, deliverable_types, context
            )
        else:  # SEQUENTIAL
            deliverable_results = self._process_sequential(
                user_input, deliverable_types, context
            )

        # Calculate totals
        for result in deliverable_results:
            if result.token_usage:
                total_tokens += result.token_usage.get("total_tokens", 0)

        # Merge documents if requested
        merged_document = None
        if self.config.merge_into_single_document:
            merged_document = self._merge_deliverables(deliverable_results)

        # Create final result
        success_count = sum(1 for r in deliverable_results if r.success)
        error_count = len(deliverable_results) - success_count
        total_time = time.time() - start_time

        self.logger.info(
            f"Orchestration completed: {success_count} successful, {error_count} failed, {total_time:.2f}s"
        )

        return OrchestrationResult(
            deliverable_results=deliverable_results,
            merged_document=merged_document,
            total_execution_time=total_time,
            total_tokens_used=total_tokens,
            success_count=success_count,
            error_count=error_count,
            config_used=self.config,
        )

    def _process_sequential(
        self,
        user_input: str,
        deliverable_types: List[DeliverableType],
        context: Optional[Dict[str, Any]],
    ) -> List[DeliverableResult]:
        """Process deliverables sequentially without streaming."""
        results = []

        for deliverable_type in deliverable_types:
            self.logger.info(f"Processing {deliverable_type.value}")
            result = self._generate_single_deliverable(
                user_input, deliverable_type, context
            )
            results.append(result)

            if not result.success:
                self.logger.warning(
                    f"Failed to generate {deliverable_type.value}: {result.error_message}"
                )

        return results

    def _process_batch(
        self,
        user_input: str,
        deliverable_types: List[DeliverableType],
        context: Optional[Dict[str, Any]],
    ) -> List[DeliverableResult]:
        """Process all deliverables in a single batch request."""
        # For now, implement as sequential since LM Studio doesn't support true batching
        # This could be enhanced to use concurrent requests in the future
        return self._process_sequential(user_input, deliverable_types, context)

    def _process_streaming(
        self,
        user_input: str,
        deliverable_types: List[DeliverableType],
        context: Optional[Dict[str, Any]],
    ) -> List[DeliverableResult]:
        """Process deliverables with streaming support."""
        # For now, implement as sequential since streaming support would require
        # additional implementation in the LM Studio client
        self.logger.warning(
            "Streaming mode not fully implemented, falling back to sequential"
        )
        return self._process_sequential(user_input, deliverable_types, context)

    def _generate_single_deliverable(
        self,
        user_input: str,
        deliverable_type: DeliverableType,
        context: Optional[Dict[str, Any]],
    ) -> DeliverableResult:
        """Generate a single deliverable."""
        start_time = time.time()

        try:
            # Generate prompt
            prompt = self.prompt_generator.generate_prompt(
                deliverable_type, user_input, context
            )

            # Create completion request
            request = CompletionRequest(
                model=self._selected_model,
                prompt=prompt,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
            )

            # Retry logic
            for attempt in range(self.config.max_retries_per_deliverable):
                try:
                    response = self.lm_client.create_completion(request)

                    if response.choices and response.choices[0].text:
                        content = response.choices[0].text.strip()

                        # Extract token usage
                        token_usage = None
                        if response.usage:
                            token_usage = {
                                "prompt_tokens": response.usage.prompt_tokens,
                                "completion_tokens": response.usage.completion_tokens,
                                "total_tokens": response.usage.total_tokens,
                            }

                        return DeliverableResult(
                            deliverable_type=deliverable_type,
                            content=content,
                            success=True,
                            execution_time=time.time() - start_time,
                            token_usage=token_usage,
                            prompt_used=prompt,
                        )
                    else:
                        raise LMStudioError(
                            "Empty response from model", error_type="api_error"
                        )

                except LMStudioError as e:
                    if attempt == self.config.max_retries_per_deliverable - 1:
                        raise
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed for {deliverable_type.value}: {e}"
                    )
                    time.sleep(2**attempt)  # Exponential backoff

        except Exception as e:
            self.logger.error(f"Failed to generate {deliverable_type.value}: {e}")
            return DeliverableResult(
                deliverable_type=deliverable_type,
                content="",
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time,
                prompt_used=prompt if "prompt" in locals() else None,
            )

    def _merge_deliverables(self, results: List[DeliverableResult]) -> str:
        """Merge multiple deliverable results into a single document."""
        successful_results = [r for r in results if r.success]

        if not successful_results:
            return "# Document Generation Failed\n\nNo deliverables were successfully generated."

        # Build merged document
        document_parts = []

        # Add title and table of contents
        document_parts.append("# Generated Documentation\n")

        if self.config.include_table_of_contents:
            document_parts.append("## Table of Contents\n")
            for i, result in enumerate(successful_results, 1):
                title = result.deliverable_type.value.replace("_", " ").title()
                document_parts.append(
                    f"{i}. [{title}](#{title.lower().replace(' ', '-')})"
                )
            document_parts.append("\n")

        # Add each deliverable
        for result in successful_results:
            title = result.deliverable_type.value.replace("_", " ").title()
            document_parts.extend([f"## {title}\n", result.content, "\n---\n"])

        # Add generation metadata
        document_parts.extend(
            [
                "## Generation Metadata\n",
                f"- **Generated at**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
                f"- **Successful deliverables**: {len(successful_results)}\n",
                f"- **Failed deliverables**: {len(results) - len(successful_results)}\n",
                f"- **Model used**: {self._selected_model}\n",
            ]
        )

        return "\n".join(document_parts)

    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        if not self._available_models:
            if self.lm_client:
                self._available_models = self.lm_client.list_models()
        return [model.id for model in self._available_models]

    def set_model(self, model_name: str) -> bool:
        """Set the model to use for generation."""
        available_models = self.get_available_models()
        if model_name in available_models:
            self._selected_model = model_name
            self.logger.info(f"Model set to: {model_name}")
            return True
        else:
            self.logger.error(
                f"Model '{model_name}' not available. Available: {available_models}"
            )
            return False

    def validate_deliverable_templates(self) -> Dict[str, Any]:
        """Validate that all deliverable templates are available."""
        validation_results = {}

        for deliverable_type in DeliverableType:
            result = self.template_renderer.validate_template(deliverable_type)
            validation_results[deliverable_type.value] = result

        return validation_results

    def close(self) -> None:
        """Clean up resources."""
        if self.lm_client:
            self.lm_client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Convenience functions
def create_orchestrator(
    config: Optional[OrchestrationConfig] = None,
) -> OrchestrationEngine:
    """Create and initialize an orchestration engine."""
    engine = OrchestrationEngine(config)
    engine.initialize()
    return engine


def quick_generate(
    user_input: str,
    deliverable_types: List[DeliverableType],
    model_name: Optional[str] = None,
    **config_kwargs,
) -> OrchestrationResult:
    """Quick function to generate deliverables without manual setup."""
    config = OrchestrationConfig(model_name=model_name, **config_kwargs)

    with create_orchestrator(config) as engine:
        return engine.orchestrate(user_input, deliverable_types)
