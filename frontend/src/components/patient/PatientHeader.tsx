"use client";

import Link from "next/link";
import type { PatientDetail } from "@/lib/types";

interface PatientHeaderProps {
    patient: PatientDetail;
    unresolvedCount: number;
    onSubmit: () => void;
    isSubmitting: boolean;
}

export function PatientHeader({
    patient,
    unresolvedCount,
    onSubmit,
    isSubmitting,
}: PatientHeaderProps) {
    return (
        <div className="sticky top-16 z-40 border-b border-slate-200 bg-white shadow-sm">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
                {/* Left: back + patient info */}
                <div className="flex items-center gap-4">
                    <Link
                        href="/queue"
                        className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700"
                    >
                        ← Queue
                    </Link>
                    <div className="h-6 w-px bg-slate-200" />
                    <div>
                        <span className="font-bold text-slate-900">{patient.id}</span>
                        <span className="ml-2 text-sm text-slate-500">
                            {patient.first_name} {patient.last_name}
                        </span>
                        <span className="ml-3 text-sm text-slate-400">
                            {patient.age}/{patient.sex} · {patient.mechanism_of_injury} ·
                            Admitted {patient.admit_date}
                        </span>
                    </div>
                </div>

                {/* Right: status */}
                <div>
                    {unresolvedCount > 0 ? (
                        <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-700">
                            <span className="inline-block h-2 w-2 rounded-full bg-amber-500" />
                            {unresolvedCount} field{unresolvedCount !== 1 ? "s" : ""} to review
                        </span>
                    ) : (
                        <button
                            onClick={onSubmit}
                            disabled={isSubmitting}
                            className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-emerald-700 disabled:opacity-50"
                        >
                            {isSubmitting ? "Submitting…" : "✓ Submit to Registry"}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
