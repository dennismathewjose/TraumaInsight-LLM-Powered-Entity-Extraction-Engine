"use client";

import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { usePatientForm } from "@/hooks/usePatientForm";
import { PatientHeader } from "@/components/patient/PatientHeader";
import { RegistryForm } from "@/components/patient/RegistryForm";
import { EvidencePanel } from "@/components/patient/EvidencePanel";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";

export default function PatientPage() {
    const params = useParams<{ id: string }>();
    const router = useRouter();
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitSuccess, setSubmitSuccess] = useState(false);

    const {
        formData,
        notes,
        selectedField,
        selectField,
        confirmField,
        correctField,
        unresolvedCount,
        submitForm,
        isLoading,
        error,
    } = usePatientForm(params.id);

    const handleSubmit = async () => {
        setIsSubmitting(true);
        try {
            await submitForm();
            setSubmitSuccess(true);
            setTimeout(() => router.push("/queue"), 1500);
        } catch {
            setIsSubmitting(false);
        }
    };

    if (isLoading) return <LoadingSpinner />;

    if (error) {
        return (
            <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6">
                <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center">
                    <p className="font-medium text-red-700">Error loading patient</p>
                    <p className="mt-1 text-sm text-red-600">{error}</p>
                </div>
            </div>
        );
    }

    if (!formData) return null;

    if (submitSuccess) {
        return (
            <div className="flex min-h-[60vh] items-center justify-center">
                <div className="text-center">
                    <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
                        <span className="text-3xl">✓</span>
                    </div>
                    <p className="mt-4 text-lg font-semibold text-emerald-700">
                        Submitted to Registry
                    </p>
                    <p className="mt-1 text-sm text-slate-500">
                        Redirecting to queue…
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div>
            <PatientHeader
                patient={formData.patient}
                unresolvedCount={unresolvedCount}
                onSubmit={handleSubmit}
                isSubmitting={isSubmitting}
            />

            {/* Two-panel layout */}
            <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6">
                <div className="flex flex-col gap-4 lg:flex-row">
                    {/* Left: Registry Form */}
                    <div className="w-full overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm lg:w-[55%]">
                        <RegistryForm
                            sections={formData.sections}
                            selectedFieldId={selectedField?.id || null}
                            onSelectField={selectField}
                        />
                    </div>

                    {/* Right: Evidence Panel */}
                    <div className="w-full overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm lg:sticky lg:top-[140px] lg:w-[45%] lg:self-start lg:max-h-[calc(100vh-160px)] lg:overflow-y-auto">
                        <EvidencePanel
                            field={selectedField}
                            notes={notes}
                            onConfirm={confirmField}
                            onCorrect={correctField}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
