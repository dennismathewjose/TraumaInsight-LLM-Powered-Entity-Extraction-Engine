import type { FieldStatus } from "@/lib/types";

const config: Record<FieldStatus, { label: string; className: string }> = {
    auto: {
        label: "AI",
        className: "bg-emerald-100 text-emerald-700 border-emerald-300",
    },
    review: {
        label: "REVIEW",
        className: "bg-amber-100 text-amber-700 border-amber-300",
    },
    confirmed: {
        label: "CONFIRMED",
        className: "bg-blue-100 text-blue-700 border-blue-300",
    },
    corrected: {
        label: "CORRECTED",
        className: "bg-violet-100 text-violet-700 border-violet-300",
    },
};

interface StatusBadgeProps {
    status: FieldStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
    const c = config[status];
    return (
        <span
            className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${c.className}`}
        >
            {c.label}
        </span>
    );
}

/* ── Priority badge (for patient list) ────────────────────────────────── */

const priorityConfig: Record<string, string> = {
    high: "bg-red-100 text-red-700",
    medium: "bg-amber-100 text-amber-700",
    low: "bg-emerald-100 text-emerald-700",
};

export function PriorityBadge({ priority }: { priority: string }) {
    return (
        <span
            className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${priorityConfig[priority] || "bg-slate-100 text-slate-600"
                }`}
        >
            {priority}
        </span>
    );
}

/* ── Patient status badge ─────────────────────────────────────────────── */

const patientStatusConfig: Record<string, { label: string; className: string }> = {
    pending: { label: "Pending", className: "bg-amber-100 text-amber-700" },
    review: { label: "In Review", className: "bg-blue-100 text-blue-700" },
    completed: { label: "Done", className: "bg-emerald-100 text-emerald-700" },
};

export function PatientStatusBadge({ status }: { status: string }) {
    const c = patientStatusConfig[status] || {
        label: status,
        className: "bg-slate-100 text-slate-600",
    };
    return (
        <span
            className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${c.className}`}
        >
            {c.label}
        </span>
    );
}
