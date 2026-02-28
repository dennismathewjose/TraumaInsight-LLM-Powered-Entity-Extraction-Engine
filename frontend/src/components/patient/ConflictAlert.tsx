interface ConflictAlertProps {
    reason: string;
}

export function ConflictAlert({ reason }: ConflictAlertProps) {
    return (
        <div className="rounded-lg border border-orange-200 bg-orange-50 p-4">
            <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-orange-600">
                <span>⚠</span> Conflict Detected
            </p>
            <p className="mt-1.5 text-sm leading-relaxed text-orange-800">
                {reason}
            </p>
        </div>
    );
}
