import type {
    ClinicalNote,
    FormField,
    OverviewStats,
    PatientFormResponse,
    PatientListItem,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Error class ───────────────────────────────────────────────────────────

export class ApiError extends Error {
    status: number;
    constructor(message: string, status: number) {
        super(message);
        this.name = "ApiError";
        this.status = status;
    }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options?.headers,
        },
    });
    if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: res.statusText }));
        throw new ApiError(body.detail || res.statusText, res.status);
    }
    return res.json() as Promise<T>;
}

// ─── Dashboard ─────────────────────────────────────────────────────────────

export function fetchStats(): Promise<OverviewStats> {
    return request<OverviewStats>("/api/stats/overview");
}

// ─── Patient list ──────────────────────────────────────────────────────────

export function fetchPatients(
    status?: string,
    limit = 20,
    offset = 0,
): Promise<PatientListItem[]> {
    const params = new URLSearchParams();
    if (status) params.set("status", status);
    params.set("limit", String(limit));
    params.set("offset", String(offset));
    return request<PatientListItem[]>(`/api/patients?${params}`);
}

// ─── Patient form ──────────────────────────────────────────────────────────

export function fetchPatientForm(
    patientId: string,
): Promise<PatientFormResponse> {
    return request<PatientFormResponse>(`/api/patients/${patientId}/form`);
}

// ─── Clinical notes ────────────────────────────────────────────────────────

export function fetchPatientNotes(
    patientId: string,
): Promise<ClinicalNote[]> {
    return request<ClinicalNote[]>(`/api/patients/${patientId}/notes`);
}

// ─── Extraction review ────────────────────────────────────────────────────

export function confirmExtraction(extractionId: string): Promise<FormField> {
    return request<FormField>(`/api/extractions/${extractionId}/confirm`, {
        method: "POST",
    });
}

export function correctExtraction(
    extractionId: string,
    correctedValue: string,
    notes?: string,
): Promise<FormField> {
    return request<FormField>(`/api/extractions/${extractionId}/correct`, {
        method: "POST",
        body: JSON.stringify({ corrected_value: correctedValue, notes }),
    });
}

// ─── Patient status ────────────────────────────────────────────────────────

export function updatePatientStatus(
    patientId: string,
    status: string,
): Promise<void> {
    return request(`/api/patients/${patientId}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
    });
}
