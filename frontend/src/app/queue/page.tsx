"use client";

import { useEffect, useState } from "react";
import { fetchPatients } from "@/lib/api";
import type { PatientListItem } from "@/lib/types";
import { QueueFilters } from "@/components/queue/QueueFilters";
import { PatientTable } from "@/components/queue/PatientTable";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";

export default function QueuePage() {
    const [filter, setFilter] = useState("all");
    const [patients, setPatients] = useState<PatientListItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let cancelled = false;
        async function load() {
            setIsLoading(true);
            setError(null);
            try {
                const status = filter === "all" ? undefined : filter;
                const data = await fetchPatients(status, 50);
                if (!cancelled) setPatients(data);
            } catch (err) {
                if (!cancelled)
                    setError(err instanceof Error ? err.message : "Failed to load patients");
            } finally {
                if (!cancelled) setIsLoading(false);
            }
        }
        load();
        return () => { cancelled = true; };
    }, [filter]);

    return (
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
            {/* Header */}
            <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Patient Queue</h1>
                    <p className="mt-1 text-sm text-slate-500">
                        {patients.length} patient{patients.length !== 1 ? "s" : ""} shown
                    </p>
                </div>
                <QueueFilters active={filter} onChange={setFilter} />
            </div>

            {/* Table */}
            <div className="mt-6 rounded-xl border border-slate-200 bg-white shadow-sm">
                {isLoading ? (
                    <LoadingSpinner />
                ) : error ? (
                    <div className="p-6 text-center">
                        <p className="font-medium text-red-700">Error</p>
                        <p className="mt-1 text-sm text-red-600">{error}</p>
                    </div>
                ) : (
                    <PatientTable patients={patients} />
                )}
            </div>
        </div>
    );
}
