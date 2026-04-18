from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class RagChunk:
    chunk_id: str
    source_file: str
    source_path: str
    category: str
    title: str
    text: str
    metadata: dict[str, Any]
    embedding: list[float] | None = None

    def to_dict(self) -> dict:
        return asdict(self)