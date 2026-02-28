"""RAG retrieval: embed a query and search ChromaDB for relevant passages."""

from __future__ import annotations

from dataclasses import dataclass

import chromadb

from pipeline.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    TOP_K_PASSAGES,
)
from pipeline.embedder import _embed_text


@dataclass
class RetrievedPassage:
    """A single passage retrieved from the vector store."""

    text: str
    similarity_score: float
    note_type: str
    note_id: str
    chunk_index: int


def _get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def retrieve(
    patient_id: str,
    query: str,
    top_k: int = TOP_K_PASSAGES,
) -> list[RetrievedPassage]:
    """Retrieve the most relevant passages for a query, filtered by patient."""
    col = _get_collection()

    query_embedding = _embed_text(query)

    results = col.query(
        query_embeddings=[query_embedding],
        where={"patient_id": patient_id},
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    passages: list[RetrievedPassage] = []

    if not results["ids"] or not results["ids"][0]:
        return passages

    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        # ChromaDB cosine distance → similarity = 1 - distance
        similarity = max(0.0, 1.0 - distance)
        passages.append(
            RetrievedPassage(
                text=doc,
                similarity_score=similarity,
                note_type=meta.get("note_type", "unknown"),
                note_id=meta.get("note_id", ""),
                chunk_index=int(meta.get("chunk_index", 0)),
            )
        )

    # Sort by similarity descending
    passages.sort(key=lambda p: p.similarity_score, reverse=True)
    return passages
