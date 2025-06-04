# CoPilot365 Presentation Prompt

## Presentation Overview
{presentation_overview}

## Presentation Details
- **Presentation Title**: {presentation_title}
- **Target Audience**: {target_audience}
- **Duration**: {presentation_duration}
- **Presentation Type**: {presentation_type}
- **Delivery Format**: {delivery_format}

## Slide Structure Requirements

### Total Slides
{total_slides}

### Slide Breakdown
{% for slide_section in slide_sections %}
#### {slide_section.section_name} ({slide_section.slide_count} slides)
{slide_section.description}

**Key Points to Cover**:
{% for point in slide_section.key_points %}
- {point}
{% endfor %}

{% endfor %}

## Detailed Slide Content

{% for slide in slides %}
### Slide {{loop.index}}: {slide.title}

#### Slide Type
{slide.type}

#### Content Requirements
{slide.content_requirements}

#### Key Messages
{% for message in slide.key_messages %}
- {message}
{% endfor %}

#### Visual Elements
{slide.visual_elements}

#### Speaker Notes
{slide.speaker_notes}

#### Transition Notes
{slide.transition_notes}

---

{% endfor %}

## Design Guidelines

### Visual Theme
{visual_theme}

### Color Scheme
{color_scheme}

### Typography
{typography_guidelines}

### Layout Principles
{layout_principles}

### Image and Graphics Requirements
{image_requirements}

## Content Guidelines

### Tone and Voice
{tone_and_voice}

### Technical Level
{technical_level}

### Key Terminology
{key_terminology}

### Messaging Framework
{messaging_framework}

## Interactive Elements

### Q&A Sessions
{qa_sessions}

### Polls and Surveys
{polls_surveys}

### Demonstrations
{demonstrations}

### Breakout Activities
{breakout_activities}

## Supporting Materials

### Handouts
{handouts}

### Reference Materials
{reference_materials}

### Follow-up Resources
{followup_resources}

### Contact Information
{contact_information}

## Technical Requirements

### Platform Specifications
{platform_specifications}

### Audio/Visual Requirements
{av_requirements}

### Equipment Needs
{equipment_needs}

### Backup Plans
{backup_plans}

## Audience Engagement Strategy

### Opening Hook
{opening_hook}

### Engagement Techniques
{engagement_techniques}

### Call-to-Action
{call_to_action}

### Success Metrics
{success_metrics}

## Prompt for CoPilot365

### Primary Prompt
```
{primary_prompt}
```

### Supplementary Prompts
{% for prompt in supplementary_prompts %}
#### {prompt.title}
```
{prompt.content}
```

{% endfor %}

### Revision Instructions
{revision_instructions}

### Quality Checklist
{% for item in quality_checklist %}
- [ ] {item}
{% endfor %}

## Delivery Instructions

### Pre-Presentation Setup
{pre_presentation_setup}

### Presentation Flow
{presentation_flow}

### Time Management
{time_management}

### Contingency Plans
{contingency_plans}

## Post-Presentation

### Follow-up Actions
{followup_actions}

### Feedback Collection
{feedback_collection}

### Next Steps
{next_steps}

### Documentation
{post_presentation_documentation}

---
*Generated on: {timestamp}*
*Project: {project_name}*
