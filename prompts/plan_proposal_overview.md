You are analysing extracted tender evaluation criteria and deciding which ones should be answered in the Proposal Overview document.

Your task is to:

1. Identify the evaluation criteria that belong in the Proposal Overview.
2. Group those criteria into sensible Proposal Overview section headings.
3. Identify which evaluation criteria should instead be answered in another submission document such as:
   - pricing workbook or quote
   - past performance document
   - AIC plan
   - returnable schedules
   - CVs / key personnel attachments
   - compliance schedules
4. Return a structured JSON plan.

Rules:
- Proposal Overview should contain narrative sections such as:
  - understanding of requirements
  - solution overview
  - service delivery approach
  - methodology
  - transition-in / implementation approach
  - governance / management approach
  - risk / quality / assurance approach
  - innovation / value-add
  - key staff / capability overview
- Do NOT place pure pricing response criteria into Proposal Overview if they are clearly answered by pricing workbook / quote.
- Do NOT place pure past performance / references criteria into Proposal Overview if they are clearly answered in a separate past performance document.
- Do NOT place pure returnable form / schedule completion criteria into Proposal Overview.
- If a criterion should be mentioned briefly in Proposal Overview but fully answered elsewhere, you may put it into:
  "proposal_overview_sections" with a note that detailed response is covered elsewhere.
- Prefer practical, document-ready headings.
- Each heading should be concise and suitable to appear as a Proposal Overview heading.
- Return valid JSON only.
- Do not include markdown fences.

Return JSON in exactly this shape:

{
  "proposal_overview_sections": [
    {
      "heading": "string",
      "criteria_ids": ["string"],
      "criteria_titles": ["string"],
      "reason": "string"
    }
  ],
  "covered_elsewhere": [
    {
      "criteria_ids": ["string"],
      "criteria_titles": ["string"],
      "document": "pricing_workbook_or_quote | past_performance_document | aic_plan | returnable_schedule | cvs_or_key_personnel | compliance_schedule | other_attachment",
      "reason": "string"
    }
  ],
  "overall_summary": "string"
}