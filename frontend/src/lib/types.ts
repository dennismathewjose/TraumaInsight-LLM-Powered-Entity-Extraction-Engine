// ─── Overview Stats (GET /api/stats/overview) ─────────────────────────────

export interface OverviewStats {
  total_patients: number;
  pending_review: number;
  completed: number;
  total_extractions: number;
  auto_filled: number;
  needs_review: number;
  reviewed: number;
  auto_fill_rate: number;
  avg_confidence: number;
  estimated_time_saved_minutes: number;
}

// ─── Patient ───────────────────────────────────────────────────────────────

export interface PatientListItem {
  id: string;
  first_name: string;
  last_name: string;
  age: number;
  sex: string;
  admit_date: string;
  discharge_date: string | null;
  mechanism_of_injury: string;
  iss: number;
  los: number;
  status: "pending" | "review" | "completed";
  priority: "high" | "medium" | "low";
  total_extractions: number;
  auto_filled: number;
  needs_review: number;
}

export interface PatientDetail extends PatientListItem {
  synthea_id: string;
  created_at: string;
  updated_at: string | null;
}

// ─── Registry Form ─────────────────────────────────────────────────────────

export type FieldStatus = "auto" | "review" | "confirmed" | "corrected";

export interface ReviewDecision {
  id: string;
  extraction_id: string;
  reviewer_id: string | null;
  decision: string;
  corrected_value: string | null;
  notes: string | null;
  decided_at: string;
}

export interface FormField {
  id: string;
  field_key: string;
  field_label: string;
  extracted_value: string;
  confidence_score: number;
  status: FieldStatus;
  citation_text: string | null;
  source_note_type: string | null;
  conflict_reason: string | null;
  review_decision: ReviewDecision | null;
}

export interface FormSection {
  title: string;
  fields: FormField[];
}

export interface FormSummary {
  total_fields: number;
  auto_filled: number;
  needs_review: number;
  confirmed: number;
  corrected: number;
}

export interface PatientFormResponse {
  patient: PatientDetail;
  sections: FormSection[];
  summary: FormSummary;
}

// ─── Clinical Notes ────────────────────────────────────────────────────────

export interface ClinicalNote {
  id: string;
  patient_id: string;
  note_type: string;
  content: string;
  author_role: string;
  note_date: string;
  created_at: string;
}
