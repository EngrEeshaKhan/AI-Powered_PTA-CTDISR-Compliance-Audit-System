<div align="center">

# AI-Powered PTA-CTDISR Compliance Audit System

**A local/offline AI-assisted compliance auditing platform for NTC auditors — RAG-powered evidence retrieval + a fine-tuned local LLM to draft CTDISR audit findings for human review.**

![Status](https://img.shields.io/badge/status-active--development-yellow)
![Backend](https://img.shields.io/badge/backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/frontend-React%20%2B%20Vite-61DAFB)
![Model](https://img.shields.io/badge/LLM-Llama%203.2%20%2B%20LoRA-8A2BE2)
![Deployment](https://img.shields.io/badge/deployment-Docker-2496ED)
![Python](https://img.shields.io/badge/python-3.10.x-3776AB)
![License](https://img.shields.io/badge/license-Internal%2FUnlicensed-lightgrey)

</div>

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Project Objectives](#3-project-objectives)
4. [System Architecture](#4-system-architecture)
5. [Phase 1 — Project Foundation](#5-phase-1--project-foundation)
6. [Phase 2 — Knowledge Base & Document Processing](#6-phase-2--knowledge-base--document-processing)
7. [Phase 3 — Vector Database & RAG](#7-phase-3--vector-database--rag)
8. [Phase 4 — CTDISR Framework & Controls](#8-phase-4--ctdisr-framework--controls)
9. [Phase 5 — AI-Powered Audit Generation](#9-phase-5--ai-powered-audit-generation-core-of-the-project)
10. [Phase 6 — Auditor Review & Reporting](#10-phase-6--auditor-review--reporting)
11. [Phase 7 — Frontend, Security & Deployment](#11-phase-7--frontend-security--deployment)
12. [Screenshots](#12-screenshots)
13. [Technology Stack](#13-technology-stack)
14. [Project Structure](#14-project-structure)
15. [Data Model / Storage Schemas](#15-data-model--storage-schemas)
16. [API Documentation](#16-api-documentation)
17. [Installation](#17-installation)
18. [Configuration & Environment Variables](#18-configuration--environment-variables)
19. [Docker Deployment](#19-docker-deployment)
20. [Git, GitHub & CI/CD Workflow](#20-git-github--cicd-workflow)
21. [User Roles & Permissions](#21-user-roles--permissions)
22. [Security Considerations](#22-security-considerations)
23. [Known Issues & Troubleshooting](#23-known-issues--troubleshooting)
24. [Current Status](#24-current-status)
25. [Future Improvements](#25-future-improvements)
26. [Author](#26-author)

---

## 1. Project Overview

The **AI-Powered PTA-CTDISR Compliance Audit System** is a local/offline platform that helps NTC (National Telecommunication Corporation) auditors evaluate PTA/licensee compliance against the **CTDISR (Cyber & Telecom Data & Information Security Regulation)** framework.
Instead of manually cross-referencing dozens of policy documents, advisories, and asset inventories against every control in the framework, the system:

1. Indexes all organizational evidence (policies, advisories, CTDISR text, asset inventories) into a searchable knowledge base.
2. Retrieves the evidence most relevant to a specific control using semantic (embedding-based) search.
3. Feeds that evidence into a fine-tuned local LLM, which drafts a structured audit finding.
4. Hands the draft to a human auditor, who reviews, edits, and finalizes it.

The system is designed to run **entirely offline** — no evidence, control data, or generated findings are sent to any external API. This matters for a regulator/telecom compliance context where the underlying documents may be sensitive.

**Design philosophy:** the AI is an assistant, not a decision-maker. Every AI-generated finding is explicitly labeled and must pass through an auditor review step (`Draft → Generated → Reviewed → Finalized`) before it counts as an official result.

## 2. Problem Statement

- CTDISR compliance audits require cross-referencing dozens of policy/advisory documents against each control, often manually, using search-in-PDF or spreadsheet lookups.
- Locating the right evidence for a given control is time-consuming, inconsistent between auditors, and easy to get wrong (missed documents, outdated policy versions, etc.).
- There is no single offline-capable tool that unifies document knowledge management, CTDISR control tracking, AI-assisted draft generation, and auditor sign-off in one auditable workflow.
- Existing generic AI tools (ChatGPT, etc.) cannot be used directly for this because the source documents are sensitive/internal and cannot be uploaded to third-party services.

## 3. Project Objectives
- Provide a centralized, offline knowledge base of policies, advisories, CTDISR controls, and asset inventories, organized by category.
- Use semantic search (sentence embeddings + FAISS) to automatically retrieve the most relevant evidence for a given control, rather than relying on keyword search.
- Use a fine-tuned local LLM (Llama 3.2 + LoRA) to draft PTA responses, recommendations, and action items grounded in retrieved evidence.
- Give auditors a structured workspace to review, edit, and finalize AI-drafted audit findings, with an explicit audit lifecycle (Draft → Generated → Reviewed → Finalized).
- Enforce role-based access so that CTDISR framework management is restricted to Administrators while day-to-day auditing is available to Auditors.
- Package the entire system (backend, frontend, model weights, storage) for local/offline deployment via Docker, so it can run inside an internal network without external dependencies.
- Maintain a clean audit trail: every finding is traceable to the control it addresses, the evidence used, the AI output, and the auditor's edits.

## 4. System Architecture

```
                       ┌───────────────────────────────────────────┐
                       │              Document Ingestion            │
                       │  PDF / DOCX / Excel  →  Parse  →  Chunk    │
                       └───────────────────────┬───────────────────┘
                                                ▼
                       ┌───────────────────────────────────────────┐
                       │        Embedding (all-MiniLM-L6-v2)        │
                       │              384-dim vectors                │
                       └───────────────────────┬───────────────────┘
                                                ▼
                       ┌───────────────────────────────────────────┐
                       │              FAISS Vector Index             │
                       │   storage/vectors/knowledge.index + meta    │
                       └───────────────────────┬───────────────────┘
                                                ▼
   Auditor selects  ──▶  Retrieve top-k evidence  ──▶  Context Builder ──▶  Fine-tuned Llama (LoRA)
   a CTDISR control       (CTDISR + Policies +                                       │
                            Advisories + Assets)                                     ▼
                                                                     PTA Response / Recommendations / Action By
                                                                                       │
                                                                                       ▼
                                                                         NTC Auditor Review & Comments
                                                                                       │
                                                                                       ▼
                                                                            Final Audit Report
```

**Layered view:**

| Layer | Responsibility |
|---|---|
| **Ingestion layer** | Parses PDF/DOCX/Excel, chunks text, extracts metadata, stores raw documents by category |
| **Retrieval layer** | Embeds chunks, indexes them in FAISS, performs semantic top-k search per control |
| **Reasoning layer** | Builds a grounded prompt from retrieved evidence, runs it through the fine-tuned Llama model |
| **Persistence layer** | Stores controls, audits, and reports as JSON documents on local disk |
| **Application layer** | FastAPI REST API exposing uploads, CTDISR controls, audits, reports, and dashboard aggregation |
| **Presentation layer** | React + MUI frontend with role-based navigation and an audit workspace |
| **Deployment layer** | Docker Compose orchestration for backend + frontend, with local storage/model mounts |

---

## 5. Phase 1 — Project Foundation

**Goal:** establish the problem, scope, and technical direction before writing implementation code.

- Defined the project objective, problem statement, and system goals (see Sections 1–3).
- Established the high-level architecture: RAG pipeline + fine-tuned LLM + FastAPI backend + React frontend + Docker packaging.
- Selected the technology stack (Section 13) based on constraints: must run offline, must run on modest local hardware (CPU inference fallback), must be deployable via Docker.
- Decided on local JSON storage rather than a full RDBMS for the MVP, keeping PostgreSQL as a documented-but-not-yet-adopted future option.


## 6. Phase 2 — Knowledge Base & Document Processing

**Goal:** get organizational evidence into a structured, searchable form.

- Four document categories are supported: **Policies, Advisories, CTDISR, Assets** — each stored in its own subfolder under `storage/documents/`.
- Ingestion supports **PDF, DOCX, and Excel** files. Documents already processed in development include:
  - `NTC-DC_Asset_Inventory.xlsx`
  - `national_cs_framework_for_telecom_07-07-2022.pdf`
  - `ISMS_Data_Protection_Policy_v1.1-compressed.pdf`
- The ingestion pipeline: **upload → parse → chunk → store with metadata**. Metadata includes source filename, category, chunk index, and (internally) file path — though the file path must never be rendered raw in the UI.
- The index currently holds roughly **805 metadata/chunk records**, tracked in `storage/vectors/knowledge_metadata.json`.
- **Upload success is not the same as processing success.** The system distinguishes four document states:
  - `Uploaded` — file received and saved to disk
  - `Processing` — parsing/chunking/embedding in progress
  - `Processed` — successfully chunked, embedded, and indexed
  - `Processing Failed` — an error occurred during parsing/embedding (the file is retained but not searchable)
- The frontend Documents screen is expected to show this status explicitly rather than a generic "success" message, plus support search/filter, per-document detail view, and delete.
- Raw filesystem paths (e.g. Windows paths like `D:\Internships and Researches\...`) must never be surfaced in the UI — only display names, categories, and status.

<img width="938" height="417" alt="image" src="https://github.com/user-attachments/assets/48383516-10b7-4672-bc95-b6e037d8ac4b" />


## 7. Phase 3 — Vector Database & RAG

**Goal:** make the knowledge base semantically searchable so the right evidence surfaces for each control.

- Embedding model: **`all-MiniLM-L6-v2`**, producing 384-dimensional vectors — chosen for being lightweight enough to run locally/offline without a GPU.
- Vector index: **FAISS**, persisted at `storage/vectors/knowledge.index`, with a parallel metadata file (`knowledge_metadata.json`) mapping vector IDs back to source document/chunk info.
- An embedding cache (`storage/cache/embeddings/`) avoids re-embedding unchanged documents on restart.
- **Retrieval flow:** given a CTDISR control (its ID + description + interpretation), the system embeds the control text and performs a top-k nearest-neighbor search across all indexed chunks, optionally filtered by category (Policies, Advisories, Assets).
- **Context Builder:** assembles the retrieved chunks into a structured, de-duplicated context block, tagged by source category, which becomes part of the prompt sent to the LLM.

<img width="734" height="434" alt="image" src="https://github.com/user-attachments/assets/55ab6b3e-6bf1-4052-addc-d5ba11e12487" />

<img width="766" height="121" alt="image" src="https://github.com/user-attachments/assets/a80c0306-2029-4c5a-86f0-af670601630f" />



## 8. Phase 4 — CTDISR Framework & Controls

**Goal:** represent the regulatory framework itself as structured, manageable data — separate from ordinary evidence documents.

- Controls are stored separately from other documents, at `storage/ctdisr/controls.json`, since they are framework definitions rather than evidence.
- Each control record includes:
  - **Control ID** (e.g. `3.1`)
  - **Control Level** (e.g. `CL1`)
  - **Control Description**
  - **Control Interpretation**
  - **Active/Inactive** status flag
- Development/testing has exercised control **3.1 / CL1** and control **4.4** specifically.
- CTDISR management endpoints (create/update/deactivate controls) are **Administrator-only**. Deleting a control is implemented as **deactivation** (`active: false`), not physical removal — this preserves audit history for any audits already run against that control.
- Auditors can view the full active control list and control detail, but cannot create, edit, or deactivate controls.

<img width="941" height="389" alt="image" src="https://github.com/user-attachments/assets/19e778ef-db3e-45dc-8385-940a1ebde4e9" />

<img width="229" height="93" alt="image" src="https://github.com/user-attachments/assets/633eaf94-5b75-4178-97d3-d6bd43744f50" />


<img width="445" height="399" alt="image" src="https://github.com/user-attachments/assets/ad1bb596-d943-4dc9-af92-3ad5e0426b53" />



## 9. Phase 5 — AI-Powered Audit Generation *(core of the project)*

**Goal:** generate a grounded, structured audit finding for a selected control, using retrieved evidence and a fine-tuned LLM.

```
Select Control → Retrieve Evidence → Build Context → Llama + LoRA → Generate Audit Finding
```

**Model details:**

- Base model: **`meta-llama/Llama-3.2-3B-Instruct`**.
- Fine-tuning method: **LoRA/QLoRA**, run on an **A100 GPU via Google Colab** (training is not expected to happen on local hardware).
- Training dataset: **~99 examples** derived from an existing CTDISR audit Excel workbook (real control → PTA response/recommendation pairs).
- Adapter size: **~24.3M trainable parameters**, roughly **0.75%** of the base model's total parameters — a lightweight adapter rather than a full fine-tune.
- **Local inference fallback:** since the 3B model is heavier than ideal for CPU-only local inference, a smaller local setup is used day-to-day:
  ```
  models/
  ├── llama-3.2-1b-instruct/
  └── pta-llama-3.2-1b-lora/
      └── final/
  ```
- **Performance:** local CPU inference takes roughly **tens of seconds per generated response**, which is expected given the hardware constraints of the offline deployment target.
- ⚠️ **Known cleanup item:** there is a configuration/path inconsistency between older references to the 3B model and the actual local 1B fallback setup — this should be resolved so model paths are consistent across config files.

**Generation flow:**

1. Auditor selects a CTDISR control in the Audit Workspace.
2. Backend retrieves top-k relevant evidence chunks (from CTDISR text, Policies, Advisories, Assets).
3. Context Builder assembles the evidence into a structured prompt.
4. The fine-tuned Llama model generates the finding, controlled by two exposed parameters:
   - `top_k` — number of evidence chunks retrieved
   - `max_new_tokens` — generation length cap
5. Output fields: **PTA Response, PTA Recommendations, Action By** — persisted immediately in `Draft`/`Generated` status.

📷 *Screenshots: Audit Workspace · Selected control · Retrieved evidence · AI-generated result*

## 10. Phase 6 — Auditor Review & Reporting

**Goal:** turn an AI draft into an authoritative, human-approved audit record.

**Audit lifecycle:**

```
Draft → AI Generated → Auditor Review → Reviewed → Finalized
```

| Status | Meaning |
|---|---|
| `Draft` | Control selected, audit initiated, no AI output yet |
| `Generated` | AI has produced PTA Response / Recommendations / Action By |
| `Reviewed` | Auditor has read and edited the AI output |
| `Finalized` | Auditor has signed off; the record is locked as the official finding |

- Auditors can edit **PTA Response, PTA Recommendations, Action By**, and add free-text **NTC Comments** — the auditor's own observations layered on top of the AI draft.
- Saved audits are persisted at `storage/audits/audit_results.json`, keyed by a unique audit ID.
- The **Reports API** (`/api/v1/reports`) exposes the saved audit list and individual audit detail to the frontend, backed by a `JsonAuditService()`.
- **Excel/PDF export** of finalized reports is planned but not yet implemented.
- The frontend's Audit History / Reports screens should render these persisted records (not raw API JSON) as a proper table: Audit ID, Control, Level, Status, Created, Updated, Actions — with a detail view showing the full finding (Control, Description, Interpretation, Evidence, PTA Response, Recommendations, Action By, NTC Comments, Status).

📷 *Screenshots: Auditor review screen · Audit History · Audit Report detail*

## 11. Phase 7 — Frontend, Security & Deployment

**Goal:** wrap the backend in a professional, role-aware interface and make the whole system deployable as a unit.

- Frontend stack: **React + Vite + MUI + React Router**, with custom layout/header/status components and an authentication context.
- Visual direction: **dark charcoal/black base with emerald/green and amber/red accents** — explicitly avoiding blue, to read as a serious compliance/security platform rather than a generic dashboard template.
- **Navigation structure:**
  ```
  Dashboard
  Knowledge Base
   ├── Documents
   └── CTDISR Controls
  Audits
   ├── Audit Workspace
   ├── Audit History
   └── Reports
  Administration
   └── Settings
  + User/Profile menu
  ```
- **Dashboard** aggregates: total documents, per-category counts (Policies/Advisories/CTDISR/Assets), CTDISR control count, audit counts/activity, AI engine status, and knowledge-base status — all served by a single `/api/v1/dashboard` endpoint so the frontend doesn't need to compute aggregates client-side.
- **Role-based UI** enforced for **NTC Administrator** vs **Auditor** (Section 21) — the CTDISR management screen in particular must not be reachable/visible to Auditors.
- **Dockerized** backend and frontend, orchestrated via a single `docker-compose.yml` at the project root (Section 19).
- **Git/GitHub workflow and CI/CD** concepts layered on top of local development (Section 20).

📷 *Screenshots: Dashboard · Admin interface · Auditor interface · Docker architecture diagram*

---

## 12. Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Knowledge Base
![Knowledge Base](docs/screenshots/knowledge-base.png)

### CTDISR Controls
![CTDISR Controls](docs/screenshots/ctdisr-controls.png)

### Audit Workspace
![Audit Workspace](docs/screenshots/audit-workspace.png)

### AI Audit Result
![AI Audit Result](docs/screenshots/audit-result.png)

### Audit History
![Audit History](docs/screenshots/audit-history.png)

### Reports
![Audit Reports](docs/screenshots/audit-reports.png)

> Store all documentation images under `docs/screenshots/` — not in `storage/` or `frontend/public/` — to keep documentation assets separate from application data. Recommended filenames are shown above; keep them in sync with the `alt`/path in each `![...]()` tag if you rename anything.

---

## 13. Technology Stack

**Backend**
| Component | Choice | Notes |
|---|---|---|
| Framework | FastAPI | Python 3.10.x |
| Storage | Local JSON files | SQLAlchemy/psycopg present in dependencies but PostgreSQL not yet confirmed as active runtime |
| Vector search | FAISS | Local, in-process index |
| Embeddings | `all-MiniLM-L6-v2` | 384-dimensional |
| LLM | Llama 3.2 (3B fine-tuned / 1B local fallback) | LoRA/QLoRA adapter |
| Document parsing | PDF / DOCX / Excel parsers | Category-tagged ingestion |
| Containerization | Docker | Backend + frontend services |


**Frontend**
| Component | Choice |
|---|---|
| Framework | React |
| Build tool | Vite |
| UI library | MUI (Material UI) |
| Routing | React Router |
| Auth | Custom authentication context |
| Theming | Dark charcoal/black + emerald/green + amber/red |


**Tooling**
- Git / GitHub for version control
- GitHub Actions (planned/being set up) for CI/CD
- Docker Compose for local/offline orchestration


## 14. Project Structure

```
project-root/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       └── api/
│           └── v1/
│               ├── uploads.py
│               ├── ctdisr.py
│               ├── dashboard.py
│               └── reports.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── context/          # auth context, etc.
│       └── services/         # API client layer
├── models/
│   ├── llama-3.2-1b-instruct/
│   └── pta-llama-3.2-1b-lora/
│       └── final/
├── storage/
│   ├── documents/
│   │   ├── policies/
│   │   ├── advisories/
│   │   ├── ctdisr/
│   │   └── assets/
│   ├── vectors/
│   │   ├── knowledge.index
│   │   └── knowledge_metadata.json
│   ├── cache/
│   │   └── embeddings/
│   ├── ctdisr/
│   │   └── controls.json
│   └── audits/
│       └── audit_results.json
└── docs/
    └── screenshots/
```


## 15. Data Model / Storage Schemas

**Control record** (`storage/ctdisr/controls.json`)
```json
{
  "control_id": "3.1",
  "control_level": "CL1",
  "control_description": "string",
  "control_interpretation": "string",
  "active": true
}
```

**Audit record** (`storage/audits/audit_results.json`)
```json
{
  "audit_id": "uuid-or-generated-id",
  "control_id": "3.1",
  "control_level": "CL1",
  "status": "Draft | Generated | Reviewed | Finalized",
  "evidence": [
    { "source": "policies", "chunk": "..." }
  ],
  "pta_response": "string",
  "pta_recommendations": "string",
  "action_by": "string",
  "ntc_comments": "string",
  "created_at": "ISO-8601 timestamp",
  "updated_at": "ISO-8601 timestamp"
}
```

**Document metadata** (`storage/vectors/knowledge_metadata.json`)
```json
{
  "chunk_id": "string",
  "source_filename": "string",
  "category": "policies | advisories | ctdisr | assets",
  "chunk_index": 0,
  "status": "Uploaded | Processing | Processed | Processing Failed"
}
```

## 16. API Documentation

**Uploads**
```
GET    /api/v1/uploads/                    # list all uploaded documents
POST   /api/v1/uploads/                    # upload + trigger processing (parse/chunk/embed)
GET    /api/v1/uploads/{document_id}       # get a single document's metadata/status
DELETE /api/v1/uploads/{document_id}       # remove a document and its indexed chunks
```

**CTDISR Controls**
```
GET    /api/v1/ctdisr/controls                       # list active controls (Auditor + Admin)
POST   /api/v1/ctdisr/controls                        # create a control (Admin only)
PUT    /api/v1/ctdisr/controls/{control_id}            # update a control (Admin only)
DELETE /api/v1/ctdisr/controls/{control_id}            # deactivate a control (Admin only) — sets active=false
POST   /api/v1/ctdisr/controls/{control_id}/audit      # run an AI audit against this control
```

Example request body for running an audit:
```json
{
  "top_k": 5,
  "max_new_tokens": 512
}
```

Example response:
```json
{
  "success": true,
  "audit_id": "aud_001",
  "control_id": "3.1",
  "status": "Generated",
  "pta_response": "...",
  "pta_recommendations": "...",
  "action_by": "..."
}
```

**Reports**
```
GET /api/v1/reports              # list saved audits
GET /api/v1/reports/{audit_id}   # single audit detail
```

Example list response:
```json
{
  "success": true,
  "count": 3,
  "results": [
    { "audit_id": "aud_001", "control_id": "3.1", "status": "Finalized", "...": "..." }
  ]
}
```

**Dashboard**
```
GET /api/v1/dashboard   # aggregated stats: document counts by category, control count,
                         # audit counts by status, AI engine status, KB status
```

> ⚠️ **Known integration gap:** the frontend service layer currently references an older `/audit-results` route, while the backend's actual reports contract is `/api/v1/reports`. This needs to be aligned — update the frontend API client rather than re-adding a legacy backend route.

Interactive API documentation is available via FastAPI's built-in Swagger UI at `/docs` once the backend is running (e.g. `http://localhost:8000/docs`).

## 17. Installation

**Prerequisites**
- Python 3.10.x
- Node.js (LTS) + npm
- Git
- (Optional, for GPU fine-tuning only) CUDA-capable GPU / Google Colab — not required to *run* the system, only to retrain the LoRA adapter

**Backend setup**
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Backend will be available at `http://localhost:8000`, with Swagger docs at `http://localhost:8000/docs`.

**Frontend setup**
```bash
cd frontend
npm install
npm run dev
```
Frontend will be available at `http://localhost:5173` (default Vite port).

**Model setup**

Ensure the local model directories exist and are populated before starting the backend:
```
models/llama-3.2-1b-instruct/
models/pta-llama-3.2-1b-lora/final/
```
If these are not present, download/copy them from your training environment (Colab output) before first run.

## 18. Configuration & Environment Variables

Recommended `.env` structure for the backend (adjust to match actual config loading in `app/`):

```env
# Server
APP_ENV=local
APP_PORT=8000

# Storage paths
STORAGE_DIR=./storage
MODELS_DIR=./models

# Model
BASE_MODEL_PATH=./models/llama-3.2-1b-instruct
LORA_ADAPTER_PATH=./models/pta-llama-3.2-1b-lora/final
DEFAULT_TOP_K=5
DEFAULT_MAX_NEW_TOKENS=512

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIM=384
```

For the frontend, a `.env` file controlling the API base URL:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 19. Docker Deployment

```bash
docker compose build
docker compose up
```

- `docker-compose.yml` must live at the **project root**, not inside `backend/`. (Verified via PowerShell: `Test-Path .\backend\docker-compose.yml` → `false`, `Test-Path .\docker-compose.yml` → `true`.)
- The backend container mounts local `./storage` and `./models` directories as volumes, so the knowledge base and model weights don't need to be baked into the image and persist across container rebuilds.
- **Docker Desktop must be running** before `docker compose up` — a common early error was the Docker engine being unreachable simply because Docker Desktop itself hadn't been started.
- Example service layout in `docker-compose.yml`:
  ```yaml
  services:
    backend:
      build: ./backend
      ports:
        - "8000:8000"
      volumes:
        - ./storage:/app/storage
        - ./models:/app/models
    frontend:
      build: ./frontend
      ports:
        - "5173:5173"
      depends_on:
        - backend
  ```

## 20. Git, GitHub & CI/CD Workflow

Repository: [`EngrEeshaKhan/AI-Powered_PTA-CTDISR-Compliance-Audit-System`](https://github.com/EngrEeshaKhan/AI-Powered_PTA-CTDISR-Compliance-Audit-System)

**Local workflow covered:** commits, branches, fetch, pull/rebase, push, merge, and code review concepts.

**Important clarification:** GitHub does not automatically run or deploy the application just because code is pushed or edited. Automation only happens if a CI/CD pipeline is explicitly configured.

**Planned/target CI/CD pipeline (GitHub Actions):**
```
Push to GitHub
     ↓
GitHub Actions triggered
     ↓
Install dependencies (backend + frontend)
     ↓
Run tests
     ↓
Build Docker image(s)
     ↓
Push/deploy image
```

Local commands (`docker build`, `docker compose build`, `docker compose up`) are separate from and unaffected by whatever GitHub Actions workflow is configured — CI/CD automates what you'd otherwise run manually, it doesn't replace local development.


## 21. User Roles & Permissions

The system supports exactly two roles.

| Capability | NTC Administrator | Auditor |
|---|---|---|
| Upload/manage documents | ✅ | View only |
| Manage document versions | ✅ | ❌ |
| View knowledge-base statistics | ✅ | ✅ |
| View CTDISR controls | ✅ | ✅ |
| Create/update/deactivate CTDISR controls | ✅ | ❌ |
| Start/run AI audits | ✅ | ✅ |
| Review/edit PTA Response, Recommendations, Action By | ✅ | ✅ |
| Add/edit NTC Comments | ✅ | ✅ |
| Finalize audit reports | ✅ | ✅ |
| Export reports | ✅ | — |
| Access Administration/Settings screens | ✅ | ❌ |

**Hard security requirement:** CTDISR framework upload/change functionality is Administrator-only, both at the API level (server-side enforcement) and the UI level (Auditors must not even see the admin screen, not just be blocked from submitting it).


## 22. Security Considerations

- CTDISR framework management is strictly Administrator-only — enforced server-side, not just hidden in the UI.
- Raw filesystem paths (e.g. `D:\Internships and Researches\...`) must never be exposed to end users; only clean display names, categories, and processing status should render in the UI.
- The system is designed to run fully offline/local — no evidence documents, control text, or generated findings are sent to third-party AI APIs.
- Authentication context on the frontend gates route access by role; this should be paired with server-side role checks on every protected endpoint (not just relied upon client-side).
- Deactivating a control (rather than hard-deleting) preserves the audit trail for any historical audits run against it.


## 23. Known Issues & Troubleshooting

**PyTorch DLL / import error on Windows when running `uvicorn app.main:app --reload`**
- This is an **environment/dependency issue**, not an architectural problem with the audit pipeline. It typically stems from a mismatched PyTorch build (CPU vs CUDA wheel) or a missing Visual C++ Redistributable on Windows.
- Suggested fix path: confirm the installed `torch` wheel matches the machine (CPU-only build if no CUDA GPU is present), reinstall inside a clean virtual environment, and verify the Microsoft Visual C++ Redistributable is installed.

**`docker-compose.yml` not found**
- Confirm the file is at the **project root**, not inside `backend/`. Use `Test-Path .\docker-compose.yml` (PowerShell) or `ls docker-compose.yml` (bash) to verify before running `docker compose up`.

**Docker engine unreachable**
- Ensure **Docker Desktop is actually running** (not just installed) before invoking any `docker` or `docker compose` command.

**Frontend reports page shows nothing / errors**
- Check that the frontend API client is pointed at `/api/v1/reports`, not the older `/audit-results` path.

**Model path errors at inference time**
- Check for stale references to the original 3B model path where the active local setup actually uses the 1B fallback (`models/llama-3.2-1b-instruct` + `models/pta-llama-3.2-1b-lora/final`).

## 24. Current Status

| Area | State |
|---|---|
| FastAPI backend | 🟢 Substantially implemented |
| Local document storage | 🟢 Implemented |
| PDF/DOCX/Excel ingestion | 🟢 Implemented |
| Embeddings | 🟢 Implemented |
| FAISS | 🟢 Implemented |
| CTDISR controls | 🟢 Implemented |
| RAG retrieval | 🟢 Implemented |
| Llama inference | 🟢 Implemented (CPU limitations) |
| LoRA model | 🟢 Trained |
| Upload API | 🟢 Implemented |
| Audit API | 🟢 Implemented |
| Saved audits | 🟢 Implemented |
| Reports API | 🟢 Implemented |
| React UI | 🟡 Actively being wired |
| Reports frontend | 🟡 Needs API alignment (`/audit-results` → `/reports`) |
| Excel/PDF export | 🟡 Planned / in progress |
| Role-based UI | 🟡 Needs complete enforcement/polish |
| Docker | 🟡 Being finalized/tested |
| CI/CD | 🟡 Learning/setting up |
| PostgreSQL | ⚪ Not confirmed as runtime storage |
| Windows PyTorch environment | 🔴 DLL/import issue (environment-level, not architectural) |

**Bottom line:** the major technical pieces are already in place — RAG + FAISS + local documents + CTDISR controls + fine-tuned Llama + FastAPI + saved audits + React frontend + Docker. Remaining work is integration, correctness, security enforcement, UI polish, reporting/export, deployment, and testing — not building the core system from scratch.

## 25. Future Improvements
- Complete Excel/PDF export for finalized audit reports.
- Finish aligning frontend reports/history wiring to the `/reports` API contract.
- Full role-based UI enforcement (hide admin-only routes/components from Auditors both visually and via route guards).
- Resolve the local Windows PyTorch DLL/import issue blocking `uvicorn app.main:app --reload` in some environments.
- Finalize the Docker Compose setup and stand up the GitHub Actions CI/CD pipeline (install → test → build → push/deploy).
- Clean up model path inconsistencies between the original 3B fine-tune references and the active local 1B fallback model.
- Evaluate whether PostgreSQL should formally replace JSON storage as the system scales beyond a single-machine deployment.
- Add automated tests (backend unit/integration tests, frontend component tests) to support the CI pipeline.
- Add audit logging (who ran/edited/finalized which audit, and when) for compliance traceability of the tool itself.

## 26. Author

**Eesha Khan**
Repository: [`EngrEeshaKhan/AI-Powered_PTA-CTDISR-Compliance-Audit-System`](https://github.com/EngrEeshaKhan/AI-Powered_PTA-CTDISR-Compliance-Audit-System)
