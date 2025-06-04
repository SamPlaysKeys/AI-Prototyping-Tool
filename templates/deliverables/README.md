# Deliverable Templates

This directory contains structured Markdown templates for generating various project deliverables. Each template uses Jinja2 templating syntax and is designed to work with the corresponding schema definitions in the prompt schema module.

## Available Templates

### 1. Problem Statement (`problem_statement.md`)
Generates a comprehensive problem statement document including:
- Executive summary
- Problem overview and impact analysis
- Business context and stakeholders
- Success criteria and constraints
- Timeline and milestones

### 2. Personas (`personas.md`)
Creates detailed user persona documentation including:
- Individual persona profiles
- Background and demographics
- Goals, motivations, and pain points
- Technical profiles and behavioral patterns
- Relationships between personas

### 3. Use Cases (`use_cases.md`)
Produces structured use case documentation with:
- Use case categories and relationships
- Detailed scenarios with actors
- Main and alternative flows
- Exception handling
- Business rules and acceptance criteria
- Test scenarios and traceability matrix

### 4. Tool Outline (`tool_outline.md`)
Generates comprehensive tool/system specifications including:
- Architecture overview and components
- Feature set and technical specifications
- API design and UI/UX guidelines
- Integration points and testing strategy
- Deployment and maintenance plans

### 5. Implementation Instructions (`implementation_instructions.md`)
Creates detailed implementation guidance with:
- Prerequisites and environment setup
- Phased implementation approach
- Technical implementation details
- Configuration management
- Testing and deployment instructions
- Troubleshooting guide

### 6. CoPilot365 Presentation Prompt (`copilot365_presentation_prompt.md`)
Produces presentation specification documents including:
- Slide structure and content requirements
- Design guidelines and visual elements
- Interactive elements and engagement strategy
- Technical requirements and delivery instructions
- Specific prompts for CoPilot365

### 7. Effectiveness Assessment (`effectiveness_assessment.md`)
Generates comprehensive assessment documentation with:
- Success metrics and KPIs
- Quantitative and qualitative analysis
- Gap analysis and risk assessment
- Impact assessment and lessons learned
- Recommendations and future monitoring

## Template Syntax

The templates use Jinja2 syntax with the following conventions:

### Basic Variable Substitution
```markdown
# {project_name}

## Overview
{project_overview}
```

### Conditional Content
```markdown
{% if feature_list %}
## Features
{% for feature in feature_list %}
- {feature.name}: {feature.description}
{% endfor %}
{% endif %}
```

### Lists and Loops
```markdown
{% for persona in personas %}
## Persona {{loop.index}}: {persona.name}

### Background
{persona.background}

{% endfor %}
```

### Complex Data Structures
```markdown
{% for phase in implementation_phases %}
## Phase {{loop.index}}: {phase.name}

### Tasks
{% for task in phase.tasks %}
#### Task {{loop.index}}: {task.name}
- **Effort**: {task.effort}
- **Description**: {task.description}

##### Steps
{% for step in task.steps %}
{{loop.index}}. {step}
{% endfor %}

{% endfor %}
{% endfor %}
```

## Usage

### Using the Template Renderer

```python
from src.template_renderer import TemplateRenderer
from src.prompt_schema import DeliverableType, create_empty_schema

# Initialize renderer
renderer = TemplateRenderer()

# Create and populate schema
schema = create_empty_schema(DeliverableType.PROBLEM_STATEMENT)
schema.project_name = "My Project"
schema.executive_summary = "This project aims to..."

# Render template
rendered_content = renderer.render_deliverable(
    DeliverableType.PROBLEM_STATEMENT,
    schema
)

# Save to file
renderer.save_rendered_deliverable(
    DeliverableType.PROBLEM_STATEMENT,
    schema,
    "output/problem_statement.md"
)
```

### Using Convenience Functions

