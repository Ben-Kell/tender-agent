You are evaluating tender compliance.

Assess the tender response against the requirement batch provided.

You must return exactly one compliance record for every requirement_id in the REQUIREMENT BATCH.
Do not omit any requirement.
Do not invent any new requirement_id.
Use the requirement_id exactly as provided.

Coverage rules:
- FULL = clearly and explicitly addressed in the final response
- PARTIAL = mentioned or partially addressed, but incomplete, weak, or ambiguous
- NONE = not addressed explicitly

Confidence rules:
- high = strong direct evidence in the response
- medium = some evidence but not complete or not clearly linked
- low = weak evidence or absent

Return valid JSON only.
Do not use markdown fences.

Return exactly this structure:

{
  "compliance": [
    {
      "requirement_id": "",
      "coverage_status": "FULL",
      "covered_in_section": "",
      "confidence": "high",
      "gap": ""
    }
  ]
}