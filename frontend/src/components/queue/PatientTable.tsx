"use client";

import Link from "next/link";
import type { PatientListItem } from "@/lib/types";
import { PatientStatusBadge, PriorityBadge } from "@/components/ui/StatusBadge";

interface PatientTableProps {
    patients: PatientListItem[];
}

export function PatientTable({ patients }: PatientTableProps) {
    if (patients.length === 0) {
        return (
            <p className="py-12 text-center text-sm text-slate-400">
                No patients match the current filter.
            </p>
        );
    }

    return (
        <div className="overflow-x-auto">
            <table className="w-full text-sm">
                <thead>
                    <tr className="border-b border-slate-200 text-left text-xs uppercase tracking-wider text-slate-500">
                        <th className="px-4 py-3 font-medium">Patient ID</th>
                        <th className="px-4 py-3 font-medium">Name</th>
                        <th className="px-4 py-3 font-medium">Age / Sex</th>
                        <th className="px-4 py-3 font-medium">Admission</th>
                        <th className="px-4 py-3 font-medium">Mechanism</th>
                        <th className="px-4 py-3 font-medium text-center">ISS</th>
                        <th className="px-4 py-3 font-medium text-center">Fields</th>
                        <th className="px-4 py-3 font-medium text-center">Auto</th>
                        <th className="px-4 py-3 font-medium text-center">Review</th>
                        <th className="px-4 py-3 font-medium">Status</th>
                        <th className="px-4 py-3 font-medium">Priority</th>
                        <th className="px-4 py-3 font-medium" />
                    </tr>
                </thead>
                <tbody>
                    {patients.map((p, i) => (
                        <tr
                            key={p.id}
                            className={`border-b border-slate-100 transition-colors hover:bg-blue-50/50 ${i % 2 === 1 ? "bg-slate-50/50" : ""
                                }`}
                        >
                            <td className="px-4 py-3 font-semibold text-slate-900">
                                {p.id}
                            </td>
                            <td className="px-4 py-3 text-slate-600">
                                {p.first_name} {p.last_name}
                            </td>
                            <td className="px-4 py-3 text-slate-600">
                                {p.age} / {p.sex}
                            </td>
                            <td className="px-4 py-3 text-slate-600">{p.admit_date}</td>
                            <td className="max-w-[180px] truncate px-4 py-3 text-slate-600">
                                {p.mechanism_of_injury}
                            </td>
                            <td className="px-4 py-3 text-center font-mono text-slate-700">
                                {p.iss}
                            </td>
                            <td className="px-4 py-3 text-center text-slate-600">
                                {p.total_extractions}
                            </td>
                            <td className="px-4 py-3 text-center text-emerald-600">
                                {p.auto_filled}
                            </td>
                            <td className="px-4 py-3 text-center">
                                {p.needs_review > 0 ? (
                                    <span className="inline-flex h-5 min-w-[20px] items-center justify-center rounded-full bg-amber-100 px-1.5 text-xs font-bold text-amber-700">
                                        {p.needs_review}
                                    </span>
                                ) : (
                                    <span className="text-slate-300">—</span>
                                )}
                            </td>
                            <td className="px-4 py-3">
                                <PatientStatusBadge status={p.status} />
                            </td>
                            <td className="px-4 py-3">
                                <PriorityBadge priority={p.priority} />
                            </td>
                            <td className="px-4 py-3 text-right">
                                <Link
                                    href={`/patient/${p.id}`}
                                    className="text-xs font-medium text-blue-600 hover:text-blue-800"
                                >
                                    Open →
                                </Link>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
