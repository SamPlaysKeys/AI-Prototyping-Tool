"""
Prompt Schema Module

This module provides functionality to transform raw user input into standardized JSON payloads
for LLM processing and template rendering. It defines schemas for each deliverable type
and includes validation and transformation functions.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import re


class DeliverableType(Enum):
    """Enumeration of available deliverable types."""

    PROBLEM_STATEMENT = "problem_statement"
    PERSONAS = "personas"
    USE_CASES = "use_cases"
    TOOL_OUTLINE = "tool_outline"
    IMPLEMENTATION_INSTRUCTIONS = "implementation_instructions"
    COPILOT365_PRESENTATION_PROMPT = "copilot365_presentation_prompt"
    EFFECTIVENESS_ASSESSMENT = "effectiveness_assessment"


class Priority(Enum):
    """Priority levels for various elements."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Status(Enum):
    """Status options for various elements."""

    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"
    CANCELLED = "Cancelled"


@dataclass
class BaseSchema:
    """Base schema with common fields for all deliverables."""

    project_name: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert the schema to a dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert the schema to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ProblemStatementSchema(BaseSchema):
    """Schema for Problem Statement deliverable."""

    executive_summary: str = ""
    current_state: str = ""
    problem_description: str = ""
    impact_analysis: str = ""
    industry_domain: str = ""
    organization_size: str = ""
    technical_environment: str = ""
    primary_stakeholders: str = ""
    secondary_stakeholders: str = ""
    key_performance_indicators: str = ""
    acceptance_criteria: str = ""
    technical_constraints: str = ""
    business_constraints: str = ""
    assumptions: str = ""
    project_duration: str = ""
    key_milestones: str = ""


@dataclass
class PersonaData:
    """Data structure for individual persona information."""

    name: str = ""
    role: str = ""
    department: str = ""
    experience_level: str = ""
    age_range: str = ""
    background: str = ""
    primary_goals: str = ""
    secondary_goals: str = ""
    motivations: str = ""
    pain_points: str = ""
    technical_challenges: str = ""
    process_challenges: str = ""
    technical_expertise: str = ""
    preferred_tools: str = ""
    device_usage: str = ""
    software_familiarity: str = ""
    work_style: str = ""
    communication_preferences: str = ""
    decision_making: str = ""
    functional_needs: str = ""
    non_functional_needs: str = ""
    information_needs: str = ""
    success_metrics: str = ""
    quote: str = ""


@dataclass
class PersonasSchema(BaseSchema):
    """Schema for Personas deliverable."""

    personas_overview: str = ""
    personas: List[PersonaData] = field(default_factory=list)
    persona_relationships: str = ""
    design_implications: str = ""


@dataclass
class AlternativeFlow:
    """Data structure for alternative flows in use cases."""

    name: str = ""
    trigger: str = ""
    steps: List[str] = field(default_factory=list)


@dataclass
class ExceptionFlow:
    """Data structure for exception flows in use cases."""

    name: str = ""
    trigger: str = ""
    steps: List[str] = field(default_factory=list)


@dataclass
class TestScenario:
    """Data structure for test scenarios."""

    name: str = ""
    objective: str = ""
    steps: str = ""
    expected_result: str = ""


@dataclass
class UseCaseData:
    """Data structure for individual use case information."""

    id: str = ""
    title: str = ""
    priority: str = ""
    complexity: str = ""
    category: str = ""
    status: str = ""
    primary_actors: str = ""
    secondary_actors: str = ""
    description: str = ""
    preconditions: str = ""
    success_postconditions: str = ""
    failure_postconditions: str = ""
    main_scenario: List[str] = field(default_factory=list)
    alternative_flows: List[AlternativeFlow] = field(default_factory=list)
    exceptions: List[ExceptionFlow] = field(default_factory=list)
    business_rules: str = ""
    performance_requirements: str = ""
    security_requirements: str = ""
    usability_requirements: str = ""
    reliability_requirements: str = ""
    acceptance_criteria: List[str] = field(default_factory=list)
    dependencies_on: str = ""
    depended_upon_by: str = ""
    test_scenarios: List[TestScenario] = field(default_factory=list)


@dataclass
class UseCasesSchema(BaseSchema):
    """Schema for Use Cases deliverable."""

    use_cases_overview: str = ""
    use_case_categories: str = ""
    use_cases: List[UseCaseData] = field(default_factory=list)
    use_case_relationships: str = ""
    traceability_matrix: str = ""


