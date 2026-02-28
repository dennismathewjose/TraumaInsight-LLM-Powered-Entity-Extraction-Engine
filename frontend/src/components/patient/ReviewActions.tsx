"use client";

import { useState } from "react";

interface ReviewActionsProps {
    onConfirm: () => Promise<void>;
    onCorrect: (value: string, notes?: string) => Promise<void>;
}

export function ReviewActions({ onConfirm, onCorrect }: ReviewActionsProps) {
    const [mode, setMode] = useState<"idle" | "correcting">("idle");
    const [correctedValue, setCorrectedValue] = useState("");
    const [correctedNotes, setCorrectedNotes] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleConfirm = async () => {
        setIsSubmitting(true);
        await onConfirm();
        setIsSubmitting(false);
    };

    const handleCorrect = async () => {
        if (!correctedValue.trim()) return;
        setIsSubmitting(true);
        await onCorrect(correctedValue.trim(), correctedNotes.trim() || undefined);
        setIsSubmitting(false);
        setMode("idle");
    };

    if (mode === "correcting") {
        return (
            <div className="space-y-3 rounded-lg border border-violet-200 bg-violet-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-wider text-violet-600">
                    Enter Corrected Value
                </p>
                <input
                    type="text"
                    value={correctedValue}
                    onChange={(e) => setCorrectedValue(e.target.value)}
                    placeholder="Corrected value…"
                    className="w-full rounded-md border border-violet-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500"
                    aria-label="Corrected value"
                    autoFocus
                />
                <textarea
                    value={correctedNotes}
                    onChange={(e) => setCorrectedNotes(e.target.value)}
                    placeholder="Optional notes…"
                    rows={2}
                    className="w-full rounded-md border border-violet-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500"
                    aria-label="Correction notes"
                />
                <div className="flex gap-2">
                    <button
                        onClick={handleCorrect}
                        disabled={isSubmitting || !correctedValue.trim()}
                        className="rounded-md bg-violet-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-violet-700 disabled:opacity-50"
                    >
                        {isSubmitting ? "Saving…" : "Save Correction"}
                    </button>
                    <button
                        onClick={() => setMode("idle")}
                        className="rounded-md px-4 py-2 text-sm font-medium text-slate-500 hover:text-slate-700"
                    >
                        Cancel
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="flex gap-3">
            <button
                onClick={handleConfirm}
                disabled={isSubmitting}
                className="flex-1 rounded-md bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-emerald-700 disabled:opacity-50"
                aria-label="Confirm extraction value"
            >
                {isSubmitting ? "Confirming…" : "✓ Confirm as Correct"}
            </button>
            <button
                onClick={() => setMode("correcting")}
                className="flex-1 rounded-md bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-violet-700"
                aria-label="Correct extraction value"
            >
                ✎ Correct Value
            </button>
        </div>
    );
}
