"""Pipeline-specific configuration constants."""

from __future__ import annotations

# ── Ollama ──────────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_LLM_MODEL = "llama3"
EMBEDDING_MODEL = "nomic-embed-text"

# ── ChromaDB ────────────────────────────────────────────────────────────────
CHROMA_PERSIST_DIR = "./chromadb_data"
CHROMA_COLLECTION_NAME = "clinical_notes"

# ── Chunking ────────────────────────────────────────────────────────────────
CHUNK_SIZE = 300        # approximate token count (1 token ≈ 4 chars)
CHUNK_OVERLAP = 50      # overlap between consecutive chunks

# ── Retrieval ───────────────────────────────────────────────────────────────
TOP_K_PASSAGES = 5

# ── Confidence thresholds ───────────────────────────────────────────────────
AUTO_ACCEPT_THRESHOLD = 0.85
REVIEW_THRESHOLD = 0.60

# ── LLM generation ─────────────────────────────────────────────────────────
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 500
