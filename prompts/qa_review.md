# QA Review Prompt

## Task

Perform a quality assurance review of the drafted tender response against the original requirements and evaluation criteria.

## Checklist

### Compliance
- [ ] All mandatory requirements are addressed
- [ ] Response follows the format and length restrictions specified in the tender
- [ ] All requested attachments and certifications are referenced or included
- [ ] Pricing is consistent with the statement of work (if applicable)

### Quality
- [ ] Each section directly responds to the stated requirement
- [ ] Claims are substantiated with evidence, data, or case study references
- [ ] No contradictions or inconsistencies between sections
- [ ] Tone is professional and consistent throughout
- [ ] No unexpanded `[PLACEHOLDER]` tags remain

### Risk Flags
- Note any sections that make unsubstantiated claims
- Note any requirements that have only been partially addressed
- Note any evaluation criteria that appear under-weighted

## Output Format

Return a structured review report listing:
1. Passed checks
2. Failed checks with remediation notes
3. Risk flags requiring human review
