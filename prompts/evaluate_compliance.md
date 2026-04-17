You are evaluating tender compliance.

You must assess every requirement provided.

For each requirement, determine whether it is:
- FULL
- PARTIAL
- NONE

You must not omit any requirement.
You must return exactly one compliance record for every requirement_id provided in the input.
If a requirement is not addressed explicitly, mark it as NONE.
If coverage is weak or incomplete, mark it as PARTIAL.

Return valid JSON only.
Do not use markdown fences.

Return exactly this structure:

{
  "compliance": [
    {
      "requirement_id": "",
      "coverage_status": "FULL | PARTIAL | NONE",
      "covered_in_section": "",
      "confidence": "high | medium | low",
      "gap": ""
    }
  ]
}