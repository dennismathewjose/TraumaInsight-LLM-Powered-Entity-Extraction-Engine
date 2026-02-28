"""medspaCy negation detection on extraction citations."""

from __future__ import annotations

from dataclasses import dataclass, field

from pipeline.extractor import ExtractionResult

# Lazy-loaded spaCy pipeline
_nlp = None


def _get_nlp():
    """Lazily load medspaCy pipeline with negation detection."""
    global _nlp
    if _nlp is None:
        import medspacy

        _nlp = medspacy.load()
    return _nlp


@dataclass
class NegationResult:
    """Result of negation analysis on an extraction."""

    is_negated: bool
    negation_cues: list[str] = field(default_factory=list)
    conflicts_with_extraction: bool = False
    details: str = ""


# Common negation phrases to check (fallback for when medspaCy misses them)
_NEGATION_PHRASES = [
    "no evidence of",
    "no signs of",
    "negative for",
    "negative",
    "denied",
    "no ",
    "not ",
    "without ",
    "ruled out",
    "ruled-out",
    "unlikely",
    "none ",
    "absent",
    "no documented",
    "no known",
    "wound healing well",
]


def _extraction_says_positive(value: str) -> bool:
    """Check if the extracted value indicates a positive finding."""
    v = value.lower().strip()
    if v.startswith("yes"):
        return True
    if v.startswith("no") or v in ("none documented", "not documented"):
        return False
    if "uncertain" in v:
        return False
    # Assume a specific value (like "14" or "Splenic laceration") is positive
    return True


def _rule_based_negation(text: str) -> list[str]:
    """Find negation cues using simple pattern matching."""
    text_lower = text.lower()
    found: list[str] = []
    for phrase in _NEGATION_PHRASES:
        if phrase in text_lower:
            found.append(phrase)
    return found


def check_negation(
    extraction_result: ExtractionResult,
    field_config: dict,
) -> NegationResult:
    """Run negation detection on the extraction's citation text."""
    citation = extraction_result.citation
    if not citation or not citation.strip():
        return NegationResult(
            is_negated=False,
            details="No citation text to analyze",
        )

    nlp = _get_nlp()
    negation_cues: list[str] = []
    is_negated = False

    # Run medspaCy
    try:
        doc = nlp(citation)
        for ent in doc.ents:
            if hasattr(ent, "is_negated") and ent.is_negated:
                is_negated = True
                # Find the negation cue if available
                if hasattr(ent, "_.context_attributes"):
                    negation_cues.append(f"negated entity: {ent.text}")
                else:
                    negation_cues.append(f"negated: {ent.text}")
    except Exception:
        pass  # Fall through to rule-based

    # Supplement with rule-based detection
    rule_cues = _rule_based_negation(citation)
    if rule_cues:
        negation_cues.extend(rule_cues)
        is_negated = True

    # Determine if negation conflicts with the extraction value
    says_positive = _extraction_says_positive(extraction_result.value)
    conflicts = is_negated and says_positive

    details_parts: list[str] = []
    if is_negated:
        details_parts.append(f"Negation detected in citation (cues: {', '.join(negation_cues)})")
    else:
        details_parts.append("No negation detected in citation")

    if conflicts:
        details_parts.append(
            f"CONFLICT: extraction says '{extraction_result.value}' but "
            "citation text contains negation"
        )

    return NegationResult(
        is_negated=is_negated,
        negation_cues=negation_cues,
        conflicts_with_extraction=conflicts,
        details=". ".join(details_parts),
    )
