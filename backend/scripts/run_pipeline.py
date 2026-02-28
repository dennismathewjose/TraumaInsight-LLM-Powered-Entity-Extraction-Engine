#!/usr/bin/env python3
"""Standalone CLI runner for the TraumaInsight extraction pipeline.

Usage:
    python scripts/run_pipeline.py --patient P-10001
    python scripts/run_pipeline.py --limit 5
    python scripts/run_pipeline.py --all
    python scripts/run_pipeline.py --patient P-10001 --model cniongolo/biomistral
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Ensure backend/ is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.orchestrator import process_all_patients, process_patient  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TraumaInsight Extraction Pipeline Runner"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--patient", type=str, help="Process a single patient (e.g., P-10001)")
    group.add_argument("--limit", type=int, help="Process first N patients")
    group.add_argument("--all", action="store_true", help="Process all patients")

    parser.add_argument(
        "--model",
        type=str,
        default="llama3",
        help="Ollama model to use (default: llama3)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  TraumaInsight — RAG Extraction Pipeline")
    print("=" * 60)

    t0 = time.time()

    if args.patient:
        result = process_patient(args.patient, model=args.model)
        patients_processed = 1
    elif args.limit:
        result = process_all_patients(model=args.model, limit=args.limit)
        patients_processed = result["patients_processed"]
    else:  # --all
        result = process_all_patients(model=args.model)
        patients_processed = result["patients_processed"]

    elapsed = time.time() - t0

    print("\n" + "=" * 60)
    print("  PIPELINE SUMMARY")
    print("=" * 60)

    if args.patient:
        print(f"  Patient:        {result['patient_id']}")
        print(f"  Model:          {result['model']}")
        print(f"  Total fields:   {result['total_fields']}")
        print(f"  Auto-accepted:  {result['auto_filled']}")
        print(f"  Needs review:   {result['needs_review']}")
    else:
        print(f"  Patients:       {patients_processed}")
        print(f"  Model:          {result['model']}")
        print(f"  Total fields:   {result['total_fields']}")
        print(f"  Auto-accepted:  {result['auto_filled']}")
        print(f"  Needs review:   {result['needs_review']}")

    print(f"  Total time:     {elapsed:.1f}s")
    if patients_processed > 0:
        print(f"  Avg per patient: {elapsed / patients_processed:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
