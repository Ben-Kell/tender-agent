# QA Review Prompt

## Purpose

Perform a comprehensive quality-assurance review of the drafted response before final submission.

## Inputs

- Drafted response document from `draft_sections.md`.
- Original requirements list from `extract_requirements.md`.
- Response template from `templates/defence_response_template_v1.md`.
- RFT submission instructions.

## Review Checklist

### 1. Compliance Check
- [ ] Every mandatory requirement has a dedicated response.
- [ ] Responses use compliant language (e.g., "We confirm…", "We will…").
- [ ] No requirements have been omitted or only partially addressed.
- [ ] Addendum changes are reflected; superseded text is not used.

### 2. Content Quality
- [ ] Claims are supported by evidence or case study references.
- [ ] No fabricated facts, statistics, or credentials are present.
- [ ] Boilerplate has been contextualised to the specific RFT (no generic filler left in).
- [ ] All `[DRAFT NOTE]` placeholders have been resolved or escalated.

### 3. Formatting & Structure
- [ ] Document follows the required template structure exactly.
- [ ] Section numbering matches the template.
- [ ] Word and page limits are respected for each section.
- [ ] Tables, figures, and appendices are correctly labelled and referenced.

### 4. Language & Style
- [ ] Grammar and spelling are correct (Australian English).
- [ ] Tone is professional, formal, and consistent throughout.
- [ ] Acronyms are defined on first use.
- [ ] No sensitive or classified information is included unless explicitly permitted.

### 5. Administrative
- [ ] Cover page, executive summary, and table of contents are complete.
- [ ] Version number and date are current.
- [ ] All required appendices are attached.
- [ ] Authorisation and signature blocks are present.

## Output Format

Produce a QA report with the following sections:

```markdown
## QA Summary
- Overall Status: PASS | FAIL | CONDITIONAL PASS
- Issues Found: <count>
- Critical Issues: <count>

## Issues Log

| # | Severity | Section | Description | Recommended Action |
|---|----------|---------|-------------|-------------------|
| 1 | Critical | 3.2 | REQ-007 not addressed | Add paragraph confirming … |
```

## Constraints

- A response with any unresolved Critical issues must not be submitted.
- Escalate issues that require subject-matter expert input rather than attempting to resolve them autonomously.
