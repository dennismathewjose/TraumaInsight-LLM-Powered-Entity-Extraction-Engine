#!/usr/bin/env python3

from __future__ import annotations
"""Generate realistic clinical notes for loaded trauma patients.

For each patient in the database, generates three template-based clinical notes:
operative report, discharge summary, and radiology report.
"""

import csv
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.clinical_note import ClinicalNote
from app.models.patient import Patient

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "synthea_output"

# ── Clinical note templates ──────────────────────────────────────────────────

SURGEON_NAMES = [
    "Dr. Sarah Mitchell, MD, FACS",
    "Dr. James Thompson, MD, FACS",
    "Dr. Maria Rodriguez, MD",
    "Dr. Robert Chen, MD, FACS",
]

RADIOLOGIST_NAMES = [
    "Dr. Lisa Park, MD",
    "Dr. Ahmed Hassan, MD",
    "Dr. Emily Novak, MD",
]

ATTENDING_NAMES = [
    "Dr. Michael Foster, MD",
    "Dr. Patricia Williams, MD",
    "Dr. David Kim, MD",
]

EBL_OPTIONS = ["50 mL", "100 mL", "150 mL", "200 mL", "300 mL", "450 mL", "75 mL"]

ANTIBIOTICS = [
    "cefazolin 1g IV",
    "vancomycin 1g IV",
    "piperacillin-tazobactam 3.375g IV",
    "ceftriaxone 1g IV",
]

PAIN_MEDS = [
    "morphine 4mg IV q4h PRN",
    "hydromorphone 0.5mg IV q3h PRN",
    "ketorolac 30mg IV q6h",
    "acetaminophen 1000mg PO q6h",
    "oxycodone 5mg PO q4h PRN",
]

DVT_PROPHYLAXIS = [
    "enoxaparin 40mg SQ daily",
    "heparin 5000 units SQ q8h",
    "SCDs bilateral lower extremities",
]


