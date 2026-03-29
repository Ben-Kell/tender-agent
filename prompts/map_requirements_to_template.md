# Map Template Prompt

Map extracted tender requirements to the most appropriate sections of the response template.

Rules:
- Use the template section names exactly where possible.
- Group requirements logically under the best matching section.
- If a requirement does not clearly fit an existing section, propose headings_to_add.
- Do not lose any requirements.
- A requirement can appear in only one primary section unless duplication is essential.
- response_guidance should explain what the writer needs to cover in that section.
- section_purpose should briefly describe why the section exists.
- Return raw JSON only.
- Do not use markdown fences.