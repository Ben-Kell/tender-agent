You are analysing tender documents to identify the overall contracting mechanism / pricing model.

You must classify the tender into one of the following categories:

1. staff_augmentation_time_and_materials
   Use this when the tender is primarily for labour hire, staff augmentation, panel resources, role-based supply, time-and-materials billing, hourly/daily rates, named labour categories, or provision of individual personnel.

2. managed_service_fixed_price
   Use this when the tender is primarily for an outcome-based service, managed service, bundled service delivery, fixed monthly charges, fixed price service delivery, SLA-based delivery, or responsibility for delivering a service rather than just supplying personnel.

3. mixed_or_unclear
   Use this when the documents genuinely indicate a hybrid pricing structure, multiple pricing models, or insufficient evidence to confidently classify as either of the above.

Important instructions:
- Focus on the dominant commercial structure of the tender.
- Do not classify based on one isolated phrase alone.
- Prefer explicit pricing schedules, rate cards, labour categories, service descriptions, deliverables, SLAs, pricing instructions, and contract clauses.
- If both models appear, decide whether one is clearly dominant. If not, return mixed_or_unclear.
- Quote short evidence snippets from the source text.
- Return valid JSON only.
- Do not include markdown fences.

Return JSON in exactly this shape:

{
  "pricing_model": "staff_augmentation_time_and_materials | managed_service_fixed_price | mixed_or_unclear",
  "confidence": "high | medium | low",
  "summary": "short plain-English summary",
  "primary_evidence": [
    "short evidence snippet 1",
    "short evidence snippet 2",
    "short evidence snippet 3"
  ],
  "secondary_indicators": [
    "indicator 1",
    "indicator 2"
  ],
  "reasoning": "brief explanation of why this classification was selected"
}