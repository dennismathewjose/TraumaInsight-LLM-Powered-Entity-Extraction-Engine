"""Chunk clinical notes and embed into ChromaDB via Ollama nomic-embed-text."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import chromadb
import requests
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

# Ensure backend/ is on sys.path so we can import app.models
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings  # noqa: E402
from app.database import Base  # noqa: E402
from app.models.clinical_note import ClinicalNote  # noqa: E402
from pipeline.config import (  # noqa: E402
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
)

# ── Helpers ─────────────────────────────────────────────────────────────────

_CHARS_PER_TOKEN = 4  # rough approximation


def _get_sync_engine():
    settings = get_settings()
    return create_engine(settings.sync_database_url, echo=False)


def _get_chroma_collection():
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks on sentence boundaries."""
    # Split on sentence endings
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if not sentences:
        return [text] if text.strip() else []

    chunk_char_limit = CHUNK_SIZE * _CHARS_PER_TOKEN
    overlap_chars = CHUNK_OVERLAP * _CHARS_PER_TOKEN

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_len = 0

    for sentence in sentences:
        s_len = len(sentence)
        if current_len + s_len > chunk_char_limit and current_chunk:
            chunks.append(" ".join(current_chunk))
            # Overlap: keep trailing sentences that fit within overlap budget
            overlap_chunk: list[str] = []
            overlap_len = 0
            for s in reversed(current_chunk):
                if overlap_len + len(s) > overlap_chars:
                    break
                overlap_chunk.insert(0, s)
                overlap_len += len(s)
            current_chunk = overlap_chunk
            current_len = overlap_len

        current_chunk.append(sentence)
        current_len += s_len

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def _embed_text(text: str) -> list[float]:
    """Embed a single text string using Ollama nomic-embed-text."""
    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/embed",
        json={"model": EMBEDDING_MODEL, "input": text},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["embeddings"][0]


# ── Public API ──────────────────────────────────────────────────────────────


def is_patient_embedded(patient_id: str) -> bool:
    """Check if any embeddings exist for this patient."""
    col = _get_chroma_collection()
    results = col.get(where={"patient_id": patient_id}, limit=1)
    return len(results["ids"]) > 0


def clear_patient_embeddings(patient_id: str) -> int:
    """Delete all embeddings for a patient. Returns count deleted."""
    col = _get_chroma_collection()
    existing = col.get(where={"patient_id": patient_id})
    ids = existing["ids"]
    if ids:
        col.delete(ids=ids)
    return len(ids)


def embed_patient(patient_id: str, force: bool = False) -> int:
    """Embed all clinical notes for one patient. Returns chunk count."""
    if not force and is_patient_embedded(patient_id):
        print(f"  Patient {patient_id} already embedded — skipping (use force=True to re-embed)")
        return 0

    if force:
        clear_patient_embeddings(patient_id)

    engine = _get_sync_engine()
    col = _get_chroma_collection()

    with Session(engine) as session:
        notes = session.execute(
            select(ClinicalNote).where(ClinicalNote.patient_id == patient_id)
        ).scalars().all()

    if not notes:
        print(f"  No clinical notes found for {patient_id}")
        return 0

    total_chunks = 0
    for note in notes:
        chunks = _chunk_text(note.content)
        for i, chunk_text in enumerate(chunks):
            doc_id = f"{note.id}_{i}"
            embedding = _embed_text(chunk_text)
            col.upsert(
                ids=[doc_id],
                documents=[chunk_text],
                embeddings=[embedding],
                metadatas=[{
                    "patient_id": patient_id,
                    "note_id": note.id,
                    "note_type": note.note_type,
                    "chunk_index": i,
                }],
            )
            total_chunks += 1

    print(f"  Embedded {total_chunks} chunks from {len(notes)} notes for {patient_id}")
    return total_chunks


def embed_all_patients() -> dict:
    """Embed clinical notes for all patients. Returns summary."""
    engine = _get_sync_engine()
    with Session(engine) as session:
        patient_ids = session.execute(
            select(ClinicalNote.patient_id).distinct()
        ).scalars().all()

    total = 0
    for pid in patient_ids:
        total += embed_patient(pid)

    return {"patients": len(patient_ids), "total_chunks": total}
