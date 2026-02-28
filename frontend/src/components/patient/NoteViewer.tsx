"use client";

import { useState } from "react";
import type { ClinicalNote } from "@/lib/types";

interface NoteViewerProps {
    notes: ClinicalNote[];
}

const noteTypeLabels: Record<string, string> = {
    operative_report: "Op Report",
    discharge_summary: "Discharge Summary",
    radiology_report: "Radiology",
};

export function NoteViewer({ notes }: NoteViewerProps) {
    const [activeIdx, setActiveIdx] = useState(0);

    if (notes.length === 0) {
        return (
            <p className="py-4 text-center text-sm text-slate-400">
                No clinical notes available.
            </p>
        );
    }

    const activeNote = notes[activeIdx];

    return (
        <div>
            <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">
                Clinical Notes
            </p>

            {/* Tabs */}
            <div className="mt-2 flex gap-1 border-b border-slate-200">
                {notes.map((note, i) => (
                    <button
                        key={note.id}
                        onClick={() => setActiveIdx(i)}
                        className={`px-3 py-2 text-xs font-medium transition-colors ${i === activeIdx
                                ? "border-b-2 border-blue-500 text-blue-600"
                                : "text-slate-400 hover:text-slate-600"
                            }`}
                    >
                        {noteTypeLabels[note.note_type] || note.note_type}
                    </button>
                ))}
            </div>

            {/* Note content */}
            <div className="mt-3 max-h-[400px] overflow-y-auto rounded-md bg-slate-50 p-4">
                <pre className="whitespace-pre-wrap font-mono text-xs leading-relaxed text-slate-700">
                    {activeNote.content}
                </pre>
            </div>
        </div>
    );
}
