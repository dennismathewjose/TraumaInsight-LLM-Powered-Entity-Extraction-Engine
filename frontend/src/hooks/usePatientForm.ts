"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
    confirmExtraction,
    correctExtraction,
    fetchPatientForm,
    fetchPatientNotes,
    updatePatientStatus,
} from "@/lib/api";
import type {
    ClinicalNote,
    FormField,
    PatientFormResponse,
} from "@/lib/types";

export function usePatientForm(patientId: string) {
    const [formData, setFormData] = useState<PatientFormResponse | null>(null);
    const [notes, setNotes] = useState<ClinicalNote[]>([]);
    const [selectedField, setSelectedField] = useState<FormField | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // ─── Fetch on mount ──────────────────────────────────────────────────

    useEffect(() => {
        let cancelled = false;
        async function load() {
            setIsLoading(true);
            setError(null);
            try {
                const [form, notesList] = await Promise.all([
                    fetchPatientForm(patientId),
                    fetchPatientNotes(patientId),
                ]);
                if (!cancelled) {
                    setFormData(form);
                    setNotes(notesList);
                }
            } catch (err) {
                if (!cancelled) {
                    setError(err instanceof Error ? err.message : "Failed to load patient data");
                }
            } finally {
                if (!cancelled) setIsLoading(false);
            }
        }
        load();
        return () => { cancelled = true; };
    }, [patientId]);

    // ─── Unresolved count ────────────────────────────────────────────────

    const unresolvedCount = useMemo(() => {
        if (!formData) return 0;
        return formData.sections.reduce(
            (acc, section) =>
                acc + section.fields.filter((f) => f.status === "review").length,
            0,
        );
    }, [formData]);

    // ─── Select a field ──────────────────────────────────────────────────

    const selectField = useCallback((field: FormField) => {
        setSelectedField(field);
    }, []);

    // ─── Helper: update field in state ───────────────────────────────────

    const updateFieldInState = useCallback(
        (fieldId: string, updater: (f: FormField) => FormField) => {
            setFormData((prev) => {
                if (!prev) return prev;
                const sections = prev.sections.map((s) => ({
                    ...s,
                    fields: s.fields.map((f) => (f.id === fieldId ? updater(f) : f)),
                }));
                // Recount summary
                const allFields = sections.flatMap((s) => s.fields);
                const summary = {
                    total_fields: allFields.length,
                    auto_filled: allFields.filter((f) => f.status === "auto").length,
                    needs_review: allFields.filter((f) => f.status === "review").length,
                    confirmed: allFields.filter((f) => f.status === "confirmed").length,
                    corrected: allFields.filter((f) => f.status === "corrected").length,
                };
                return { ...prev, sections, summary };
            });
        },
        [],
    );

    // ─── Confirm ─────────────────────────────────────────────────────────

    const confirmField = useCallback(
        async (fieldId: string) => {
            // Optimistic update
            updateFieldInState(fieldId, (f) => ({ ...f, status: "confirmed" as const }));
            setSelectedField((prev) =>
                prev?.id === fieldId ? { ...prev, status: "confirmed" as const } : prev,
            );
            try {
                await confirmExtraction(fieldId);
            } catch {
                // Rollback
                updateFieldInState(fieldId, (f) => ({ ...f, status: "review" as const }));
                setSelectedField((prev) =>
                    prev?.id === fieldId ? { ...prev, status: "review" as const } : prev,
                );
            }
        },
        [updateFieldInState],
    );

    // ─── Correct ─────────────────────────────────────────────────────────

    const correctField = useCallback(
        async (fieldId: string, value: string, fieldNotes?: string) => {
            const prevField = formData?.sections
                .flatMap((s) => s.fields)
                .find((f) => f.id === fieldId);

            // Optimistic update
            updateFieldInState(fieldId, (f) => ({
                ...f,
                status: "corrected" as const,
                extracted_value: value,
            }));
            setSelectedField((prev) =>
                prev?.id === fieldId
                    ? { ...prev, status: "corrected" as const, extracted_value: value }
                    : prev,
            );
            try {
                await correctExtraction(fieldId, value, fieldNotes);
            } catch {
                // Rollback
                if (prevField) {
                    updateFieldInState(fieldId, () => prevField);
                    setSelectedField((prev) =>
                        prev?.id === fieldId ? prevField : prev,
                    );
                }
            }
        },
        [updateFieldInState, formData],
    );

    // ─── Submit form ─────────────────────────────────────────────────────

    const submitForm = useCallback(async () => {
        await updatePatientStatus(patientId, "completed");
    }, [patientId]);

    return {
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
    };
}
