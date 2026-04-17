You are extracting supplier response requirements from a tender document chunk.

Extract only requirement records from the text provided.
Do NOT extract metadata.
Do NOT return a metadata object.
Do NOT return commentary.

Capture:
- mandatory obligations
- response requirements
- evaluation criteria response requirements
- pricing/commercial requirements
- security requirements
- personnel requirements
- governance/reporting requirements
- technical requirements
- plans, schedules, and deliverables the supplier must provide

Rules:
- Preserve clause references where possible.
- Preserve the wording of the requirement as closely as possible.
- Break combined obligations into separate requirement records where practical.
- Ignore background/context text that does not impose a supplier obligation or response need.
- If the text includes evaluation criteria, submission instructions, response schedules, annexures to be completed, pricing instructions, staffing tables, compliance statements, or mandatory plans, extract them.
- requirement_type must be one of:
  mandatory, response, commercial, security, personnel, governance, technical
- response_needed must be true if Fujitsu needs to address it in the response, submit something for it, price it, or comply with it.

Return valid JSON only.
Do not use markdown fences.

Return either:
1) a raw JSON list of requirement objects
or
2) an object with a top-level "requirements" list

Each requirement object must use this shape:

{
  "requirement_id": "REQ-001",
  "clause_reference": "",
  "requirement_text": "",
  "requirement_type": "mandatory",
  "response_needed": true
}