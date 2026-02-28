#!/usr/bin/env python3

from __future__ import annotations
"""Load Synthea CSV data into the TraumaInsight database.

Reads CSV files from ../data/synthea_output/, filters for trauma patients,
and populates the patients and encounters tables.
"""

import csv
import random
import sys
from datetime import date, datetime
from pathlib import Path

# Add backend dir to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base
from app.models.encounter import Encounter
from app.models.patient import Patient

# ── Configuration ────────────────────────────────────────────────────────────

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "synthea_output"

TRAUMA_KEYWORDS = [
    "laceration", "fracture", "contusion", "wound",
    "injury", "trauma", "burn", "dislocation", "sprain",
    "concussion", "hemorrhage",
]

EXCLUDE_KEYWORDS = [
    "dental",
    "stress fracture",
]

INJURY_MECHANISMS = [
    "Motor vehicle collision",
    "Fall from height",
    "Pedestrian struck by vehicle",
    "Motorcycle crash",
    "Bicycle accident",
    "Assault / blunt force",
    "Stabbing / penetrating injury",
    "Fall (ground level)",
    "Machinery accident",
    "Sports injury",
]

ENCOUNTER_TYPE_MAP = {
    "emergency": "emergency",
    "urgentcare": "emergency",
    "inpatient": "inpatient",
    "ambulatory": "inpatient",
    "wellness": "inpatient",
    "outpatient": "outpatient",
}


def _is_trauma_condition(description: str) -> bool:
    """Check whether a condition description is trauma-related."""
    desc_lower = description.lower()
    if any(excl in desc_lower for excl in EXCLUDE_KEYWORDS):
        return False
    return any(kw in desc_lower for kw in TRAUMA_KEYWORDS)


def _compute_age(birthdate_str: str, reference_date: date | None = None) -> int:
    """Compute age in years from a birthdate string (YYYY-MM-DD)."""
    birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
    ref = reference_date or date.today()
    age = ref.year - birthdate.year
    if (ref.month, ref.day) < (birthdate.month, birthdate.day):
        age -= 1
    return age


def _assign_priority(conditions: list[str]) -> str:
    """Assign a priority based on condition severity heuristics."""
    high_keywords = ["hemorrhage", "laceration", "concussion", "trauma", "burn"]
    for cond in conditions:
        if any(kw in cond.lower() for kw in high_keywords):
            return "high"
    if len(conditions) >= 3:
        return "high"
    if len(conditions) >= 2:
        return "medium"
    return "low"


