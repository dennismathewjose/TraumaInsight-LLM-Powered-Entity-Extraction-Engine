"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchPatients, fetchStats } from "@/lib/api";
import type { OverviewStats, PatientListItem } from "@/lib/types";
import { StatCard } from "@/components/dashboard/StatCard";
import { PendingPatientsList } from "@/components/dashboard/PendingPatientsList";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";

export default function DashboardPage() {
    const [stats, setStats] = useState<OverviewStats | null>(null);
    const [patients, setPatients] = useState<PatientListItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function load() {
            try {
                const [s, p] = await Promise.all([
                    fetchStats(),
                    fetchPatients("pending", 10),
                ]);
                setStats(s);
                setPatients(p);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load dashboard");
            } finally {
                setIsLoading(false);
            }
        }
        load();
    }, []);

    if (isLoading) return <LoadingSpinner />;

    if (error) {
        return (
            <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6">
                <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center">
                    <p className="font-medium text-red-700">Error loading dashboard</p>
                    <p className="mt-1 text-sm text-red-600">{error}</p>
                </div>
            </div>
        );
    }

    if (!stats) return null;

    return (
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
            {/* Page title */}
            <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
            <p className="mt-1 text-sm text-slate-500">
                Trauma registry overview and pending patient reviews
            </p>

            {/* Stat cards */}
            <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
                <StatCard label="Total Patients" value={stats.total_patients} />
                <StatCard
                    label="Pending Review"
                    value={stats.pending_review}
                    color="amber"
                />
                <StatCard
                    label="Completed"
                    value={stats.completed}
                    color="emerald"
                />
                <StatCard
                    label="Fields Auto-Filled"
                    value={`${stats.auto_filled} / ${stats.total_extractions}`}
                />
                <StatCard
                    label="Auto-Fill Rate"
                    value={`${stats.auto_fill_rate}%`}
                    color="blue"
                />
                <StatCard
                    label="Est. Time Saved"
                    value={`${stats.estimated_time_saved_minutes} min`}
                    color="emerald"
                />
            </div>

            {/* Pending patients */}
            <div className="mt-8">
                <div className="flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-slate-900">
                        Patients Needing Review
                    </h2>
                    <Link
                        href="/queue"
                        className="text-sm font-medium text-blue-600 hover:text-blue-800"
                    >
                        View Full Patient Queue →
                    </Link>
                </div>

                <div className="mt-4 rounded-xl border border-slate-200 bg-white p-1 shadow-sm">
                    <PendingPatientsList patients={patients} />
                </div>
            </div>
        </div>
    );
}
