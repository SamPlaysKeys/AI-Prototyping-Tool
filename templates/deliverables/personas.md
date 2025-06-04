# User Personas

## Overview
{personas_overview}

{% for persona in personas %}
## Persona {{loop.index}}: {persona.name}

### Basic Information
- **Name**: {persona.name}
- **Role/Title**: {persona.role}
- **Department**: {persona.department}
- **Experience Level**: {persona.experience_level}
- **Age Range**: {persona.age_range}

### Background
{persona.background}

### Goals and Motivations
#### Primary Goals
{persona.primary_goals}

#### Secondary Goals
{persona.secondary_goals}

#### Motivations
{persona.motivations}

### Pain Points and Challenges
#### Current Pain Points
{persona.pain_points}

#### Technical Challenges
{persona.technical_challenges}

#### Process Challenges
{persona.process_challenges}

### Technical Profile
- **Technical Expertise**: {persona.technical_expertise}
- **Preferred Tools**: {persona.preferred_tools}
- **Device Usage**: {persona.device_usage}
- **Software Familiarity**: {persona.software_familiarity}

### Behavioral Patterns
#### Work Style
{persona.work_style}

#### Communication Preferences
{persona.communication_preferences}

#### Decision Making Process
{persona.decision_making}

### Needs and Requirements
#### Functional Needs
{persona.functional_needs}

#### Non-Functional Needs
{persona.non_functional_needs}

#### Information Needs
{persona.information_needs}

### Success Metrics
{persona.success_metrics}

### Quotes
> "{persona.quote}"

---

{% endfor %}

## Persona Relationships
{persona_relationships}

## Design Implications
{design_implications}

---
*Generated on: {timestamp}*
*Project: {project_name}*
