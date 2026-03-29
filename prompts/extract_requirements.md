Extract tender metadata and all supplier response requirements from the tender documents.

You must return these metadata fields exactly:
- tender_reference
- tender_title
- customer
- submission_date

Rules for metadata:
- Use exact wording from the tender where possible.
- Do not guess.
- If a value is not clearly available, return an empty string.
- Put all metadata inside a top-level object named "metadata".

Rules for requirements:
- Capture mandatory obligations, evaluation response requirements, pricing requirements, security requirements, personnel requirements, plans, reporting, governance, AIC, compliance, and deliverables.
- Preserve clause references where possible.
- Do not summarise requirements into vague wording.
- Break combined obligations into separate requirements where practical.
- requirement_type must be one of: mandatory, response, commercial, security, personnel, governance, technical.
- Set response_needed to true where the supplier must address the point in the tender response.

Return only valid JSON matching the structure requested by the caller.