interface CitationCardProps {
    citationText: string;
    sourceNoteType: string;
}

const noteTypeLabels: Record<string, string> = {
    operative_report: "Operative Report",
    discharge_summary: "Discharge Summary",
    radiology_report: "Radiology Report",
};

export function CitationCard({ citationText, sourceNoteType }: CitationCardProps) {
    return (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
            <p className="text-[10px] font-medium uppercase tracking-wider text-amber-600">
                Source Citation
            </p>
            <p className="mt-1.5 font-mono text-sm leading-relaxed text-slate-800">
                &ldquo;{citationText}&rdquo;
            </p>
            <p className="mt-2 text-xs text-amber-600">
                From: {noteTypeLabels[sourceNoteType] || sourceNoteType}
            </p>
        </div>
    );
}
