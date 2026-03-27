# Map Template Prompt

## Task

Map each extracted requirement to the appropriate section of the response template.

## Instructions

1. Review the list of extracted requirements (output of `extract_requirements`).
2. Review the response template structure (see `templates/defence_response_template_v1.md`).
3. For each requirement, identify the most appropriate template section to address it.
4. Where a requirement spans multiple sections, create a mapping entry for each relevant section.
5. Flag any requirements that do not map clearly to an existing template section.

## Output Format

```json
[
  {
    "requirement_id": "REQ-001",
    "template_section": "2.1 Technical Approach",
    "notes": "Address the capability demonstration here with supporting evidence."
  }
]
```
