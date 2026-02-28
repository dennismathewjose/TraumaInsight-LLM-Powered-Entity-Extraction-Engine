"use client";

import type { ClinicalNote, FormField } from "@/lib/types";
import { ConfidenceDot } from "@/components/ui/ConfidenceDot";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { CitationCard } from "@/components/patient/CitationCard";
import { ConflictAlert } from "@/components/patient/ConflictAlert";
import { ReviewActions } from "@/components/patient/ReviewActions";
import { NoteViewer } from "@/components/patient/NoteViewer";

interface EvidencePanelProps {
    field: FormField | null;
    notes: ClinicalNote[];
    onConfirm: (fieldId: string) => Promise<void>;
    onCorrect: (fieldId: string, value: string, notes?: string) => Promise<void>;
}

export function EvidencePanel({
    field,
    notes,
    onConfirm,
    onCorrect,
}: EvidencePanelProps) {
    // Empty state
    if (!field) {
        return (
            <div className="flex h-full items-center justify-center p-8">
                <div className="text-center">
                    <p className="text-4xl">👈</p>
                    <p className="mt-3 text-sm font-medium text-slate-400">
                        Click any field to see the evidence
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-5 p-5">
            {/* Header */}
            <div>
                <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">
                    Evidence for
                </p>
                <h3 className="mt-0.5 text-lg font-bold text-slate-900">
                    {field.field_label}
                </h3>
            </div>

            {/* AI's answer */}
            <div className="rounded-lg border border-slate-200 bg-white p-4">
                <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">
                    AI&apos;s Answer
                </p>
                <div className="mt-2 flex items-center gap-2">
                    <span className="text-base font-semibold text-slate-900">
                        {field.extracted_value}
                    </span>
                    <ConfidenceDot score={field.confidence_score} size="md" />
                    <span className="text-xs text-slate-400">
                        {(field.confidence_score * 100).toFixed(0)}%
                    </span>
                </div>
                <div className="mt-2">
                    <StatusBadge status={field.status} />
                </div>
            </div>

            {/* Citation */}
            {field.citation_text && field.source_note_type && (
                <CitationCard
                    citationText={field.citation_text}
                    sourceNoteType={field.source_note_type}
                />
            )}

            {/* Conflict alert */}
            {field.conflict_reason && (
                <ConflictAlert reason={field.conflict_reason} />
            )}

            {/* Review actions (only for fields needing review) */}
            {field.status === "review" && (
                <ReviewActions
                    onConfirm={() => onConfirm(field.id)}
                    onCorrect={(value, n) => onCorrect(field.id, value, n)}
                />
            )}

            {/* Confirmation messages */}
            {field.status === "confirmed" && (
                <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
                    <p className="text-sm font-medium text-emerald-700">
                        ✓ You confirmed the AI&apos;s answer
                    </p>
                </div>
            )}
            {field.status === "corrected" && (
                <div className="rounded-lg border border-violet-200 bg-violet-50 p-4">
                    <p className="text-sm font-medium text-violet-700">
                        ✎ You corrected this to: <strong>{field.extracted_value}</strong>
                    </p>
                </div>
            )}

            {/* Clinical notes */}
            <div className="border-t border-slate-200 pt-5">
                <NoteViewer notes={notes} />
            </div>
        </div>
    );
}
