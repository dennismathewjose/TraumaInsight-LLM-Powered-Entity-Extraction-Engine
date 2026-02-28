"use client";

import Link from "next/link";
import type { PatientListItem } from "@/lib/types";
import { PriorityBadge } from "@/components/ui/StatusBadge";

interface Props {
    patients: PatientListItem[];
}

export function PendingPatientsList({ patients }: Props) {
    if (patients.length === 0) {
        return (
            <p className="py-8 text-center text-sm text-slate-400">
                No patients pending review.
            </p>
        );
    }

    return (
        <div className="overflow-x-auto">
            <table className="w-full text-sm">
                <thead>
                    <tr className="border-b border-slate-200 text-left text-xs uppercase tracking-wider text-slate-500">
                        <th className="py-3 pr-4 font-medium">Patient</th>
                        <th className="py-3 pr-4 font-medium">Age / Sex</th>
                        <th className="py-3 pr-4 font-medium">Mechanism</th>
                        <th className="py-3 pr-4 font-medium text-center">To Review</th>
                        <th className="py-3 pr-4 font-medium">Priority</th>
                        <th className="py-3 font-medium" />
                    </tr>
                </thead>
                <tbody>
                    {patients.map((p) => (
                        <tr
                            key={p.id}
                            className="border-b border-slate-100 transition-colors hover:bg-slate-50"
                        >
                            <td className="py-3 pr-4">
                                <Link
                                    href={`/patient/${p.id}`}
                                    className="font-semibold text-blue-600 hover:underline"
                                >
                                    {p.id}
                                </Link>
                                <span className="ml-2 text-xs text-slate-400">
                                    {p.first_name} {p.last_name}
                                </span>
                            </td>
                            <td className="py-3 pr-4 text-slate-600">
                                {p.age} / {p.sex}
                            </td>
                            <td className="max-w-[200px] truncate py-3 pr-4 text-slate-600">
                                {p.mechanism_of_injury}
                            </td>
                            <td className="py-3 pr-4 text-center">
                                <span className="inline-flex h-6 min-w-[24px] items-center justify-center rounded-full bg-amber-100 px-2 text-xs font-bold text-amber-700">
                                    {p.needs_review}
                                </span>
                            </td>
                            <td className="py-3 pr-4">
                                <PriorityBadge priority={p.priority} />
                            </td>
                            <td className="py-3 text-right">
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