def main() -> None:
    print("=" * 60)
    print("TraumaInsight — Synthea Data Loader")
    print("=" * 60)

    if not DATA_DIR.exists():
        print(f"ERROR: Data directory not found: {DATA_DIR}")
        sys.exit(1)

    # ── Step 1: Parse conditions to find trauma patients ─────────────────
    print(f"\n📂 Reading conditions from {DATA_DIR / 'conditions.csv'} …")
    trauma_patient_conditions: dict[str, list[str]] = {}

    with open(DATA_DIR / "conditions.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            desc = row["DESCRIPTION"]
            if _is_trauma_condition(desc):
                patient_uuid = row["PATIENT"]
                if patient_uuid not in trauma_patient_conditions:
                    trauma_patient_conditions[patient_uuid] = []
                trauma_patient_conditions[patient_uuid].append(desc)

    print(f"   Found {len(trauma_patient_conditions)} trauma patients "
          f"out of total conditions")

    if not trauma_patient_conditions:
        print("⚠️  No trauma patients found. Check the data files.")
        sys.exit(1)

    # ── Step 2: Parse patients.csv ───────────────────────────────────────
    print(f"\n📂 Reading patients from {DATA_DIR / 'patients.csv'} …")
    synthea_patients: dict[str, dict] = {}
    total_synthea = 0

    with open(DATA_DIR / "patients.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_synthea += 1
            if row["Id"] in trauma_patient_conditions:
                synthea_patients[row["Id"]] = row

    print(f"   Matched {len(synthea_patients)} trauma patients out of "
          f"{total_synthea} total Synthea patients")

    # ── Step 3: Parse encounters.csv ─────────────────────────────────────
    print(f"\n📂 Reading encounters from {DATA_DIR / 'encounters.csv'} …")
    trauma_encounters: dict[str, list[dict]] = {}

    with open(DATA_DIR / "encounters.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            patient_uuid = row["PATIENT"]
            if patient_uuid in trauma_patient_conditions:
                if patient_uuid not in trauma_encounters:
                    trauma_encounters[patient_uuid] = []
                trauma_encounters[patient_uuid].append(row)

    # ── Step 4: Load into database ───────────────────────────────────────
    settings = get_settings()
    engine = create_engine(settings.sync_database_url, echo=False)

    # Ensure tables exist
    Base.metadata.create_all(engine)

    patient_count = 0
    encounter_count = 0

    with Session(engine) as session:
        # Clear existing data
        session.execute(text("DELETE FROM encounters"))
        session.execute(text("DELETE FROM clinical_notes"))
        session.execute(text("DELETE FROM review_decisions"))
        session.execute(text("DELETE FROM extractions"))
        session.execute(text("DELETE FROM patients"))
        session.commit()

        for idx, (synthea_uuid, pdata) in enumerate(synthea_patients.items(), start=1):
            patient_id = f"P-{10000 + idx}"
            admit_conditions = trauma_patient_conditions[synthea_uuid]

            # Compute fields
            age = _compute_age(pdata["BIRTHDATE"])
            sex_char = "M" if pdata["GENDER"] == "M" else "F"
            mechanism = random.choice(INJURY_MECHANISMS)
            priority = _assign_priority(admit_conditions)
            iss = random.randint(4, 34)

            # Find admit/discharge from encounters
            patient_encs = trauma_encounters.get(synthea_uuid, [])
            if patient_encs:
                sorted_encs = sorted(patient_encs, key=lambda e: e["START"])
                first_enc_start = datetime.fromisoformat(
                    sorted_encs[0]["START"].replace("Z", "+00:00")
                ).date()
                last_enc_stop = None
                if sorted_encs[-1].get("STOP"):
                    last_enc_stop = datetime.fromisoformat(
                        sorted_encs[-1]["STOP"].replace("Z", "+00:00")
                    ).date()
                admit_date = first_enc_start
                discharge_date = last_enc_stop
            else:
                admit_date = date.today()
                discharge_date = None

            los = (discharge_date - admit_date).days if discharge_date else None

            patient = Patient(
                id=patient_id,
                synthea_id=synthea_uuid,
                first_name=pdata.get("FIRST"),
                last_name=pdata.get("LAST"),
                age=age,
                sex=sex_char,
                admit_date=admit_date,
                discharge_date=discharge_date,
                mechanism_of_injury=mechanism,
                iss=iss,
                los=los,
                status="pending",
                priority=priority,
            )
            session.add(patient)
            patient_count += 1

            # Add encounters
            for enc_row in patient_encs:
                enc_class = enc_row.get("ENCOUNTERCLASS", "inpatient").lower()
                enc_type = ENCOUNTER_TYPE_MAP.get(enc_class, "inpatient")

                start_dt = datetime.fromisoformat(
                    enc_row["START"].replace("Z", "+00:00")
                )
                end_dt = None
                if enc_row.get("STOP"):
                    end_dt = datetime.fromisoformat(
                        enc_row["STOP"].replace("Z", "+00:00")
                    )

                encounter = Encounter(
                    id=enc_row["Id"],
                    patient_id=patient_id,
                    encounter_type=enc_type,
                    start_date=start_dt,
                    end_date=end_dt,
                    primary_diagnosis_code=enc_row.get("REASONCODE") or None,
                    primary_diagnosis_desc=enc_row.get("REASONDESCRIPTION") or None,
                )
                session.add(encounter)
                encounter_count += 1

        session.commit()

    print(f"\n✅ Loaded {patient_count} trauma patients "
          f"(out of {total_synthea} total Synthea patients)")
    print(f"✅ Loaded {encounter_count} encounters")
    print("=" * 60)


if __name__ == "__main__":
    main()
