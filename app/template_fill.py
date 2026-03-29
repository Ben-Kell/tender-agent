def fill_template_placeholders(text: str, metadata: dict) -> str:
    replacements = {
        "[RFT NUMBER]": metadata.get("tender_reference", ""),
        "[TENDER TITLE]": metadata.get("tender_title", ""),
        "[CUSTOMER NAME]": metadata.get("customer", ""),
        "[DATE]": metadata.get("submission_date", ""),
    }

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text