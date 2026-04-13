from typing import List


def split_text_into_chunks(text: str, max_chars: int = 12000, overlap: int = 1000) -> List[str]:
    """
    Splits long text into overlapping chunks.
    Uses character count as a simple approximation to stay safely under token limits.
    """
    if not text:
        return []

    text = text.strip()
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + max_chars, text_length)
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = max(0, end - overlap)

    return chunks