# tender-agent

An AI-assisted tender response agent for government and defence procurement.

## Repository Structure

```
tender-agent/
  prompts/                        # LLM prompt templates for each agent step
    system_instructions.md        # Base system prompt / agent persona
    extract_requirements.md       # Extract and categorise requirements from tender docs
    map_template.md               # Map requirements to response template sections
    draft_sections.md             # Draft response content per section
    qa_review.md                  # Quality assurance review checklist
  templates/                      # Response document templates
    defence_response_template_v1.md   # Markdown response template
    defence_response_template_v1.docx # Word response template (add manually – see templates/README.md)
  boilerplate/                    # Reusable content blocks
    corporate_overview.md
    security_capability.md
    service_management.md
    transition_approach.md
  case_studies/                   # Reference case studies for past experience sections
    nds_case_study.md
    dict_case_study.md
  tenders/                        # Per-tender working directories
    RFT-123/
      input/                      # Source tender documents (PDF/DOCX – not committed)
      output/                     # Generated response documents
```

## Getting Started

1. Place tender documents in `tenders/<RFT-ID>/input/`.
2. Use the prompts in `prompts/` to guide the agent through:
   - Extracting requirements (`extract_requirements.md`)
   - Mapping requirements to the template (`map_template.md`)
   - Drafting response sections (`draft_sections.md`)
   - Reviewing the draft (`qa_review.md`)
3. Review and finalise the output in `tenders/<RFT-ID>/output/`.