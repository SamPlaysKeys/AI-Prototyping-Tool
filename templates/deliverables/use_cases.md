# Use Cases

## Overview
{use_cases_overview}

## Use Case Categories
{use_case_categories}

{% for use_case in use_cases %}
## Use Case {{loop.index}}: {use_case.title}

### Basic Information
- **Use Case ID**: UC-{use_case.id}
- **Priority**: {use_case.priority}
- **Complexity**: {use_case.complexity}
- **Category**: {use_case.category}
- **Status**: {use_case.status}

### Actors
#### Primary Actor(s)
{use_case.primary_actors}

#### Secondary Actor(s)
{use_case.secondary_actors}

### Description
{use_case.description}

### Preconditions
{use_case.preconditions}

### Postconditions
#### Success Postconditions
{use_case.success_postconditions}

#### Failure Postconditions
{use_case.failure_postconditions}

### Main Success Scenario
{% for step in use_case.main_scenario %}
{{loop.index}}. {step}
{% endfor %}

### Alternative Flows
{% for alt_flow in use_case.alternative_flows %}
#### Alternative Flow {loop.index}: {alt_flow.name}
**Trigger**: {alt_flow.trigger}

**Steps**:
{% for step in alt_flow.steps %}
{{loop.index}}. {step}
{% endfor %}

{% endfor %}

### Exception Flows
{% for exception in use_case.exceptions %}
#### Exception {loop.index}: {exception.name}
**Trigger**: {exception.trigger}

**Steps**:
{% for step in exception.steps %}
{{loop.index}}. {step}
{% endfor %}

{% endfor %}

### Business Rules
{use_case.business_rules}

### Non-Functional Requirements
- **Performance**: {use_case.performance_requirements}
- **Security**: {use_case.security_requirements}
- **Usability**: {use_case.usability_requirements}
- **Reliability**: {use_case.reliability_requirements}

### Acceptance Criteria
{% for criteria in use_case.acceptance_criteria %}
- {criteria}
{% endfor %}

### Dependencies
#### Depends On
{use_case.dependencies_on}

#### Depended Upon By
{use_case.depended_upon_by}

### Test Scenarios
{% for test in use_case.test_scenarios %}
#### Test Scenario {loop.index}: {test.name}
**Objective**: {test.objective}
**Steps**: {test.steps}
**Expected Result**: {test.expected_result}

{% endfor %}

---

{% endfor %}

## Use Case Relationships
{use_case_relationships}

## Traceability Matrix
{traceability_matrix}

---
*Generated on: {timestamp}*
*Project: {project_name}*
