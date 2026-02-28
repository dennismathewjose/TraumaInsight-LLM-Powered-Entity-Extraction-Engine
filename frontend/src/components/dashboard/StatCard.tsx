interface StatCardProps {
    label: string;
    value: string | number;
    color?: "default" | "amber" | "emerald" | "blue";
    subtitle?: string;
}

const colorMap = {
    default: "text-slate-900",
    amber: "text-amber-600",
    emerald: "text-emerald-600",
    blue: "text-blue-600",
};

export function StatCard({ label, value, color = "default", subtitle }: StatCardProps) {
    return (
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                {label}
            </p>
            <p className={`mt-1.5 text-2xl font-bold ${colorMap[color]}`}>
                {value}
            </p>
            {subtitle && (
                <p className="mt-0.5 text-xs text-slate-400">{subtitle}</p>
            )}
        </div>
    );
}
