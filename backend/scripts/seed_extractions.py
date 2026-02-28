#!/usr/bin/env python3

from __future__ import annotations
"""Seed extraction data for the first N patients.

Generates realistic extraction results that mimic what the AI pipeline
would produce, allowing frontend testing before the pipeline exists.
"""

import random
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.clinical_note import ClinicalNote
from app.models.extraction import Extraction
from app.models.patient import Patient

NUM_PATIENTS_TO_SEED = 5

# ── Extraction field definitions by section ──────────────────────────────────

FIELD_DEFINITIONS: list[dict] = [
    # INJURIES
    {"section": "injuries", "field_key": "primary_injury", "field_label": "Primary Injury"},
    {"section": "injuries", "field_key": "injury_location", "field_label": "Injury Location"},
    # PROCEDURES
    {"section": "procedures", "field_key": "primary_procedure", "field_label": "Primary Procedure"},
    {"section": "procedures", "field_key": "secondary_procedure", "field_label": "Secondary Procedure"},
    # COMPLICATIONS
    {"section": "complications", "field_key": "complications_present", "field_label": "Complications Present"},
    {"section": "complications", "field_key": "complication_type", "field_label": "Complication Type"},
    # SEVERITY
    {"section": "severity", "field_key": "iss_score", "field_label": "Injury Severity Score (ISS)"},
    {"section": "severity", "field_key": "gcs_score", "field_label": "Glasgow Coma Scale (GCS)"},
    # DISCHARGE
    {"section": "discharge", "field_key": "discharge_disposition", "field_label": "Discharge Disposition"},
]

FALLBACK_VALUES: dict[str, list[str]] = {
    "primary_injury": [
        "Splenic laceration", "Rib fracture", "Liver laceration",
        "Tibial fracture", "Femur fracture", "Concussion",
        "Pneumothorax", "Pelvic fracture",
    ],
    "injury_location": [
        "Abdomen", "Chest", "Lower extremity", "Upper extremity",
        "Head", "Pelvis", "Spine",
    ],
    "primary_procedure": [
        "Splenectomy", "Open reduction internal fixation",
        "Exploratory laparotomy", "Chest tube insertion",
        "Wound debridement", "Craniotomy",
    ],
    "secondary_procedure": [
        "Wound closure", "Drain placement", "Fracture reduction",
        "Skin grafting", "None",
    ],
    "complications_present": ["Yes", "No"],
    "complication_type": [
        "Surgical site infection", "DVT", "Pneumonia",
        "Urinary tract infection", "None", "Postoperative ileus",
    ],
    "iss_score": ["9", "16", "22", "25", "29", "4", "14"],
    "gcs_score": ["15", "14", "13", "12", "15", "15"],
    "discharge_disposition": [
        "Home", "Home with services", "Rehabilitation facility",
        "Skilled nursing facility", "Transferred",
    ],
}

CONFLICT_REASONS = [
    "Operative report and discharge summary disagree on this value.",
    "Multiple conflicting references found across clinical notes.",
    "Extracted value matches radiology report but not operative note.",
    "Low extraction confidence — ambiguous wording in source note.",
    "Discharge summary mentions a different value than the operative report.",
]

NOTE_TYPE_MAP = {
    "injuries": "operative_report",
    "procedures": "operative_report",
    "complications": "discharge_summary",
    "severity": "radiology_report",
    "discharge": "discharge_summary",
}


def _extract_citation(note_content: str, field_key: str) -> str | None:
    """Extract a plausible citation snippet from the note content."""
    lines = note_content.split("\n")
    # Try to find a relevant line
    keywords_map = {
        "primary_injury": ["diagnosis", "injury", "laceration", "fracture"],
        "injury_location": ["abdomen", "chest", "extremity", "head", "pelvis"],
        "primary_procedure": ["procedure", "performed", "operation"],
        "secondary_procedure": ["wound", "drain", "closure"],
        "complications_present": ["complication", "uncomplicated", "c/b"],
        "complication_type": ["infection", "dvt", "pneumonia", "ileus"],
        "iss_score": ["iss", "severity", "score"],
        "gcs_score": ["gcs", "glasgow", "neuro"],
        "discharge_disposition": ["discharge", "disposition", "home"],
    }
    search_words = keywords_map.get(field_key, [])

    for line in lines:
        line_stripped = line.strip()
        if line_stripped and any(kw in line_stripped.lower() for kw in search_words):
            # Return a snippet (max 200 chars)
            return line_stripped[:200]

    # Fallback: return first non-empty content line
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("=") and len(stripped) > 20:
            return stripped[:200]
    return None


def main() -> None:
    print("=" * 60)
    print("TraumaInsight — Extraction Seeder")
    print("=" * 60)

    settings = get_settings()
    engine = create_engine(settings.sync_database_url, echo=False)

    with Session(engine) as session:
        # Clear existing extractions and reviews
        session.execute(text("DELETE FROM review_decisions"))
        session.execute(text("DELETE FROM extractions"))
        session.commit()

        patients = session.execute(
            select(Patient).order_by(Patient.id).limit(NUM_PATIENTS_TO_SEED)
        ).scalars().all()

        if not patients:
            print("⚠️  No patients found. Run load_synthea.py first.")
            sys.exit(1)

        extraction_count = 0
        review_count = 0

        for patient in patients:
            # Get patient's clinical notes
            notes = session.execute(
                select(ClinicalNote).where(ClinicalNote.patient_id == patient.id)
            ).scalars().all()

            notes_by_type: dict[str, ClinicalNote] = {}
            for n in notes:
                notes_by_type[n.note_type] = n

            # Randomly pick 1-2 fields to be "review" status
            review_indices = set(random.sample(range(len(FIELD_DEFINITIONS)), k=min(2, len(FIELD_DEFINITIONS))))

            for idx, field_def in enumerate(FIELD_DEFINITIONS):
                source_note_type = NOTE_TYPE_MAP.get(field_def["section"], "operative_report")
                source_note = notes_by_type.get(source_note_type)

                # Pick value
                field_key = field_def["field_key"]
                values = FALLBACK_VALUES.get(field_key, ["Unknown"])

                # For ISS, try to use patient's actual ISS
                if field_key == "iss_score" and patient.iss is not None:
                    extracted_value = str(patient.iss)
                else:
                    extracted_value = random.choice(values)

                # Determine status and confidence
                is_review = idx in review_indices
                if is_review:
                    confidence = round(random.uniform(0.55, 0.78), 2)
                    status = "review"
                    conflict_reason = random.choice(CONFLICT_REASONS)
                    review_count += 1
                else:
                    confidence = round(random.uniform(0.85, 0.98), 2)
                    status = "auto"
                    conflict_reason = None

                # Get citation
                citation = None
                if source_note:
                    citation = _extract_citation(source_note.content, field_key)

                extraction = Extraction(
                    id=str(uuid4()),
                    patient_id=patient.id,
                    source_note_id=source_note.id if source_note else None,
                    section=field_def["section"],
                    field_label=field_def["field_label"],
                    field_key=field_key,
                    extracted_value=extracted_value,
                    confidence_score=confidence,
                    status=status,
                    citation_text=citation,
                    source_note_type=source_note_type,
                    conflict_reason=conflict_reason,
                    extraction_method="rag",
                )
                session.add(extraction)
                extraction_count += 1

        session.commit()

    print(f"\n✅ Seeded {extraction_count} extractions for {len(patients)} patients")
    print(f"   {extraction_count - review_count} auto-filled, {review_count} needing review")
    print("=" * 60)


if __name__ == "__main__":
    main()
