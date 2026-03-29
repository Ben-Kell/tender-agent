Extract all explicit and implied supplier response requirements from the tender documents.

Include:
- mandatory obligations
- response requirements
- pricing requirements
- personnel requirements
- security requirements
- governance requirements
- reporting requirements
- plan requirements
- AIC requirements
- technical and delivery requirements

Rules:
- Preserve clause references where possible.
- Use the source filename where possible.
- Break combined obligations into separate requirements where practical.
- requirement_type must be one of:
  mandatory, response, commercial, security, personnel, governance, technical
- response_needed should be true if the supplier needs to address it in the tender response.