@dataclass
class SystemComponent:
    """Data structure for system components."""

    name: str = ""
    type: str = ""
    purpose: str = ""
    tech_stack: str = ""
    dependencies: str = ""
    description: str = ""


@dataclass
class FeatureData:
    """Data structure for feature information."""

    name: str = ""
    priority: str = ""
    complexity: str = ""
    description: str = ""
    acceptance_criteria: str = ""
    dependencies: str = ""


@dataclass
class Enhancement:
    """Data structure for future enhancements."""

    name: str = ""
    timeline: str = ""
    rationale: str = ""
    impact: str = ""
    prerequisites: str = ""


@dataclass
class APIEndpoint:
    """Data structure for API endpoints."""

    method: str = ""
    path: str = ""
    description: str = ""
    authentication: str = ""
    request_params: str = ""
    response_format: str = ""
    error_codes: str = ""


@dataclass
class UIComponent:
    """Data structure for UI components."""

    name: str = ""
    type: str = ""
    purpose: str = ""
    interactions: str = ""
    responsive_design: str = ""


@dataclass
class ExternalIntegration:
    """Data structure for external integrations."""

    system_name: str = ""
    type: str = ""
    protocol: str = ""
    data_exchange: str = ""
    authentication: str = ""
    error_handling: str = ""


@dataclass
class ToolOutlineSchema(BaseSchema):
    """Schema for Tool Outline deliverable."""

    tool_overview: str = ""
    tool_name: str = ""
    tool_version: str = ""
    tool_category: str = ""
    target_platforms: str = ""
    license_type: str = ""
    high_level_architecture: str = ""
    system_components: List[SystemComponent] = field(default_factory=list)
    data_flow_description: str = ""
    data_flow_diagram: str = ""
    core_features: List[FeatureData] = field(default_factory=list)
    secondary_features: List[FeatureData] = field(default_factory=list)
    future_enhancements: List[Enhancement] = field(default_factory=list)
    frontend_tech_stack: str = ""
    backend_tech_stack: str = ""
    database_tech_stack: str = ""
    infrastructure_tech_stack: str = ""
    third_party_integrations: str = ""
    minimum_requirements: str = ""
    recommended_requirements: str = ""
    performance_specifications: str = ""
    security_requirements: str = ""
    scalability_considerations: str = ""
    api_overview: str = ""
    api_endpoints: List[APIEndpoint] = field(default_factory=list)
    ui_ux_principles: str = ""
    ui_components: List[UIComponent] = field(default_factory=list)
    accessibility_requirements: str = ""
    external_integrations: List[ExternalIntegration] = field(default_factory=list)
    testing_approach: str = ""
    test_types: str = ""
    test_coverage_goals: str = ""
    testing_tools: str = ""
    deployment_environment: str = ""
    deployment_process: str = ""
    rollback_strategy: str = ""
    monitoring_logging: str = ""
    maintenance_plan: str = ""
    support_model: str = ""
    update_strategy: str = ""


@dataclass
class TaskData:
    """Data structure for implementation tasks."""

    name: str = ""
    effort: str = ""
    assigned_to: str = ""
    dependencies: str = ""
    description: str = ""
    steps: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    testing_requirements: str = ""
    documentation_requirements: str = ""


@dataclass
class RiskData:
    """Data structure for risk information."""

    name: str = ""
    probability: str = ""
    impact: str = ""
    mitigation: str = ""


@dataclass
class ImplementationPhase:
    """Data structure for implementation phases."""

    name: str = ""
    overview: str = ""
    duration: str = ""
    prerequisites: str = ""
    objectives: List[str] = field(default_factory=list)
    tasks: List[TaskData] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    quality_gates: List[str] = field(default_factory=list)
    risks: List[RiskData] = field(default_factory=list)


@dataclass
class CommonIssue:
    """Data structure for common issues."""

    name: str = ""
    symptoms: str = ""
    causes: str = ""
    resolution: str = ""
    prevention: str = ""


