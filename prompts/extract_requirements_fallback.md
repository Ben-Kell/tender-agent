You are extracting supplier response requirements from a tender chunk.

Focus specifically on:
- evaluation criteria
- conditions for participation
- response schedules
- pricing instructions
- staffing/resource tables
- annexures to complete
- security obligations
- compliance obligations
- mandatory plans, reports, and deliverables

Extract only concrete supplier obligations or response items.

Return valid JSON only.
Do not use markdown fences.

Return either:
- a raw JSON list
or
- {"requirements": [...]}

Each object must contain:
{
  "requirement_id": "REQ-001",
  "clause_reference": "",
  "requirement_text": "",
  "requirement_type": "mandatory",
  "response_needed": true
}