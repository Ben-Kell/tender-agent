# Extract Requirements Prompt

## Task

Parse the provided tender document(s) and extract all requirements into a structured list.

## Instructions

1. Read through the entire tender document, including all annexes and addenda.
2. Identify and categorise each requirement as:
   - **Mandatory** – must be addressed for the response to be considered compliant
   - **Desirable** – should be addressed to maximise evaluation score
   - **Informational** – context that informs the response but requires no direct answer
3. For each requirement, capture:
   - Clause/section reference
   - Requirement text (verbatim or paraphrased)
   - Category (Mandatory / Desirable / Informational)
   - Evaluation criterion it maps to (if stated)
4. Output the requirements as a structured markdown table or JSON object.

## Output Format

```json
[
  {
    "id": "REQ-001",
    "clause": "3.1.2",
    "text": "The respondent must demonstrate...",
    "category": "Mandatory",
    "evaluation_criterion": "Technical Capability"
  }
]
```
