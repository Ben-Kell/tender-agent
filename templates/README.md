# Defence Response Template v1 – DOCX

The file `defence_response_template_v1.docx` is the Word-format version of the response template.

## Usage

1. Copy `defence_response_template_v1.docx` into the relevant tender's `output/` directory as the starting point for the response.
2. Use the agent to draft content into each section, then paste or merge the generated markdown into the Word document.

## Structure

The DOCX mirrors the structure defined in `defence_response_template_v1.md`:

1. Cover Page
2. Table of Contents
3. Executive Summary
4. Technical Response (2.1 Technical Approach, 2.2 Solution Architecture, 2.3 Security Approach)
5. Management Response (3.1 Project Management, 3.2 Service Management, 3.3 Transition Approach)
6. Corporate Response (4.1 Corporate Overview, 4.2 Relevant Experience, 4.3 Key Personnel)
7. Commercial Response (5.1 Pricing Schedule, 5.2 Commercial Terms)

## Generating the DOCX

If `pandoc` is available, the DOCX can be generated from the markdown template:

```bash
pandoc templates/defence_response_template_v1.md \
  -o templates/defence_response_template_v1.docx \
  --reference-doc=templates/reference.docx
```