@dataclass
class ImplementationInstructionsSchema(BaseSchema):
    """Schema for Implementation Instructions deliverable."""

    project_overview: str = ""
    dev_environment_setup: str = ""
    required_tools: str = ""
    system_requirements: str = ""
    access_requirements: str = ""
    implementation_phases: List[ImplementationPhase] = field(default_factory=list)
    architecture_setup: str = ""
    database_setup: str = ""
    api_implementation: str = ""
    frontend_implementation: str = ""
    integration_implementation: str = ""
    security_implementation: str = ""
    environment_configuration: str = ""
    deployment_configuration: str = ""
    security_configuration: str = ""
    monitoring_configuration: str = ""
    unit_testing_implementation: str = ""
    integration_testing_implementation: str = ""
    system_testing_implementation: str = ""
    performance_testing_implementation: str = ""
    security_testing_implementation: str = ""
    user_acceptance_testing: str = ""
    development_deployment: str = ""
    staging_deployment: str = ""
    production_deployment: str = ""
    rollback_procedures: str = ""
    go_live_checklist: List[str] = field(default_factory=list)
    monitoring_setup: str = ""
    support_procedures: str = ""
    maintenance_tasks: str = ""
    knowledge_transfer: str = ""
    documentation_handover: str = ""
    common_issues: List[CommonIssue] = field(default_factory=list)
    performance_troubleshooting: str = ""
    security_troubleshooting: str = ""
    integration_troubleshooting: str = ""
    documentation_references: str = ""
    training_materials: str = ""
    external_resources: str = ""
    contact_information: str = ""


@dataclass
class SlideSection:
    """Data structure for slide sections."""

    section_name: str = ""
    slide_count: int = 0
    description: str = ""
    key_points: List[str] = field(default_factory=list)


@dataclass
class SlideData:
    """Data structure for individual slides."""

    title: str = ""
    type: str = ""
    content_requirements: str = ""
    key_messages: List[str] = field(default_factory=list)
    visual_elements: str = ""
    speaker_notes: str = ""
    transition_notes: str = ""


@dataclass
class SupplementaryPrompt:
    """Data structure for supplementary prompts."""

    title: str = ""
    content: str = ""


@dataclass
class CoPilot365PresentationSchema(BaseSchema):
    """Schema for CoPilot365 Presentation Prompt deliverable."""

    presentation_overview: str = ""
    presentation_title: str = ""
    target_audience: str = ""
    presentation_duration: str = ""
    presentation_type: str = ""
    delivery_format: str = ""
    total_slides: int = 0
    slide_sections: List[SlideSection] = field(default_factory=list)
    slides: List[SlideData] = field(default_factory=list)
    visual_theme: str = ""
    color_scheme: str = ""
    typography_guidelines: str = ""
    layout_principles: str = ""
    image_requirements: str = ""
    tone_and_voice: str = ""
    technical_level: str = ""
    key_terminology: str = ""
    messaging_framework: str = ""
    qa_sessions: str = ""
    polls_surveys: str = ""
    demonstrations: str = ""
    breakout_activities: str = ""
    handouts: str = ""
    reference_materials: str = ""
    followup_resources: str = ""
    contact_information: str = ""
    platform_specifications: str = ""
    av_requirements: str = ""
    equipment_needs: str = ""
    backup_plans: str = ""
    opening_hook: str = ""
    engagement_techniques: str = ""
    call_to_action: str = ""
    success_metrics: str = ""
    primary_prompt: str = ""
    supplementary_prompts: List[SupplementaryPrompt] = field(default_factory=list)
    revision_instructions: str = ""
    quality_checklist: List[str] = field(default_factory=list)
    pre_presentation_setup: str = ""
    presentation_flow: str = ""
    time_management: str = ""
    contingency_plans: str = ""
    followup_actions: str = ""
    feedback_collection: str = ""
    next_steps: str = ""
    post_presentation_documentation: str = ""


@dataclass
class KPIData:
    """Data structure for KPI information."""

    name: str = ""
    target: str = ""
    actual: str = ""
    status: str = ""
    variance: str = ""
    analysis: str = ""


@dataclass
class BusinessObjective:
    """Data structure for business objectives."""

    name: str = ""
    target: str = ""
    achievement: str = ""
    status: str = ""
    impact: str = ""
    evidence: str = ""


@dataclass
class MetricItem:
    """Data structure for metric items."""

    name: str = ""
    target: str = ""
    actual: str = ""
    variance: str = ""
    status: str = ""


