"""Citation builder — clean and verify LLM citations against source passages."""

from __future__ import annotations

from difflib import SequenceMatcher

from pipeline.extractor import ExtractionResult
from pipeline.retriever import RetrievedPassage


def _best_match_score(needle: str, haystack: str) -> float:
    """Fuzzy substring match score between needle and haystack."""
    if not needle or not haystack:
        return 0.0
    return SequenceMatcher(None, needle.lower(), haystack.lower()).ratio()


def build_citation(
    extraction_result: ExtractionResult,
    passages: list[RetrievedPassage],
) -> tuple[str, str]:
    """Clean the LLM citation and identify its source note type.

    Returns (citation_text, source_note_type).
    """
    if not passages:
        return (extraction_result.citation.strip() or "No source passages", "unknown")

    raw_citation = extraction_result.citation.strip()

    if not raw_citation:
        # No citation produced — use best passage
        best = passages[0]
        snippet = best.text[:300].strip()
        return (snippet, best.note_type)

    # Try to match the citation against each passage
    best_score = 0.0
    best_passage = passages[0]

    for p in passages:
        score = _best_match_score(raw_citation, p.text)
        if score > best_score:
            best_score = score
            best_passage = p

    if best_score >= 0.3:
        # Good enough match — use the cleaned citation
        return (raw_citation, best_passage.note_type)

    # Hallucinated citation — fall back to the best passage text
    snippet = best_passage.text[:300].strip()
    return (snippet, best_passage.note_type)