```python
from src.template_renderer import render_deliverable_from_input
from src.prompt_schema import DeliverableType

# Generate from user input
user_input = """
Project: AI Chatbot Development
Problem: Customer service efficiency is low
Stakeholders: Customer service team, IT department
Goal: Reduce response time by 50%
"""

rendered_md = render_deliverable_from_input(
    DeliverableType.PROBLEM_STATEMENT,
    user_input
)

print(rendered_md)
```

### Generating Multiple Deliverables

```python
from src.template_renderer import create_deliverable_package

user_input = """
Project: E-commerce Platform Redesign
Problem: Current platform has poor user experience
Users: Online shoppers, store administrators
Goals: Improve conversion rate, simplify management
"""

results = create_deliverable_package(
    user_input=user_input,
    output_dir="./deliverables",
    selected_deliverables=[
        DeliverableType.PROBLEM_STATEMENT,
        DeliverableType.PERSONAS,
        DeliverableType.USE_CASES
    ]
)

print(f"Generated {len(results['generated'])} deliverables")
print(f"Failed: {len(results['failed'])} deliverables")
```

## Template Validation

To validate templates and check for issues:

```python
from src.template_renderer import TemplateRenderer
from src.prompt_schema import DeliverableType

renderer = TemplateRenderer()

# Validate specific template
validation = renderer.validate_template(DeliverableType.PROBLEM_STATEMENT)
print(f"Template valid: {validation['is_valid']}")

# Get available templates
available = renderer.get_available_templates()
print(f"Available templates: {list(available.keys())}")

# Preview template variables
variables = renderer.preview_template_variables(DeliverableType.PERSONAS)
print(f"Template has {variables['total_variables']} variables")
```

## Customization

### Adding New Templates

1. Create a new template file in this directory
2. Update the `template_map` in `TemplateRenderer`
3. Create corresponding schema in `prompt_schema.py`
4. Add the new deliverable type to the `DeliverableType` enum

### Modifying Existing Templates

- Templates can be edited directly
- Use Jinja2 syntax for dynamic content
- Ensure variable names match schema field names
- Test changes with the validation functions

### Template Best Practices

1. **Consistent Structure**: Follow the established pattern of headers and sections
2. **Conditional Content**: Use `{% if %}` blocks for optional sections
3. **Default Values**: Provide meaningful placeholders for empty fields
4. **Documentation**: Include comments in complex template logic
5. **Validation**: Test templates with both full and minimal data

## Schema Integration

Each template is designed to work with a specific schema class:

- `problem_statement.md` ↔ `ProblemStatementSchema`
- `personas.md` ↔ `PersonasSchema`
- `use_cases.md` ↔ `UseCasesSchema`
- `tool_outline.md` ↔ `ToolOutlineSchema`
- `implementation_instructions.md` ↔ `ImplementationInstructionsSchema`
- `copilot365_presentation_prompt.md` ↔ `CoPilot365PresentationSchema`
- `effectiveness_assessment.md` ↔ `EffectivenessAssessmentSchema`

The schema classes define the structure and data types for all template variables, ensuring type safety and providing validation capabilities.

## Error Handling

Common template errors and solutions:

### Template Not Found
```
FileNotFoundError: Template file not found
```
**Solution**: Ensure template file exists in the correct directory

### Variable Not Found
```
UndefinedError: 'variable_name' is undefined
```
**Solution**: Check schema field names match template variables

### Syntax Error
```
TemplateSyntaxError: unexpected char
```
**Solution**: Validate Jinja2 syntax, especially loop and conditional blocks

### Type Error
```
TypeError: argument of type 'NoneType' is not iterable
```
**Solution**: Use conditional blocks around list iterations

## Dependencies

The template system requires:

- `jinja2` for template processing
- `dataclasses` for schema definitions
- `pathlib` for file handling
- `typing` for type hints

Install dependencies:
```bash
pip install jinja2
```

## Contributing

When contributing new templates or modifications:

1. Follow the existing naming conventions
2. Include comprehensive documentation
3. Test with various data scenarios
4. Update this README if adding new template types
5. Ensure backward compatibility with existing schemas