def _get_patient_conditions(synthea_id: str) -> list[str]:
    """Get the condition descriptions for a patient from the Synthea CSV."""
    conditions: list[str] = []
    cond_path = DATA_DIR / "conditions.csv"
    if not cond_path.exists():
        return conditions
    with open(cond_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["PATIENT"] == synthea_id:
                conditions.append(row["DESCRIPTION"])
    return conditions


def _get_patient_procedures(synthea_id: str) -> list[str]:
    """Get procedure descriptions for a patient from the Synthea CSV."""
    procedures: list[str] = []
    proc_path = DATA_DIR / "procedures.csv"
    if not proc_path.exists():
        return procedures
    with open(proc_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["PATIENT"] == synthea_id:
                procedures.append(row["DESCRIPTION"])
    return procedures


def _generate_operative_report(
    patient: Patient, conditions: list[str], procedures: list[str]
) -> str:
    """Generate a realistic operative report."""
    surgeon = random.choice(SURGEON_NAMES)
    ebl = random.choice(EBL_OPTIONS)
    abx = random.choice(ANTIBIOTICS)

    # Pick relevant conditions for pre/post-op diagnosis
    trauma_conditions = [c for c in conditions if any(
        kw in c.lower() for kw in ["fracture", "laceration", "injury", "wound", "contusion", "hemorrhage"]
    )]
    primary_dx = trauma_conditions[0] if trauma_conditions else conditions[0] if conditions else "Traumatic injury NOS"
    secondary_dxs = trauma_conditions[1:3] if len(trauma_conditions) > 1 else []

    # Pick procedures
    relevant_procs = procedures[:3] if procedures else ["Exploratory laparotomy", "Wound debridement"]

    findings_lines = [
        f"Upon exploration, the patient was found to have {primary_dx.lower()}.",
    ]
    if secondary_dxs:
        findings_lines.append(f"Additional findings included {', '.join(d.lower() for d in secondary_dxs)}.")
    findings_lines.append(
        f"The surrounding tissue showed moderate edema and ecchymosis consistent with acute traumatic injury."
    )

    note = f"""OPERATIVE REPORT

Date of Procedure: {patient.admit_date.strftime('%m/%d/%Y')}
Surgeon: {surgeon}
Assistant: Resident physician

PREOPERATIVE DIAGNOSIS:
{primary_dx}
{chr(10).join(secondary_dxs)}

POSTOPERATIVE DIAGNOSIS:
{primary_dx}
{chr(10).join(secondary_dxs)}

PROCEDURE(S) PERFORMED:
{chr(10).join(f"- {p}" for p in relevant_procs)}

ANESTHESIA: General endotracheal

INDICATIONS:
{patient.age} yo {patient.sex} presenting to the trauma bay s/p {patient.mechanism_of_injury.lower()}. \
CT imaging revealed {primary_dx.lower()}. Patient taken to OR for surgical intervention.

FINDINGS:
{chr(10).join(findings_lines)}

DESCRIPTION OF PROCEDURE:
The patient was brought to the operating room and placed in the supine position. \
After adequate general anesthesia was achieved, the patient was prepped and draped in \
the standard sterile fashion. {abx} was administered within 30 minutes prior to incision.

{'The procedure(s) were performed without complication.' if random.random() > 0.3 else 'Minor bleeding was encountered and controlled with electrocautery.'}

All sponge and instrument counts were correct at the end of the case.

EBL: {ebl}
FLUIDS: LR 1500 mL
DRAINS: {random.choice(['None', 'JP drain x1 placed in the operative bed', 'Penrose drain'])}
DISPOSITION: Patient transferred to PACU in stable condition.

Dictated by: {surgeon}
"""
    return note.strip()


def _generate_discharge_summary(
    patient: Patient, conditions: list[str], procedures: list[str]
) -> str:
    """Generate a realistic discharge summary."""
    attending = random.choice(ATTENDING_NAMES)
    pain_med = random.choice(PAIN_MEDS)
    dvt_proph = random.choice(DVT_PROPHYLAXIS)

    trauma_conditions = [c for c in conditions if any(
        kw in c.lower() for kw in ["fracture", "laceration", "injury", "wound", "contusion", "hemorrhage", "concussion"]
    )]
    primary_dx = trauma_conditions[0] if trauma_conditions else "Traumatic injury"

    los = patient.los or random.randint(2, 8)
    discharge_date = patient.discharge_date or (patient.admit_date + timedelta(days=los))

    complications_text = random.choice([
        "Hospital course was uncomplicated.",
        "Hospital course was c/b mild postoperative ileus which resolved with conservative management.",
        "Hospital course notable for transient hypotension responsive to fluid resuscitation.",
        "Postoperative course was unremarkable. Patient progressed well.",
    ])

    note = f"""DISCHARGE SUMMARY

Patient: {patient.first_name or 'Patient'} {patient.last_name or patient.id}
MRN: {patient.id}
Admit Date: {patient.admit_date.strftime('%m/%d/%Y')}
Discharge Date: {discharge_date.strftime('%m/%d/%Y')}
Length of Stay: {los} days
Attending: {attending}

PRINCIPAL DIAGNOSIS:
{primary_dx}

SECONDARY DIAGNOSES:
{chr(10).join(f"- {c}" for c in trauma_conditions[1:4]) or '- None'}

HISTORY OF PRESENT ILLNESS:
{patient.age} yo {patient.sex} who presented to the ED s/p {patient.mechanism_of_injury.lower()}. \
Patient was evaluated by the trauma team and found to have {primary_dx.lower()}. \
ISS was calculated at {patient.iss or 'N/A'}.

HOSPITAL COURSE:
Patient was admitted to the trauma service. {complications_text} \
{'Surgical intervention was performed (see operative report).' if procedures else 'Managed conservatively.'} \
Pain was controlled with {pain_med}. DVT prophylaxis: {dvt_proph}. \
Patient was mobilized on POD#1 with physical therapy.

By POD#{los - 1}, patient was tolerating a regular diet, ambulating independently, \
and pain was well-controlled on oral medications. Wound care was reviewed with the patient.

DISCHARGE MEDICATIONS:
- Acetaminophen 500mg PO q6h PRN pain
- Ibuprofen 400mg PO q8h PRN (with food)
{f'- Oxycodone 5mg PO q4-6h PRN breakthrough pain (qty: 20, no refills)' if random.random() > 0.4 else ''}
- {dvt_proph.split()[0]} (if applicable, per attending)

DISCHARGE INSTRUCTIONS:
1. Follow up with trauma surgery in 2 weeks
2. Return to ED for fever >101.5°F, worsening pain, wound drainage, or SOB
3. No heavy lifting (>10 lbs) for 6 weeks
4. May shower, do not submerge wound

DISCHARGE CONDITION: Stable, improved
DISCHARGE DISPOSITION: Home

Dictated by: {attending}
"""
    return note.strip()


def _generate_radiology_report(
    patient: Patient, conditions: list[str]
) -> str:
    """Generate a realistic radiology / CT report."""
    radiologist = random.choice(RADIOLOGIST_NAMES)

    trauma_conditions = [c for c in conditions if any(
        kw in c.lower() for kw in ["fracture", "laceration", "injury", "wound", "contusion", "hemorrhage", "concussion"]
    )]
    primary_finding = trauma_conditions[0] if trauma_conditions else "Soft tissue injury"

    # Generate modality-specific findings
    modality = random.choice(["CT abdomen/pelvis with IV contrast", "CT chest/abdomen/pelvis with IV contrast", "CT head without contrast"])

    additional_findings = random.choice([
        "Small bilateral pleural effusions. No pneumothorax.",
        "No free fluid in the abdomen or pelvis. No pneumoperitoneum.",
        "Mild bibasilar atelectasis. No acute cardiopulmonary process.",
        "No acute intracranial hemorrhage. No midline shift.",
    ])

    note = f"""RADIOLOGY REPORT

Exam: {modality}
Date: {patient.admit_date.strftime('%m/%d/%Y')}
Ordering Physician: Trauma Surgery
Clinical History: {patient.age} yo {patient.sex} s/p {patient.mechanism_of_injury.lower()}. Evaluate for injury.

TECHNIQUE:
Helical CT was performed from the {"vertex through the skull base" if "head" in modality.lower() else "lung apices through the symphysis pubis"} \
following {'' if 'without' in modality.lower() else 'administration of 100 mL Omnipaque 350 intravenous contrast. '}{'No contrast administered.' if 'without' in modality.lower() else ''} \
Multiplanar reformats were reviewed.

COMPARISON: None available.

FINDINGS:
{primary_finding}: Imaging demonstrates findings consistent with {primary_finding.lower()}. \
{'There is associated soft tissue edema and surrounding inflammatory changes.' if random.random() > 0.3 else 'This is acute in appearance.'}

{chr(10).join(f"Additional finding: {c}" for c in trauma_conditions[1:3])}

{additional_findings}

Osseous structures: {'Fracture line identified as described above.' if any('fracture' in c.lower() for c in trauma_conditions) else 'No acute fracture identified on this study.'}

IMPRESSION:
1. {primary_finding} — acute
{chr(10).join(f"{i+2}. {c}" for i, c in enumerate(trauma_conditions[1:3]))}
{f'{len(trauma_conditions) + 1}. {additional_findings.split(".")[0]}' if len(trauma_conditions) < 3 else ''}

Findings communicated to trauma team by telephone at time of interpretation.

Interpreted by: {radiologist}
"""
    return note.strip()


def main() -> None:
    print("=" * 60)
    print("TraumaInsight — Clinical Note Generator")
    print("=" * 60)

    settings = get_settings()
    engine = create_engine(settings.sync_database_url, echo=False)

    with Session(engine) as session:
        # Clear existing notes
        session.execute(text("DELETE FROM clinical_notes"))
        session.commit()

        patients = session.execute(select(Patient)).scalars().all()
        if not patients:
            print("⚠️  No patients found. Run load_synthea.py first.")
            sys.exit(1)

        note_count = 0
        for patient in patients:
            synthea_id = patient.synthea_id or ""
            conditions = _get_patient_conditions(synthea_id)
            procedures = _get_patient_procedures(synthea_id)

            admit_dt = datetime.combine(patient.admit_date, datetime.min.time())

            # 1. Operative Report
            op_note = ClinicalNote(
                id=str(uuid4()),
                patient_id=patient.id,
                note_type="operative_report",
                content=_generate_operative_report(patient, conditions, procedures),
                author_role="surgeon",
                note_date=admit_dt,
            )
            session.add(op_note)
            note_count += 1

            # 2. Discharge Summary
            discharge_dt = datetime.combine(
                patient.discharge_date or patient.admit_date + timedelta(days=patient.los or 3),
                datetime.min.time(),
            )
            dc_note = ClinicalNote(
                id=str(uuid4()),
                patient_id=patient.id,
                note_type="discharge_summary",
                content=_generate_discharge_summary(patient, conditions, procedures),
                author_role="attending",
                note_date=discharge_dt,
            )
            session.add(dc_note)
            note_count += 1

            # 3. Radiology Report
            rad_note = ClinicalNote(
                id=str(uuid4()),
                patient_id=patient.id,
                note_type="radiology_report",
                content=_generate_radiology_report(patient, conditions),
                author_role="radiologist",
                note_date=admit_dt + timedelta(hours=1),
            )
            session.add(rad_note)
            note_count += 1

        session.commit()

    print(f"\n✅ Generated {note_count} clinical notes for {len(patients)} patients")
    print(f"   ({note_count // 3} patients × 3 notes each)")
    print("=" * 60)


if __name__ == "__main__":
    main()
