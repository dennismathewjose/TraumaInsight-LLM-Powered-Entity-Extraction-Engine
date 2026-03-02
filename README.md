<div align="center">

# TraumaInsight

### LLM-Powered Entity Extraction Engine for Trauma Registry Abstraction

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.134-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?logo=next.js&logoColor=white)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-1A1A2E)](https://ollama.com)

*Automate trauma registry chart abstraction with local RAG-based AI — no data leaves the hospital.*

</div>

---

##  Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Database Setup](#database-setup)
  - [Running the Application](#running-the-application)
- [RAG Extraction Pipeline](#rag-extraction-pipeline)
  - [Pipeline Data Flow](#pipeline-data-flow)
  - [Running the Pipeline](#running-the-pipeline)
  - [Registry Fields](#registry-fields)
- [API Reference](#api-reference)
- [Frontend](#frontend)
- [Data Model](#data-model)
- [Configuration](#configuration)

---

## Overview

**TraumaInsight** is a clinical AI application that automates **trauma registry chart abstraction** — the labor-intensive process of reading clinical notes and extracting standardized data fields for every trauma patient.

Trauma registrars at hospitals spend hours manually reviewing operative reports, discharge summaries, and radiology reports to fill out registry forms. TraumaInsight uses a **local RAG (Retrieval-Augmented Generation) pipeline** to:

1. **Read** clinical notes from the EHR
2. **Retrieve** relevant passages using vector similarity search
3. **Extract** structured data using a local LLM (Llama 3)
4. **Validate** extractions with clinical NLP negation detection
5. **Score** confidence and flag uncertain fields for human review

The registrar then reviews only the flagged fields — typically 20–30% of the total — dramatically reducing abstraction time.

> **Privacy-first design:** All processing runs locally via Ollama. No patient data is sent to external APIs.

---

## Key Features

| Feature | Description |
|---------|-------------|
|  **RAG Extraction** | Retrieval-Augmented Generation using ChromaDB + Llama 3 for context-aware extraction |
|  **Negation Detection** | medspaCy-based clinical NLP to catch "no signs of infection" vs. "infection" |
|  **Confidence Scoring** | 4-factor scoring (retrieval quality, assertion clarity, cross-document agreement, negation consistency) |
|  **9 Registry Fields** | Injuries, procedures, complications, severity, and discharge data |
|  **Review Interface** | Two-panel form with evidence panel showing AI reasoning & source citations |
|  **Confirm / Correct** | Registrars can approve or override AI extractions with one click |
|  **MIMIC-IV Compatible** | Built for synthetic clinical data; works with MIMIC-IV format |
|  **Fully Local** | Ollama LLM + local PostgreSQL + local ChromaDB — zero external API calls |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        TraumaInsight Architecture                   │
├────────────────────┬────────────────────┬───────────────────────────┤
│                    │                    │                           │
│   Next.js Frontend │   FastAPI Backend  │   RAG Pipeline            │
│   (Port 3000)      │   (Port 8000)      │                           │
│                    │                    │                           │
│ ┌────────────────┐ │ ┌────────────────┐ │ ┌───────────────────────┐ │
│ │ Dashboard      │ │ │ /api/patients  │ │ │ Embedder              │ │
│ │ Patient Queue  │◄┼─┤ /api/stats     │ │ │ (nomic-embed-text)    │ │
│ │ Registry Form  │ │ │ /api/notes     │ │ │         │             │ │
│ │ Evidence Panel │ │ │ /api/pipeline  │◄┼─┤         ▼             │ │
│ └────────────────┘ │ │ /api/reviews   │ │ │ ChromaDB (Vector DB)  │ │
│                    │ └───────┬────────┘ │ │         │             │ │
│                    │         │          │ │         ▼             │ │
│                    │    ┌────▼─────┐    │ │ Retriever → Extractor │ │
│                    │    │PostgreSQL│    │ │ (Ollama / Llama 3)    │ │
│                    │    │  + Seed  │    │ │         │             │ │
│                    │    │   Data   │    │ │         ▼             │ │
│                    │    └──────────┘    │ │ Negation → Scorer     │ │
│                    │                    │ │ (medspaCy)            │ │
│                    │                    │ └───────────────────────┘ │
└────────────────────┴────────────────────┴───────────────────────────┘
```

---

## Tech Stack

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Runtime |
| FastAPI | 0.134 | Async REST API |
| SQLAlchemy | 2.0 | ORM (async + sync) |
| PostgreSQL | 16 | Primary database |
| Alembic | 1.18 | Database migrations |
| Pydantic | 2.12 | Data validation |

### RAG Pipeline
| Technology | Version | Purpose |
|-----------|---------|---------|
| Ollama | latest | Local LLM runtime |
| Llama 3 | 8B (Q4_0) | Text extraction |
| nomic-embed-text | — | Embedding model (768-dim) |
| BioMistral | 7B | Alternative clinical model |
| ChromaDB | 1.5 | Vector store (persistent) |
| medspaCy | 1.3 | Clinical NLP / negation detection |
| spaCy | 3.8 | NLP backbone |

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | 16 | React framework (App Router) |
| TypeScript | 5 | Type safety |
| Tailwind CSS | 4 | Styling (custom theme tokens) |
| React | 19 | UI components |

---

## Project Structure

```
TraumaInsight-LLM-Powered-Entity-Extraction-Engine/
├── .env                          # Environment variables
├── docker-compose.yml            # PostgreSQL container
├── README.md                     # This file
│
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI application entry point
│   │   ├── config.py             # Settings (pydantic-settings)
│   │   ├── database.py           # SQLAlchemy engine + session factory
│   │   ├── models/               # ORM models
│   │   │   ├── patient.py        #   Patient demographics
│   │   │   ├── encounter.py      #   Hospital encounters
│   │   │   ├── clinical_note.py  #   Clinical notes (3 types)
│   │   │   ├── extraction.py     #   AI extraction results
│   │   │   └── review_decision.py#   Human review decisions
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   └── api/                  # API route handlers
│   │       ├── patients.py       #   GET /api/patients, /api/stats
│   │       ├── notes.py          #   GET /api/patients/{id}/notes
│   │       ├── extractions.py    #   GET /api/patients/{id}/form
│   │       ├── reviews.py        #   POST confirm/correct/submit
│   │       └── pipeline.py       #   POST /api/pipeline/run/{id}
│   │
│   ├── pipeline/                 # RAG extraction pipeline
│   │   ├── config.py             #   Pipeline-specific settings
│   │   ├── registry_fields.py    #   9 field definitions + prompts
│   │   ├── embedder.py           #   Chunk + embed → ChromaDB
│   │   ├── retriever.py          #   RAG query → ranked passages
│   │   ├── extractor.py          #   Ollama LLM → structured JSON
│   │   ├── negation_handler.py   #   medspaCy negation detection
│   │   ├── confidence_scorer.py  #   4-factor weighted scoring
│   │   ├── citation_builder.py   #   Fuzzy-match source citations
│   │   └── orchestrator.py       #   End-to-end pipeline per patient
│   │
│   ├── scripts/
│   │   ├── load_synthea.py       #   Load Synthea FHIR data
│   │   ├── generate_notes.py     #   Generate clinical notes via LLM
│   │   ├── seed_extractions.py   #   Seed extraction data
│   │   └── run_pipeline.py       #   CLI pipeline runner
│   │
│   ├── alembic/                  # Database migrations
│   └── tests/                    # pytest test suite
│
├── frontend/
│   └── src/
│       ├── app/                  # Next.js App Router pages
│       │   ├── dashboard/        #   Dashboard (stats + pending list)
│       │   ├── queue/            #   Patient queue (filters + table)
│       │   └── patient/[id]/     #   Registry form (two-panel layout)
│       ├── components/           # React components (16 total)
│       │   ├── nav/              #   Navbar
│       │   ├── dashboard/        #   StatCard, PendingPatientsList
│       │   ├── queue/            #   QueueFilters, PatientTable
│       │   ├── patient/          #   FormField, EvidencePanel, etc.
│       │   └── ui/               #   ConfidenceDot, StatusBadge, etc.
│       ├── hooks/                # usePatientForm custom hook
│       └── lib/                  # API client + TypeScript types
│
└── data/                         # Synthea-generated patient data
```

---

## Getting Started

### Prerequisites

| Requirement | Install |
|------------|---------|
| Python 3.11+ | [python.org](https://www.python.org/downloads/) |
| Node.js 18+ | [nodejs.org](https://nodejs.org/) |
| Docker | [docker.com](https://www.docker.com/get-started/) |
| Ollama | [ollama.com](https://ollama.com/download) |

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/dennismathewjose/TraumaInsight-LLM-Powered-Entity-Extraction-Engine.git
cd TraumaInsight-LLM-Powered-Entity-Extraction-Engine
```

**2. Set up the Python virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Pull Required Ollama Models**
```bash
ollama pull llama3
ollama pull nomic-embed-text
ollama pull cniongolo/biomistral   # optional — clinical alternative
```

**4. Install frontend dependencies**
```bash
cd frontend
npm install
cd ..
```

### Database Setup

**1. Start PostgreSQL via Docker**
```bash
docker-compose up -d
```
This creates a PostgreSQL 16 instance at `localhost:5432` with credentials `traumainsight / traumainsight_dev`.

**2. Run database migrations**
```bash
cd backend
alembic upgrade head
```

**3. Load seed data**
```bash
# Load Synthea patient data
python scripts/load_synthea.py

# Generate clinical notes using LLM
python scripts/generate_notes.py

# Seed initial extraction data
python scripts/seed_extractions.py
```

### Running the Application

Open **three terminal windows:**

```bash
# Terminal 1 — Ollama LLM server
ollama serve

# Terminal 2 — Backend API (http://localhost:8000)
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 3 — Frontend (http://localhost:3000)
cd frontend
npm run dev
```

Then open **http://localhost:3000** in your browser.

---

## RAG Extraction Pipeline

### Pipeline Data Flow

```
PostgreSQL (clinical_notes)
        │
        ▼
┌─────────────────┐
│   Embedder       │  Chunk notes → 300-token windows (50 overlap)
│   nomic-embed-   │  Embed via Ollama → store in ChromaDB
│   text (768-dim) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Retriever      │  Embed field query → cosine similarity search
│   ChromaDB       │  Filter by patient_id → return top-5 passages
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Extractor      │  Format passages → send to Llama 3
│   Ollama/Llama3  │  System prompt enforces JSON output
│   temp=0.1       │  Parse {value, citation, reasoning}
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Negation       │  medspaCy ConText + rule-based patterns
│   Handler        │  Detect: "no SSI" vs "SSI present"
│   (medspaCy)     │  Flag conflicts with extracted value
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Confidence     │  4-factor weighted score (0.0 – 1.0):
│   Scorer         │    • Retrieval quality   (30%)
│                  │    • Assertion clarity    (30%)
│                  │    • Cross-doc agreement  (20%)
│                  │    • Negation consistency (20%)
│                  │  ≥0.85 → auto  |  ≥0.60 → review
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Citation       │  Fuzzy-match LLM citation against passages
│   Builder        │  Identify source note type
│                  │  Fallback if citation hallucinated
└────────┬────────┘
         │
         ▼
    PostgreSQL (extractions table)
```

### Running the Pipeline

**Via CLI:**
```bash
cd backend

# Process one patient
python scripts/run_pipeline.py --patient P-10001

# Process first 5 patients
python scripts/run_pipeline.py --limit 5

# Process all 68 patients
python scripts/run_pipeline.py --all

# Use BioMistral instead of Llama 3
python scripts/run_pipeline.py --patient P-10001 --model cniongolo/biomistral
```

**Via API:**
```bash
# Single patient
curl -X POST http://localhost:8000/api/pipeline/run/P-10001

# All patients (with optional limit)
curl -X POST "http://localhost:8000/api/pipeline/run-all?limit=5&model=llama3"
```

**Expected output:**
```
============================================================
  TraumaInsight — RAG Extraction Pipeline
============================================================

Processing patient P-10001 with model llama3...
  Embedding clinical notes...
  Embedded 5 chunks from 3 notes for P-10001
  [1/9] primary_injury: Fracture of bone (disorder) (0.77, review)
  [2/9] primary_injury_grade: AIS 14 (0.81, review)
  [3/9] secondary_injury: Fracture of rib (disorder) (0.74, review)
  [4/9] primary_procedure: Exploratory laparotomy with splenectomy (0.75, review)
  [5/9] complication_ssi: No (0.76, review)
  [6/9] complication_sepsis: No (0.76, review)
  [7/9] complication_vte: No (0.77, review)
  [8/9] initial_gcs: Not documented (0.57, review)
  [9/9] hospital_los: 4781 days (0.72, review)

Pipeline complete for P-10001:
  Total fields: 9
  Auto-accepted: 0 (0.0%)
  Needs review: 9 (100.0%)
  Time: 405.7s
```

### Registry Fields

The pipeline extracts 9 standardized fields across 5 sections:

| Section | Field | Description |
|---------|-------|-------------|
| **Injuries** | Primary Injury | Main traumatic diagnosis (type + location) |
| | AIS/Grade | Injury severity (AAST grade, AIS score) |
| | Secondary Injury | Additional injuries beyond primary |
| **Procedures** | Primary Procedure | Main surgical intervention performed |
| **Complications** | SSI | Surgical Site Infection (Yes/No) |
| | Sepsis | Systemic sepsis (Yes/No/Uncertain) |
| | DVT/PE | Venous thromboembolism (Yes/No) |
| **Severity** | Initial GCS | Glasgow Coma Scale on arrival |
| **Discharge** | Hospital LOS | Length of stay in days |

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/stats` | Dashboard overview statistics |
| `GET` | `/api/patients` | List all patients with status |
| `GET` | `/api/patients/{id}/form` | Get extraction form for a patient |
| `GET` | `/api/patients/{id}/notes` | Get clinical notes for a patient |
| `POST` | `/api/extractions/{id}/confirm` | Confirm an AI extraction as correct |
| `POST` | `/api/extractions/{id}/correct` | Correct an AI extraction value |
| `POST` | `/api/patients/{id}/submit` | Submit all reviewed extractions |
| `POST` | `/api/pipeline/run/{id}` | Run extraction pipeline for a patient |
| `POST` | `/api/pipeline/run-all` | Run pipeline for all patients |

Full interactive docs at **http://localhost:8000/docs** (Swagger UI).

---

## Frontend

### Pages

| Page | Route | Description |
|------|-------|-------------|
| **Dashboard** | `/dashboard` | Overview stats, pending patient list |
| **Patient Queue** | `/queue` | Full patient table with All/Pending/Completed filters |
| **Registry Form** | `/patient/[id]` | Two-panel layout: form (left) + evidence (right) |

### Key Interactions

- **Click a field** → Evidence panel shows AI answer, confidence %, source citation, and conflict alerts
- **Confirm** → Accept the AI extraction (field turns green)
- **Correct** → Override with a manual value (field turns purple)
- **Submit** → Finalize all reviewed fields and update patient status

---

## Data Model

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Patient    │────▶│  Encounter   │     │  ClinicalNote    │
│              │     │              │     │                  │
│ id (PK)      │     │ id (PK)      │     │ id (PK)          │
│ first_name   │     │ patient_id   │     │ patient_id (FK)  │
│ last_name    │     │ admit_date   │     │ note_type        │
│ date_of_birth│     │ discharge_dt │     │ content (TEXT)    │
│ gender       │     │ injury_type  │     │ generated_at     │
│ status       │     │ priority     │     └──────────────────┘
└──────┬───────┘     └──────────────┘
       │
       │     ┌──────────────────┐     ┌──────────────────┐
       └────▶│   Extraction     │────▶│ ReviewDecision   │
             │                  │     │                  │
             │ id (PK)          │     │ id (PK)          │
             │ patient_id (FK)  │     │ extraction_id(FK)│
             │ field_key        │     │ decision_type    │
             │ extracted_value  │     │ corrected_value  │
             │ confidence_score │     │ decided_at       │
             │ status           │     └──────────────────┘
             │ citation_text    │
             │ conflict_reason  │
             │ extraction_method│
             └──────────────────┘
```

**Note types:** `operative_report`, `discharge_summary`, `radiology_report`

**Extraction statuses:** `auto` → `confirmed` | `review` → `confirmed` / `corrected`

---

## Configuration

### Environment Variables (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://traumainsight:traumainsight_dev@localhost:5432/traumainsight` | PostgreSQL connection |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `LLM_MODEL` | `llama3` | Default LLM model |
| `CHROMA_PERSIST_DIR` | `./chromadb_data` | ChromaDB storage path |
| `APP_ENV` | `development` | Application environment |
| `APP_PORT` | `8000` | Backend API port |
| `FRONTEND_URL` | `http://localhost:3000` | Frontend URL (CORS) |

### Pipeline Configuration (`backend/pipeline/config.py`)

| Setting | Value | Description |
|---------|-------|-------------|
| `CHUNK_SIZE` | 300 tokens | Approximate tokens per chunk |
| `CHUNK_OVERLAP` | 50 tokens | Overlap between chunks |
| `TOP_K_PASSAGES` | 5 | Passages retrieved per query |
| `AUTO_ACCEPT_THRESHOLD` | 0.85 | Auto-accept confidence threshold |
| `REVIEW_THRESHOLD` | 0.60 | Minimum for review (below = high priority) |
| `LLM_TEMPERATURE` | 0.1 | Low temperature for factual extraction |

---

<div align="center">

** For trauma registrars**

*Reducing chart abstraction time so clinicians can focus on patient care.*

</div>