@dataclass
class PerformanceMetric:
    """Data structure for performance metrics."""

    category: str = ""
    items: List[MetricItem] = field(default_factory=list)
    analysis: str = ""


@dataclass
class StakeholderFeedback:
    """Data structure for stakeholder feedback."""

    group: str = ""
    rating: str = ""
    strengths: str = ""
    improvements: str = ""
    comments: str = ""


@dataclass
class FeatureUtilization:
    """Data structure for feature utilization data."""

    name: str = ""
    frequency: str = ""
    adoption_rate: str = ""
    performance: str = ""
    satisfaction: str = ""
    issues: str = ""


@dataclass
class GapData:
    """Data structure for gap analysis."""

    name: str = ""
    category: str = ""
    severity: str = ""
    impact: str = ""
    root_cause: str = ""
    recommended_action: str = ""
    priority: str = ""


@dataclass
class RiskAssessment:
    """Data structure for risk assessment."""

    name: str = ""
    probability: str = ""
    impact: str = ""
    level: str = ""
    mitigation_status: str = ""
    action_required: str = ""


@dataclass
class ActionItem:
    """Data structure for action items."""

    title: str = ""
    priority: str = ""
    effort: str = ""
    timeline: str = ""
    owner: str = ""
    expected_impact: str = ""
    description: str = ""


@dataclass
class Improvement:
    """Data structure for improvements."""

    title: str = ""
    timeline: str = ""
    resources: str = ""
    benefits: str = ""
    implementation_plan: str = ""


@dataclass
class StrategicChange:
    """Data structure for strategic changes."""

    title: str = ""
    strategic_alignment: str = ""
    investment: str = ""
    expected_roi: str = ""
    timeline: str = ""
    dependencies: str = ""


@dataclass
class EffectivenessAssessmentSchema(BaseSchema):
    """Schema for Effectiveness Assessment deliverable."""

    assessment_overview: str = ""
    assessment_date: str = ""
    assessment_period: str = ""
    assessors: str = ""
    assessment_type: str = ""
    assessment_methodology: str = ""
    kpis: List[KPIData] = field(default_factory=list)
    business_objectives: List[BusinessObjective] = field(default_factory=list)
    performance_metrics: List[PerformanceMetric] = field(default_factory=list)
    usage_statistics: str = ""
    roi_analysis: str = ""
    cost_benefit_analysis: str = ""
    user_satisfaction_survey: str = ""
    user_feedback_summary: str = ""
    net_promoter_score: str = ""
    stakeholder_feedback: List[StakeholderFeedback] = field(default_factory=list)
    expert_assessment: str = ""
    feature_utilization: List[FeatureUtilization] = field(default_factory=list)
    system_performance: str = ""
    reliability_assessment: str = ""
    security_assessment: str = ""
    requirements_coverage: str = ""
    identified_gaps: List[GapData] = field(default_factory=list)
    missing_features: str = ""
    current_risks: List[RiskAssessment] = field(default_factory=list)
    emerging_risks: str = ""
    baseline_comparison: str = ""
    industry_benchmarks: str = ""
    competitive_analysis: str = ""
    business_impact: str = ""
    user_impact: str = ""
    technical_impact: str = ""
    organizational_impact: str = ""
    what_worked_well: str = ""
    what_didnt_work: str = ""
    unexpected_outcomes: str = ""
    key_insights: str = ""
    immediate_actions: List[ActionItem] = field(default_factory=list)
    short_term_improvements: List[Improvement] = field(default_factory=list)
    long_term_changes: List[StrategicChange] = field(default_factory=list)
    continuous_monitoring_plan: str = ""
    key_metrics_to_track: str = ""
    review_schedule: str = ""
    escalation_procedures: str = ""
    overall_assessment: str = ""
    success_rating: str = ""
    key_achievements: str = ""
    critical_issues: str = ""
    next_steps: str = ""
    assessment_methodology_details: str = ""
    data_sources: str = ""
    survey_instruments: str = ""
    detailed_metrics: str = ""
    assessment_team: str = ""


