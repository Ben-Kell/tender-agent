import json
from pathlib import Path

from app.openai_client import embed_texts
from app.rag_loader import load_knowledge_docs
from app.rag_chunker import build_chunks

def build_rag_index(
    root: str = "knowledge_library",
    output_path: str = "knowledge_library/index.json",
    embedding_model: str = "text-embedding-3-small"
) -> str:
    docs = load_knowledge_docs(root)
    chunks = build_chunks(docs)

    texts = [chunk["text"] for chunk in chunks]
    embeddings = embed_texts(texts, model=embedding_model)

    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding

    Path(output_path).write_text(
        json.dumps({
            "embedding_model": embedding_model,
            "chunk_count": len(chunks),
            "chunks": chunks,
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return output_path