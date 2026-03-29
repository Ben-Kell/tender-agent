def fill_template_placeholders(template_text: str, metadata: dict) -> str:
    replacements = {
        "[RFT NUMBER]": metadata.get("tender_reference", ""),
        "[TENDER TITLE]": metadata.get("tender_title", ""),
        "[CUSTOMER NAME]": metadata.get("customer", ""),
        "[ABN]": metadata.get("abn", ""),
        "[DATE]": metadata.get("submission_date", ""),
    }

    for placeholder, value in replacements.items():
        template_text = template_text.replace(placeholder, str(value))

    return template_text