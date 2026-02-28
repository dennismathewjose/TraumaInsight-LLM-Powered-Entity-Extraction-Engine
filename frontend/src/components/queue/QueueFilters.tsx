"use client";

interface QueueFiltersProps {
    active: string;
    onChange: (filter: string) => void;
}

const filters = [
    { key: "all", label: "All" },
    { key: "pending", label: "Pending" },
    { key: "completed", label: "Completed" },
];

export function QueueFilters({ active, onChange }: QueueFiltersProps) {
    return (
        <div className="flex gap-1 rounded-lg bg-slate-100 p-1">
            {filters.map((f) => (
                <button
                    key={f.key}
                    onClick={() => onChange(f.key)}
                    className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${active === f.key
                            ? "bg-white text-slate-900 shadow-sm"
                            : "text-slate-500 hover:text-slate-700"
                        }`}
                    aria-pressed={active === f.key}
                >
                    {f.label}
                </button>
            ))}
        </div>
    );
}
