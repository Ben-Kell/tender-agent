You are extracting labour roles for a staff augmentation / time-and-materials tender.

Your task is to identify only the role-based pricing requirements requested by the tender.

Extract each requested role into structured JSON.

Important rules:
- Only extract roles that are actually requested by the tender.
- Ignore example text, background text, and supplier capability text.
- Prefer role tables, pricing schedules, annexures, labour category tables, and staffing requirement sections.
- If quantity is stated like "x 3", extract quantity = 3.
- If SFIA code is stated, extract it exactly.
- If SFIA level is stated, extract the number only.
- If security clearance is stated, extract it.
- If the pricing unit required by the tender is stated, extract it as "day" or "hour".
- If contract duration is stated, extract:
  - duration_years
  - duration_months
- If duration is not stated, leave as null.
- Return valid JSON only.
- No markdown fences.

Return exactly this structure:

{
  "tender_roles": [
    {
      "tender_role_name": "",
      "sfia_code": "",
      "sfia_level": null,
      "quantity": 1,
      "clearance": "",
      "pricing_unit_required": "",
      "duration_years": null,
      "duration_months": null,
      "source_snippet": ""
    }
  ]
}