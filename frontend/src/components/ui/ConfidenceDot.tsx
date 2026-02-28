interface ConfidenceDotProps {
    score: number;
    size?: "sm" | "md";
}

export function ConfidenceDot({ score, size = "sm" }: ConfidenceDotProps) {
    const color =
        score >= 0.85
            ? "bg-emerald-500"
            : score >= 0.6
                ? "bg-amber-500"
                : "bg-red-500";

    const label =
        score >= 0.85 ? "High" : score >= 0.6 ? "Medium" : "Low";

    const dim = size === "md" ? "h-3 w-3" : "h-2.5 w-2.5";

    return (
        <span
            className={`inline-block shrink-0 rounded-full ${color} ${dim}`}
            title={`Confidence: ${(score * 100).toFixed(0)}% (${label})`}
            aria-label={`Confidence ${(score * 100).toFixed(0)} percent`}
        />
    );
}
