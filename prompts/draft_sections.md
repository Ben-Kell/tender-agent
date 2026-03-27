# Draft Sections Prompt

## Purpose

Draft the content for each section of the response template, addressing all mapped requirements.

## Inputs

- Requirement-to-section mapping table from `map_template.md`.
- Full requirements list from `extract_requirements.md`.
- Boilerplate content from `boilerplate/`.
- Relevant case studies from `case_studies/`.
- Response template structure from `templates/defence_response_template_v1.md`.

## Instructions

For each template section, in order:

1. List the requirements mapped to this section.
2. Identify any applicable boilerplate content and insert it as a starting point.
3. Identify any relevant case studies and summarise how they demonstrate the required capability.
4. Draft the section response, ensuring:
   - Every mapped requirement is explicitly addressed.
   - The response is written in first-person plural ("we", "our").
   - Claims are supported by evidence (statistics, case study outcomes, accreditations).
   - Any specified word or page limit is respected.
   - Headings and formatting follow the template structure.
5. Add a `[DRAFT NOTE]` comment where human review or additional input is needed.

## Output Format

Produce a complete draft of the response document in Markdown, following the template structure exactly. Include the following metadata block at the top:

```markdown
---
rft: <RFT reference>
version: DRAFT 0.1
date: <ISO date>
status: For Review
---
```

## Constraints

- Do not invent facts, certifications, or statistics not found in the boilerplate or case studies.
- Preserve mandatory requirement wording when confirming compliance (e.g., "We confirm that…").
- Keep each section self-contained; do not assume the evaluator will read other sections.
