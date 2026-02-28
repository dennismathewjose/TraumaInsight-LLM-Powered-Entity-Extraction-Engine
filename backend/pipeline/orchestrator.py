"""Full extraction pipeline orchestrator — processes patients end-to-end."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

# Ensure backend/ is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings  # noqa: E402
from app.models.extraction import Extraction  # noqa: E402
from app.models.patient import Patient  # noqa: E402
from pipeline.citation_builder import build_citation  # noqa: E402
from pipeline.confidence_scorer import score_extraction  # noqa: E402
from pipeline.config import DEFAULT_LLM_MODEL  # noqa: E402
from pipeline.embedder import embed_patient  # noqa: E402
from pipeline.extractor import extract  # noqa: E402
from pipeline.negation_handler import check_negation  # noqa: E402
from pipeline.registry_fields import REGISTRY_FIELDS  # noqa: E402
from pipeline.retriever import retrieve  # noqa: E402


def _get_sync_session():
    settings = get_settings()
    engine = create_engine(settings.sync_database_url, echo=False)
    return Session(engine)


def process_patient(patient_id: str, model: str = DEFAULT_LLM_MODEL) -> dict:
    """Run the full extraction pipeline for a single patient.

    Returns a summary dict with counts and timing.
    """
    t0 = time.time()
    print(f"\nProcessing patient {patient_id} with model {model}...")

    session = _get_sync_session()

    # 1. Verify patient exists
    patient = session.execute(
        select(Patient).where(Patient.id == patient_id)
    ).scalar_one_or_none()

    if patient is None:
        session.close()
        raise ValueError(f"Patient {patient_id} not found")

    # 2. Embed clinical notes (skips if already done)
    try:
        print(f"  Embedding clinical notes...")
        embed_patient(patient_id)
    except Exception as e:
        session.close()
        raise RuntimeError(f"Embedding failed for {patient_id}: {e}") from e

    # 3. Delete existing extractions (clean slate for re-run)
    session.execute(
        delete(Extraction).where(Extraction.patient_id == patient_id)
    )
    session.commit()

    # 4. Process each registry field
    auto_count = 0
    review_count = 0
    total_fields = len(REGISTRY_FIELDS)

    for idx, field_cfg in enumerate(REGISTRY_FIELDS, 1):
        try:
            # Retrieve
            passages = retrieve(patient_id, field_cfg["query"])

            # Extract via LLM
            extraction_result = extract(passages, field_cfg, model=model)

            # Negation check
            negation_result = check_negation(extraction_result, field_cfg)

            # Confidence score
            confidence = score_extraction(passages, extraction_result, negation_result)

            # Build citation
            citation_text, source_note_type = build_citation(extraction_result, passages)

            # Determine source note ID (highest similarity passage)
            source_note_id = passages[0].note_id if passages else None

            # Create extraction record
            ext = Extraction(
                id=str(uuid4()),
                patient_id=patient_id,
                source_note_id=source_note_id,
                section=field_cfg["section"],
                field_label=field_cfg["field_label"],
                field_key=field_cfg["field_key"],
                extracted_value=extraction_result.value,
                confidence_score=confidence.score,
                status=confidence.status,
                citation_text=citation_text,
                source_note_type=source_note_type,
                conflict_reason=confidence.conflict_reason,
                extraction_method="rag",
            )
            session.add(ext)
            session.commit()

            if confidence.status == "auto":
                auto_count += 1
            else:
                review_count += 1

            print(
                f"  [{idx}/{total_fields}] {field_cfg['field_key']}: "
                f"{extraction_result.value} "
                f"({confidence.score:.2f}, {confidence.status})"
            )

        except Exception as e:
            # Graceful failure — save a failed extraction
            ext = Extraction(
                id=str(uuid4()),
                patient_id=patient_id,
                section=field_cfg["section"],
                field_label=field_cfg["field_label"],
                field_key=field_cfg["field_key"],
                extracted_value="Extraction failed",
                confidence_score=0.0,
                status="review",
                conflict_reason=f"Pipeline error: {e}",
                extraction_method="rag",
            )
            session.add(ext)
            session.commit()
            review_count += 1
            print(f"  [{idx}/{total_fields}] {field_cfg['field_key']}: ERROR — {e}")

    session.close()
    elapsed = time.time() - t0

    summary = {
        "patient_id": patient_id,
        "total_fields": total_fields,
        "auto_filled": auto_count,
        "needs_review": review_count,
        "model": model,
        "time_seconds": round(elapsed, 1),
    }

    print(f"\nPipeline complete for {patient_id}:")
    print(f"  Total fields: {total_fields}")
    print(f"  Auto-accepted: {auto_count} ({auto_count / total_fields * 100:.1f}%)")
    print(f"  Needs review: {review_count} ({review_count / total_fields * 100:.1f}%)")
    print(f"  Time: {elapsed:.1f}s")

    return summary


def process_all_patients(
    model: str = DEFAULT_LLM_MODEL,
    limit: int | None = None,
) -> dict:
    """Run pipeline for all (or first N) patients."""
    session = _get_sync_session()
    query = select(Patient.id).order_by(Patient.id)
    if limit:
        query = query.limit(limit)
    patient_ids = session.execute(query).scalars().all()
    session.close()

    t0 = time.time()
    total_auto = 0
    total_review = 0
    processed = 0

    for pid in patient_ids:
        try:
            result = process_patient(pid, model=model)
            total_auto += result["auto_filled"]
            total_review += result["needs_review"]
            processed += 1
        except Exception as e:
            print(f"  SKIPPING {pid}: {e}")

    elapsed = time.time() - t0
    return {
        "patients_processed": processed,
        "total_fields": processed * len(REGISTRY_FIELDS),
        "auto_filled": total_auto,
        "needs_review": total_review,
        "model": model,
        "time_seconds": round(elapsed, 1),
    }


def process_patient_batch(
    patient_ids: list[str],
    model: str = DEFAULT_LLM_MODEL,
) -> dict:
    """Run pipeline for specific patients."""
    t0 = time.time()
    total_auto = 0
    total_review = 0
    processed = 0

    for pid in patient_ids:
        try:
            result = process_patient(pid, model=model)
            total_auto += result["auto_filled"]
            total_review += result["needs_review"]
            processed += 1
        except Exception as e:
            print(f"  SKIPPING {pid}: {e}")

    elapsed = time.time() - t0
    return {
        "patients_processed": processed,
        "total_fields": processed * len(REGISTRY_FIELDS),
        "auto_filled": total_auto,
        "needs_review": total_review,
        "model": model,
        "time_seconds": round(elapsed, 1),
    }
