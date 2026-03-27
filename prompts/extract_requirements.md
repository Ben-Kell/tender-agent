# Extract Requirements Prompt

## Purpose

Parse all tender documents for this RFT and produce a structured, numbered list of requirements.

## Instructions

1. Read every provided document: the main RFT, all annexes, and any addenda.
2. For each requirement found, record the following fields:
   - **ID** – A unique identifier (e.g., `REQ-001`).
   - **Source** – Document name and section/clause number.
   - **Type** – `Mandatory` | `Desirable` | `Information`.
   - **Summary** – A one-sentence description of what is required.
   - **Full Text** – The verbatim requirement text from the document.
   - **Evaluation Criterion** – The associated evaluation criterion, if stated.
   - **Word/Page Limit** – Any limit specified for the response to this requirement.
   - **Notes** – Any ambiguities or items requiring human clarification.

3. Organise requirements into the following categories:
   - Technical Requirements
   - Management & Governance
   - Security & Compliance
   - Transition & Implementation
   - Pricing & Commercial
   - General / Administrative

4. Output a Markdown table for each category.

## Output Format

```markdown
## [Category Name]

| ID | Source | Type | Summary | Limit | Notes |
|----|--------|------|---------|-------|-------|
| REQ-001 | RFT §3.1 | Mandatory | ... | 500 words | — |
```

## Constraints

- Do not paraphrase mandatory requirements; preserve exact wording.
- If a requirement appears in both the RFT and an addendum, use the addendum version and note the supersession.
- Flag any contradictory requirements with a `⚠️ CONFLICT` note.
