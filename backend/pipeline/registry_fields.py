"""Registry field definitions — queries and extraction prompts."""

from __future__ import annotations

REGISTRY_FIELDS: list[dict[str, str]] = [
    # ── INJURIES ────────────────────────────────────────────────────────
    {
        "field_key": "primary_injury",
        "field_label": "Primary Injury",
        "section": "injuries",
        "query": (
            "What is the primary traumatic injury or diagnosis for this "
            "patient? Include the specific type, location, and grade if documented."
        ),
        "extraction_prompt": (
            "Based on the clinical text excerpts below, identify the PRIMARY "
            "traumatic injury. Include the injury type (e.g., laceration, "
            "fracture, contusion), anatomical location, and grade/severity "
            "if mentioned.\n\nExcerpts:\n{passages}\n\n"
            'Respond in JSON:\n{{"value": "brief description of primary '
            'injury", "citation": "exact quote from the text that supports '
            'your answer", "reasoning": "brief explanation"}}'
        ),
    },
    {
        "field_key": "primary_injury_grade",
        "field_label": "Primary Injury — AIS/Grade",
        "section": "injuries",
        "query": (
            "What is the injury severity grade or AIS score for the primary "
            "injury? Look for AAST grades, AIS scores, or severity classifications."
        ),
        "extraction_prompt": (
            "Based on the clinical text excerpts below, identify the severity "
            "grade or AIS score for the primary injury. Look for terms like "
            "'Grade I/II/III/IV/V', 'AIS score', 'AAST grade', "
            "'mild/moderate/severe'.\n\nExcerpts:\n{passages}\n\n"
            'Respond in JSON:\n{{"value": "grade or severity (e.g., Grade III, '
            'AIS 4)", "citation": "exact quote that states the grade", '
            '"reasoning": "brief explanation"}}'
        ),
    },
    {
        "field_key": "secondary_injury",
        "field_label": "Secondary Injury",
        "section": "injuries",
        "query": (
            "Are there any secondary or additional injuries besides the primary "
            "injury? Look for other fractures, lacerations, organ injuries, or "
            "traumatic findings."
        ),
        "extraction_prompt": (
            "Based on the clinical text excerpts below, identify any SECONDARY "
            "injuries (injuries other than the primary one). If no secondary "
            "injuries exist, say 'None documented'.\n\nExcerpts:\n{passages}\n\n"
            'Respond in JSON:\n{{"value": "description of secondary injury or '
            "'None documented'\", \"citation\": \"exact quote if found, or "
            "'No secondary injury documented'\", \"reasoning\": \"brief "
            'explanation"}}'
        ),
    },
    # ── PROCEDURES ──────────────────────────────────────────────────────
    {
        "field_key": "primary_procedure",
        "field_label": "Primary Procedure",
        "section": "procedures",
        "query": (
            "What surgical procedures or interventions were performed on this "
            "patient? Include the procedure name, type, and approach."
        ),
        "extraction_prompt": (
            "Based on the clinical text excerpts below, identify the PRIMARY "
            "surgical procedure performed. Include the procedure name and "
            "approach (e.g., 'Exploratory laparotomy with splenectomy', "
            "'ORIF of left femur').\n\nExcerpts:\n{passages}\n\n"
            'Respond in JSON:\n{{"value": "procedure name and approach", '
            '"citation": "exact quote describing the procedure", '
            '"reasoning": "brief explanation"}}'
        ),
    },
    # ── COMPLICATIONS ───────────────────────────────────────────────────
    {
        "field_key": "complication_ssi",
        "field_label": "Complication — Surgical Site Infection",
        "section": "complications",
        "query": (
            "Did this patient develop a surgical site infection (SSI) during "
            "this hospitalization? Look for wound infection, surgical wound "
            "complications, cellulitis at incision site, or positive wound cultures."
        ),
        "extraction_prompt": (
            "Based on the clinical text excerpts below, determine if the "
            "patient developed a Surgical Site Infection (SSI) during this "
            "encounter. Look for: wound infection, incisional infection, "
            "cellulitis at surgical site, positive wound cultures, or terms "
            "like 'SSI'. IMPORTANT: Also check for NEGATION — phrases like "
            "'no signs of infection', 'wound healing well', 'no SSI' mean "
            "the answer is No.\n\nExcerpts:\n{passages}\n\n"
            "Respond in JSON:\n{{\"value\": \"Yes — [details]\" or \"No\", "
            '"citation": "exact quote supporting your answer", '
            '"reasoning": "brief explanation including any negation detected"}}'
        ),
    },
    {
        "field_key": "complication_sepsis",
        "field_label": "Complication — Sepsis",
        "section": "complications",
        "query": (
            "Did this patient develop sepsis during this hospitalization? "
            "Look for sepsis, bacteremia, SIRS criteria, positive blood "
            "cultures, septic shock, or systemic infection."
        ),
        "extraction_prompt": (
            "Based on the clinical text excerpts below, determine if the "
            "patient developed Sepsis during this encounter. Look for: "
            "sepsis diagnosis, bacteremia, SIRS criteria met, positive blood "
            "cultures, septic shock. IMPORTANT: Check for NEGATION — "
            "'no signs of sepsis', 'blood cultures negative' mean No. "
            "Also distinguish between localized infection (SSI/UTI/pneumonia) "
            "and systemic sepsis.\n\nExcerpts:\n{passages}\n\n"
            "Respond in JSON:\n{{\"value\": \"Yes — [details]\" or \"No\" or "
            "\"Uncertain — [reason]\", \"citation\": \"exact quote supporting "
            'your answer", "reasoning": "brief explanation"}}'
        ),
    },
    {
        "field_key": "complication_vte",
        "field_label": "Complication — DVT/PE",
        "section": "complications",
        "query": (
            "Did this patient develop a venous thromboembolism (DVT or PE) "
            "during this hospitalization? Look for deep vein thrombosis, "
            "pulmonary embolism, blood clots, VTE, or anticoagulation for "
            "clot treatment."
        ),
        "extraction_prompt": (
            "Based on the clinical text excerpts below, determine if the "
            "patient developed DVT (Deep Vein Thrombosis) or PE (Pulmonary "
            "Embolism) during this encounter. IMPORTANT: Check for NEGATION "
            "— 'no evidence of DVT or PE', 'negative duplex ultrasound' mean "
            "No. Prophylactic anticoagulation does NOT mean the patient had "
            "VTE.\n\nExcerpts:\n{passages}\n\n"
            "Respond in JSON:\n{{\"value\": \"Yes — [DVT/PE details]\" or "
            '"No", "citation": "exact quote supporting your answer", '
            '"reasoning": "brief explanation"}}'
        ),
    },
    # ── SEVERITY ────────────────────────────────────────────────────────
    {
        "field_key": "initial_gcs",
        "field_label": "Initial GCS Score",
        "section": "severity",
        "query": (
            "What was the patient's initial Glasgow Coma Scale (GCS) score on "
            "arrival or initial assessment? Look for GCS, Glasgow Coma Scale, "
            "or level of consciousness assessment."
        ),
        "extraction_prompt": (
            "Based on the clinical text excerpts below, identify the patient's "
            "initial GCS (Glasgow Coma Scale) score. This should be the FIRST "
            "GCS documented, typically on arrival to the ED or trauma bay. "
            "If no GCS is documented, say 'Not documented'.\n\n"
            "Excerpts:\n{passages}\n\n"
            'Respond in JSON:\n{{"value": "numeric GCS score (e.g., 14) or '
            "'Not documented'\", \"citation\": \"exact quote mentioning GCS\", "
            '"reasoning": "brief explanation"}}'
        ),
    },
    # ── DISCHARGE ───────────────────────────────────────────────────────
    {
        "field_key": "hospital_los",
        "field_label": "Hospital Length of Stay",
        "section": "discharge",
        "query": (
            "What was the patient's total hospital length of stay? Look for "
            "admission date, discharge date, total days in hospital, or LOS."
        ),
        "extraction_prompt": (
            "Based on the clinical text excerpts below, determine the patient's "
            "total hospital length of stay in days. Calculate from admission to "
            "discharge dates if both are available.\n\nExcerpts:\n{passages}\n\n"
            'Respond in JSON:\n{{"value": "X days" or "Not documented", '
            '"citation": "exact quote with dates or LOS mention", '
            '"reasoning": "brief explanation of calculation if applicable"}}'
        ),
    },
]