class PromptSchemaProcessor:
    """Main processor class for handling prompt schemas and transformations."""

    def __init__(self):
        self.schema_map = {
            DeliverableType.PROBLEM_STATEMENT: ProblemStatementSchema,
            DeliverableType.PERSONAS: PersonasSchema,
            DeliverableType.USE_CASES: UseCasesSchema,
            DeliverableType.TOOL_OUTLINE: ToolOutlineSchema,
            DeliverableType.IMPLEMENTATION_INSTRUCTIONS: ImplementationInstructionsSchema,
            DeliverableType.COPILOT365_PRESENTATION_PROMPT: CoPilot365PresentationSchema,
            DeliverableType.EFFECTIVENESS_ASSESSMENT: EffectivenessAssessmentSchema,
        }

    def parse_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Parse raw user input and extract structured information.

        Args:
            user_input: Raw text input from the user

        Returns:
            Dictionary containing parsed information
        """
        parsed_data = {
            "raw_input": user_input,
            "extracted_fields": {},
            "inferred_deliverable_type": None,
            "confidence_score": 0.0,
        }

        # Basic text processing
        cleaned_input = self._clean_input(user_input)

        # Extract key-value pairs
        extracted_fields = self._extract_key_value_pairs(cleaned_input)
        parsed_data["extracted_fields"] = extracted_fields

        # Infer deliverable type
        deliverable_type, confidence = self._infer_deliverable_type(cleaned_input)
        parsed_data["inferred_deliverable_type"] = deliverable_type
        parsed_data["confidence_score"] = confidence

        return parsed_data

    def create_schema(
        self, deliverable_type: DeliverableType, parsed_data: Dict[str, Any]
    ) -> BaseSchema:
        """
        Create a schema instance for the specified deliverable type.

        Args:
            deliverable_type: Type of deliverable to create schema for
            parsed_data: Parsed user input data

        Returns:
            Schema instance populated with available data
        """
        schema_class = self.schema_map.get(deliverable_type)
        if not schema_class:
            raise ValueError(f"Unknown deliverable type: {deliverable_type}")

        # Create instance with default values
        schema_instance = schema_class()

        # Populate with parsed data
        self._populate_schema(schema_instance, parsed_data)

        return schema_instance

    def transform_to_json_payload(
        self, deliverable_type: DeliverableType, user_input: str
    ) -> Dict[str, Any]:
        """
        Transform raw user input into a standardized JSON payload.

        Args:
            deliverable_type: Type of deliverable
            user_input: Raw user input

        Returns:
            Standardized JSON payload
        """
        # Parse user input
        parsed_data = self.parse_user_input(user_input)

        # Create schema
        schema = self.create_schema(deliverable_type, parsed_data)

        # Convert to dictionary
        payload = schema.to_dict()

        # Add metadata
        payload["_metadata"] = {
            "deliverable_type": deliverable_type.value,
            "processing_timestamp": datetime.now().isoformat(),
            "input_confidence_score": parsed_data["confidence_score"],
            "schema_version": "1.0",
        }

        return payload

    def validate_schema(self, schema: BaseSchema) -> Dict[str, Any]:
        """
        Validate a schema instance for completeness and correctness.

        Args:
            schema: Schema instance to validate

        Returns:
            Validation results
        """
        validation_results = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "completeness_score": 0.0,
        }

        schema_dict = schema.to_dict()
        total_fields = len(schema_dict)
        populated_fields = sum(
            1 for value in schema_dict.values() if value and value != "" and value != []
        )

        validation_results["completeness_score"] = (
            populated_fields / total_fields if total_fields > 0 else 0.0
        )

        # Check for required fields (basic validation)
        if hasattr(schema, "project_name") and not schema.project_name:
            validation_results["warnings"].append("Project name is empty")

        return validation_results

    def _clean_input(self, user_input: str) -> str:
        """
        Clean and normalize user input.

        Args:
            user_input: Raw user input

        Returns:
            Cleaned input string
        """
        # Remove extra whitespace
        cleaned = re.sub(r"\s+", " ", user_input.strip())

        # Normalize line endings
        cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")

        return cleaned

    def _extract_key_value_pairs(self, text: str) -> Dict[str, str]:
        """
        Extract key-value pairs from text using various patterns.

        Args:
            text: Input text to process

        Returns:
            Dictionary of extracted key-value pairs
        """
        extracted = {}

        # Pattern 1: "Key: Value" format
        pattern1 = r"([A-Za-z][A-Za-z0-9\s]+?):\s*([^\n]+)"
        matches1 = re.findall(pattern1, text)

        for key, value in matches1:
            cleaned_key = key.strip().lower().replace(" ", "_")
            extracted[cleaned_key] = value.strip()

        # Pattern 2: "Key = Value" format
        pattern2 = r"([A-Za-z][A-Za-z0-9\s]+?)\s*=\s*([^\n]+)"
        matches2 = re.findall(pattern2, text)

        for key, value in matches2:
            cleaned_key = key.strip().lower().replace(" ", "_")
            if cleaned_key not in extracted:  # Don't override pattern1 matches
                extracted[cleaned_key] = value.strip()

        return extracted

    def _infer_deliverable_type(
        self, text: str
    ) -> tuple[Optional[DeliverableType], float]:
        """
        Infer the deliverable type from the text content.

        Args:
            text: Input text to analyze

        Returns:
            Tuple of (deliverable_type, confidence_score)
        """
        text_lower = text.lower()

        # Define keywords for each deliverable type
        keywords = {
            DeliverableType.PROBLEM_STATEMENT: [
                "problem",
                "issue",
                "challenge",
                "current state",
                "pain point",
                "stakeholder",
                "constraint",
                "assumption",
                "business case",
            ],
            DeliverableType.PERSONAS: [
                "persona",
                "user",
                "customer",
                "actor",
                "role",
                "demographic",
                "behavior",
                "motivation",
                "goal",
                "frustration",
            ],
            DeliverableType.USE_CASES: [
                "use case",
                "scenario",
                "user story",
                "requirement",
                "functional",
                "precondition",
                "postcondition",
                "actor",
                "system",
            ],
            DeliverableType.TOOL_OUTLINE: [
                "tool",
                "application",
                "system",
                "software",
                "architecture",
                "component",
                "feature",
                "api",
                "interface",
                "technology",
            ],
            DeliverableType.IMPLEMENTATION_INSTRUCTIONS: [
                "implementation",
                "development",
                "deployment",
                "configuration",
                "setup",
                "installation",
                "coding",
                "programming",
                "build",
            ],
            DeliverableType.COPILOT365_PRESENTATION_PROMPT: [
                "presentation",
                "slide",
                "powerpoint",
                "copilot",
                "demo",
                "meeting",
                "audience",
                "pitch",
                "proposal",
            ],
            DeliverableType.EFFECTIVENESS_ASSESSMENT: [
                "assessment",
                "evaluation",
                "analysis",
                "performance",
                "metric",
                "kpi",
                "effectiveness",
                "success",
                "feedback",
                "review",
            ],
        }

        # Calculate scores for each deliverable type
        scores = {}
        for deliverable_type, keyword_list in keywords.items():
            score = sum(1 for keyword in keyword_list if keyword in text_lower)
            scores[deliverable_type] = score / len(keyword_list)

        # Find the best match
        if not scores or max(scores.values()) == 0:
            return None, 0.0

        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]

        return best_type, confidence

    def _populate_schema(self, schema: BaseSchema, parsed_data: Dict[str, Any]) -> None:
        """
        Populate schema fields with parsed data.

        Args:
            schema: Schema instance to populate
            parsed_data: Parsed user input data
        """
        extracted_fields = parsed_data.get("extracted_fields", {})

        # Map extracted fields to schema attributes
        for field_name, field_value in extracted_fields.items():
            if hasattr(schema, field_name):
                setattr(schema, field_name, field_value)

        # Set project name if available
        if "project_name" in extracted_fields:
            schema.project_name = extracted_fields["project_name"]
        elif "project" in extracted_fields:
            schema.project_name = extracted_fields["project"]
        elif "name" in extracted_fields:
            schema.project_name = extracted_fields["name"]


def get_schema_for_deliverable(deliverable_type: DeliverableType) -> type:
    """
    Get the schema class for a specific deliverable type.

    Args:
        deliverable_type: The deliverable type

    Returns:
        Schema class for the deliverable type
    """
    processor = PromptSchemaProcessor()
    return processor.schema_map.get(deliverable_type)


def create_empty_schema(deliverable_type: DeliverableType) -> BaseSchema:
    """
    Create an empty schema instance for a deliverable type.

    Args:
        deliverable_type: The deliverable type

    Returns:
        Empty schema instance
    """
    schema_class = get_schema_for_deliverable(deliverable_type)
    if not schema_class:
        raise ValueError(f"Unknown deliverable type: {deliverable_type}")

    return schema_class()
