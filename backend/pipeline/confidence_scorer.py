"""Multi-factor confidence scoring for extractions."""

from __future__ import annotations

from dataclasses import dataclass, field

from pipeline.config import AUTO_ACCEPT_THRESHOLD, REVIEW_THRESHOLD
from pipeline.extractor import ExtractionResult
from pipeline.negation_handler import NegationResult
from pipeline.retriever import RetrievedPassage

# ── Weight configuration ────────────────────────────────────────────────────
W_RETRIEVAL = 0.30
W_ASSERTION = 0.30
W_CROSS_DOC = 0.20
W_NEGATION = 0.20

# ── Keyword sets ────────────────────────────────────────────────────────────
_DEFINITIVE_KEYWORDS = [
    "confirmed", "diagnosed with", "grade i", "grade ii", "grade iii",
    "grade iv", "grade v", "s/p", "status post", "ais ", "underwent",
    "performed", "identified", "demonstrated", "revealed",
]

_EQUIVOCAL_KEYWORDS = [
    "concern for", "possible", "cannot rule out", "questionable",
    "suspected", "likely", "probable", "may represent", "suggestive",
    "uncertain", "unclear",
]


@dataclass
class ConfidenceResult:
    """Confidence scoring result."""

    score: float
    status: str  # "auto" or "review"
    conflict_reason: str | None
    breakdown: dict


def _score_retrieval(passages: list[RetrievedPassage]) -> float:
    """Score based on average similarity of retrieved passages."""
    if not passages:
        return 0.0
    avg = sum(p.similarity_score for p in passages) / len(passages)
    # Scale: 0.0 if avg < 0.3, linearly to 1.0 if avg > 0.8
    if avg >= 0.8:
        return 1.0
    if avg <= 0.3:
        return 0.0
    return (avg - 0.3) / 0.5


def _score_assertion(extraction_result: ExtractionResult) -> float:
    """Score based on definitiveness of the citation language."""
    text = (extraction_result.citation + " " + extraction_result.value).lower()

    # Check for "not documented" / "no mention"
    if "not documented" in text or "no mention" in text:
        return 0.2

    # Check definitive keywords
    for kw in _DEFINITIVE_KEYWORDS:
        if kw in text:
            return 1.0

    # Check equivocal keywords
    for kw in _EQUIVOCAL_KEYWORDS:
        if kw in text:
            return 0.5

    # Default: moderate confidence
    return 0.7


def _score_cross_doc(passages: list[RetrievedPassage]) -> float:
    """Score based on cross-document agreement."""
    if not passages:
        return 0.0

    note_types = set(p.note_type for p in passages)
    supporting_types = len(note_types)

    if supporting_types >= 3:
        return 1.0
    if supporting_types == 2:
        return 0.7
    return 0.5


def _score_negation(negation_result: NegationResult) -> float:
    """Score based on negation consistency."""
    if negation_result.conflicts_with_extraction:
        return 0.2
    if negation_result.is_negated:
        # Negation detected but doesn't conflict (extraction says "No" and
        # negation confirms) — good consistency
        return 1.0
    if negation_result.negation_cues:
        return 0.8  # Some cues but no clear negation
    return 0.8  # Neutral — no negation cues found


def _build_conflict_reason(
    score: float,
    breakdown: dict,
    negation_result: NegationResult,
) -> str | None:
    """Generate a human-readable reason when status is 'review'."""
    if score >= AUTO_ACCEPT_THRESHOLD:
        return None

    reasons: list[str] = []

    if breakdown["retrieval"] < 0.5:
        reasons.append("Low retrieval similarity — relevant passages may not have been found")
    if breakdown["assertion"] <= 0.5:
        reasons.append("Equivocal or uncertain language in clinical text")
    if breakdown["cross_doc"] < 0.7:
        reasons.append("Limited cross-document support for this finding")
    if negation_result.conflicts_with_extraction:
        reasons.append("Negation detected in citation but extraction value is positive")

    if not reasons:
        reasons.append("Confidence below auto-accept threshold")

    return "; ".join(reasons)


def score_extraction(
    passages: list[RetrievedPassage],
    extraction_result: ExtractionResult,
    negation_result: NegationResult,
) -> ConfidenceResult:
    """Compute a multi-factor confidence score."""
    if not extraction_result.success:
        return ConfidenceResult(
            score=0.0,
            status="review",
            conflict_reason=f"Extraction failed: {extraction_result.error}",
            breakdown={"retrieval": 0, "assertion": 0, "cross_doc": 0, "negation": 0},
        )

    r = _score_retrieval(passages)
    a = _score_assertion(extraction_result)
    c = _score_cross_doc(passages)
    n = _score_negation(negation_result)

    score = round(W_RETRIEVAL * r + W_ASSERTION * a + W_CROSS_DOC * c + W_NEGATION * n, 4)

    breakdown = {
        "retrieval": round(r, 3),
        "assertion": round(a, 3),
        "cross_doc": round(c, 3),
        "negation": round(n, 3),
    }

    status = "auto" if score >= AUTO_ACCEPT_THRESHOLD else "review"
    conflict_reason = _build_conflict_reason(score, breakdown, negation_result)

    return ConfidenceResult(
        score=score,
        status=status,
        conflict_reason=conflict_reason,
        breakdown=breakdown,
    )
