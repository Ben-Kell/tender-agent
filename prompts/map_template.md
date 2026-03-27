# Map Template Prompt

## Purpose

Map each extracted requirement to the appropriate section of the response template so that every requirement is addressed exactly once.

## Inputs

- Structured requirements list produced by `extract_requirements.md`.
- Response template structure (see `templates/defence_response_template_v1.md`).

## Instructions

1. Review the response template section headings and their stated purposes.
2. For each requirement ID, identify the single best-fit template section.
3. Where a requirement spans multiple sections, assign it to the primary section and add cross-references.
4. Identify any template sections that have no mapped requirements and flag them as `UNUSED`.
5. Identify any requirements that do not map cleanly to any section and flag them as `UNMAPPED`.

## Output Format

Produce two artefacts:

### 1. Requirement-to-Section Mapping Table

```markdown
| Req ID | Requirement Summary | Template Section | Notes |
|--------|---------------------|------------------|-------|
| REQ-001 | ... | 3.2 Technical Approach | — |
```

### 2. Section Coverage Summary

```markdown
| Section | Title | Mapped Requirements | Status |
|---------|-------|---------------------|--------|
| 3.2 | Technical Approach | REQ-001, REQ-005 | ✅ Covered |
| 4.1 | Pricing Schedule | — | ⚠️ UNUSED |
```

## Constraints

- Every mandatory requirement must be mapped; raise an error if any are left unmapped.
- Do not create new template sections; work within the existing structure.
