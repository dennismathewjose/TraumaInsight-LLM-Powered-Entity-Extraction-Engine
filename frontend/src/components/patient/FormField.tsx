"use client";

import type { FormField as FormFieldType } from "@/lib/types";
import { ConfidenceDot } from "@/components/ui/ConfidenceDot";
import { StatusBadge } from "@/components/ui/StatusBadge";

interface FormFieldProps {
    field: FormFieldType;
    isSelected: boolean;
    onSelect: () => void;
}

const statusBg: Record<string, string> = {
    auto: "border-l-emerald-400 bg-emerald-50/40 hover:bg-emerald-50",
    review: "border-l-amber-400 bg-amber-50/40 hover:bg-amber-50",
    confirmed: "border-l-blue-400 bg-blue-50/40 hover:bg-blue-50",
    corrected: "border-l-violet-400 bg-violet-50/40 hover:bg-violet-50",
};

export function FormField({ field, isSelected, onSelect }: FormFieldProps) {
    return (
        <button
            onClick={onSelect}
            aria-label={`View evidence for ${field.field_label}`}
            className={`group w-full border-l-4 px-4 py-3 text-left transition-all ${statusBg[field.status] || ""
                } ${isSelected ? "ring-2 ring-blue-400 ring-inset" : ""}`}
        >
            <div className="flex items-start justify-between gap-3">
                <div className="min-w-0 flex-1">
                    <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">
                        {field.field_label}
                    </p>
                    <p className="mt-0.5 text-sm font-semibold text-slate-900">
                        {field.status === "review" && (
                            <span className="mr-1 text-amber-600">⚠</span>
                        )}
                        {field.extracted_value}
                    </p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                    <ConfidenceDot score={field.confidence_score} />
                    <StatusBadge status={field.status} />
                </div>
            </div>
        </button>
    );
}
