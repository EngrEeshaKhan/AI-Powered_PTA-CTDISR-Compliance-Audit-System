::: {align="center"}
# AI-Powered PTA CTDISR Compliance Audit System

-------
                    │ Asset Documents           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │   Document Processing     │
                    │                           │
                    │ PDF / DOCX / XLSX Parsing │
                    │ Cleaning                  │
                    │ Category Detection        │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │       Chunking Layer      │
                    │                           │
                    │ Policy Chunker            │
                    │ Advisory Chunker          │
                    │ CTDISR Chunker            │
                    │ Asset Chunker             │
                    │ Semantic Chunker          │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │      Embedding Model      │
                    │                           │
                    │ all-MiniLM-L6-v2          │
                    │ Sentence Transformers     │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │       Vector Index        │
                    │                           │
                    │          FAISS            │
                    │ Semantic Similarity       │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │    Retrieval / RAG        │
                    │                           │
                    │ Query Builder              │
                    │ Retriever                  │
                    │ Context Builder             │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │       Llama 3.2           │
                    │                           │
                    │ Fine-Tuned Model           │
                    │ LoRA Adapter               │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │      AI Audit Result      │
                    │                           │
                    │ PTA Response              │
                    │ Recommendation            │
                    │ Evidence / Context        │
                    │ Audit Findings            │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │      Auditor Workspace    │
                    │                           │
                    │ Review → Edit → Finalize  │
                    │ Export / Reporting        │
                    └───────────────────────────┘
```

------------------------------------------------------------------------

# 🧠 Artificial Intelligence Pipeline

## 1. Document Ingestion

Knowledge documents are uploaded through the web interface.

Supported categories:

-   Policies
-   Advisories
-   
```

------------------------------------------------------------------------

## 3. Chunking

Large documents are divided into smaller meaningful pieces.

The project contains category-aware chunkers:

``` text
backend/app/ai/chunking/

├── advisory_chunker.py
├── asset_chunker.py
├── ctdisr_chunker.py
├── policy_chunker.py
└── semantic_chunker.py
```

Category-specific chunking helps preserve the structure of compliance
information.

------------------------------------------------------------------------

## 4. Embeddings

The project uses:

**`sentence-transformers/all-MiniLM-L6-v2`**

to convert text chunks into numerical vectors.

Conceptually:

``` text
Compliance Text
       ↓
Sentence Transformer
       ↓
384-dimensional embedding
       ↓
Vector Index
```

Embeddings are cached to reduce unnecessary recomputation.

------------------------------------------------------------------------

## 5. Vector Search

FAISS is used for efficient semantic similarity search.

When an auditor audits a control:

``` text
CTDISR Control
      ↓
Search Query
      ↓
Embedding
  
The fine-tuning workflow uses:

-   PyTorch
-   Hugging Face Transformers
-   PEFT
-   LoRA / QLoRA
-   TRL
-   Hugging Face Datasets
-   4-bit quantization during GPU training/inference where supported

The model is trained to understand the structure of PTA CTDISR audit
information.

### Training data structure

The project dataset includes fields such as:

``` text
Control
Cont
The platform uses authenticated access and role-based functionality.

### Roles

  -----------------------------------------------------------------------
  Role                                Capabilities
  ----------------------------------- -----------------------------------
  Administrator                       Manage users, documents, controls
                                      and compliance operations

  Auditor                             Review controls, execute AI audits
                                      and work with audit results
  -----------------------------------------------------------------------

Authentication uses bearer access tokens.

The frontend stores the active access token and automatically attaches
it to API requests.

------------------------------------------------------------------------

# 🖥️ Frontend

The frontend is built with:

-   React
-   React Router
-   Material UI
-   Axios
-   Vite

### Main application areas

``` text
Dashboard
Documents
Controls
Audits
Users
```

The interface follows a professional cybersecurity/compliance visual
direction:

-   Dark enterprise interface
-   Charcoal/black surfaces
-   Emerald compliance accents
-   Amber warning states
-   Red error states
-   Responsive layouts
-   Status chips
-   Data tables
-   Dialog-based editing
-   AI audit actions

------------------------------------------------------------------------

# ⚙️ Backend

The backend is implemented with **FastAPI**.

Typical backend structure:

``` text
backend/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── dashboard.py
│   │       ├── uploads.py
│   │       └── ...
│   │
│   ├── ai/
│   │   ├── chunking/
│   │   ├── embeddings/
│   │   ├── llm/
│   │   ├── retrieval/
│   │   └── pipelines/
│   │
│   ├── core/
│   │   └── auth/
│   │
│   ├── modules/
│   │   ├── audits/
│   │   ├── auth/
│   │   └── ctdisr/
│   │
│   └── main.py
│
├── storage/
│   ├── documents/
│   │   ├── advisories/
│   │   ├── policies/
│   │   ├── ctdisr/
│   │   └── assets/
│   │
│   ├── vectors/
│   ├── cache/
│   └── audits/
│
├── models/
│   ├── llama-3.2-1b-instruct/
│   └── pta-llama-3.2-1b-lora/
│
├── pyproject.toml
└── Dockerfile
```

------------------------------------------------------------------------

# ⚛️ Frontend Structure

``` text
frontend/
│
├── src/
│   ├── components/
│   ├── context/
│   │   └── AuthContext.jsx
│   │
│   ├── layouts/
│   │   └── AppLayout.jsx
│   │
│   ├── pages/
│   │   ├── LoginPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── DocumentsPage.jsx
│   │   ├── ControlsPage.jsx
│   │   ├── ControlDetailsPage.jsx
│   │   ├── AuditsPage.jsx
│   │   ├── AuditDetailsPage.jsx
│   │   └── UsersPage.jsx
│   │
│   ├── routes/
│   │   └── AppRoutes.jsx
│   │
│   ├── services/
│   │   ├── api.js
│   │   ├── documents.service.js
│   │   ├── controls.service.js
│   │   └── ...
│   │
│   ├── App.jsx
│   ├── main.jsx
│   ├── theme.js
│   └── styles.css
│
├── package.json
└── vite.config.js
```

------------------------------------------------------------------------

# 🔌 API Overview

The FastAPI backend exposes interactive API documentation through
Swagger UI.

When the backend is running:

``` text
http://127.0.0.1:8000/docs
```

## Authentication

``` text
POST /api/v1/auth/login
```

------------------------------------------------------------------------

## Dashboard

``` text
GET /api/v1/dashboard/statistics
```

------------------------------------------------------------------------

## Document Upload

``` text
POST /api/v1/uploads/
```

Delete an uploaded document:

``` text
DELETE /api/v1/uploads/{document_id}
```

------------------------------------------------------------------------

## CTDISR Controls

### Get controls

``` text
GET /api/v1/ctdisr/controls
```

### Create control

``` text
POST /api/v1/ctdisr/controls
```

### Get statistics

``` text
GET /api/v1/ctdisr/controls/statistics
```

### Get one control

``` text
GET /api/v1/ctdisr/controls/{control_id}
```

### Update control

``` text
PUT /api/v1/ctdisr/controls/{control_id}
```

### Deactivate control

``` text
DELETE /api/v1/ctdisr/controls/{control_id}
```

> The DELETE operation is designed as a control deactivation operation
> rather than a physical database deletion.

### Run AI audit

``` text
POST /api/v1/ctdisr/controls/{control_id}/audit
```

Example query parameters:

``` text
?top_k=5&max_new_tokens=400
```

------------------------------------------------------------------------

# 🚀 Local Installation

## Prerequisites

Install:

-   Python 3.10+
-   Node.js 18+
-   npm
-   Git
-   Docker Desktop (optional)
-   CUDA-capable GPU (recommended for model training)

------------------------------------------------------------------------

# 1️⃣ Clone the Repository

``` bash
git clone <YOUR_REPOSITORY_URL>
cd AI-Powered_PTA-CTDISR-Compliance-Audit-System
```

------------------------------------------------------------------------

# 2️⃣ Backend Setup

Move into the backend:

``` bash
cd backend
```

Create a virtual environment:

### Windows

``` powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Linux / macOS

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

``` bash
pip install -e .
```

If your project uses a requirements file instead:

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

# 3️⃣ Configure Environment Variables

Create:

``` text
backend/.env
```

Example:

``` env
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8000
```

Add project-specific authentication/model/database variables according
to the backend configuration.

> Do not commit `.env` files or model credentials to GitHub.

------------------------------------------------------------------------

# 4️⃣ Start FastAPI

From the `backend` directory:

``` bash
uvicorn app.main:app --reload
```

Backend:

``` text
http://127.0.0.1:8000
```

Swagger:

``` text
http://127.0.0.1:8000/docs
```

------------------------------------------------------------------------

# 5️⃣ Frontend Setup

Open another terminal:

``` bash
cd frontend
```

Install dependencies:

``` bash
npm install
```

Start Vite:

``` bash
npm run dev
```

The frontend will normally be available at:

``` text
http://localhost:5173
```

------------------------------------------------------------------------

# 🐳 Docker

The project also supports containerized backend execution.

A typical development setup contains:

``` text
docker-compose.yml
```

with services such as:

``` text
backend
```

and mounted directories for:

``` text
storage/
models/
```

Example:

``` bash
docker compose up --build
```

Stop services:

``` bash
docker compose down
```

------------------------------------------------------------------------

# 📂 Knowledge Base

The knowledge base is organized by document category:

``` text
storage/documents/

├── advisories/
├── policies/
├── ctdisr/
└── assets/
```

The processing pipeline transforms these documents into searchable
knowledge.

A typical flow is:

``` text
Upload
  ↓
Register
  ↓
Parse
  ↓
Chunk
  ↓
Embed
  ↓
Index
  ↓
Retrieve
  ↓
Generate
```

------------------------------------------------------------------------

# 📈 Example AI Audit Workflow

Suppose the auditor selects:

``` text
Control 4.4
```

The system performs:

``` text
1. Load CTDISR control
        ↓
2. Build retrieval query
        ↓
3. Generate query embedding
        ↓
4. Search FAISS index
        ↓
5. Retrieve top-K relevant chunks
        ↓
6. Build grounded context
        ↓
7. Send context + control to Llama
        ↓
8. Generate PTA-oriented audit assistance
        ↓
9. Display result to auditor
        ↓
10. Auditor reviews and finalizes
```

This is the core **RAG + Fine-Tuned LLM** workflow.

------------------------------------------------------------------------

# 🧪 Model Training

The project uses a supervised fine-tuning workflow for the audit model.

A simplified training pipeline is:

``` text
PTA Audit Excel
      ↓
Control List Sheet
      ↓
Training Dataset
      ↓
JSONL
      ↓
Tokenizer
      ↓
Llama Base Model
      ↓
LoRA / QLoRA
      ↓
Fine-Tuned Adapter
      ↓
Local Inference
```

The training dataset contains structured audit examples based on CTDISR
controls and associated PTA/NTC information.

------------------------------------------------------------------------

# 🧰 Technology Stack

## Backend

  Technology   Purpose
  ------------ ----------------------------
  Python       Core backend language
  FastAPI      REST API
  Uvicorn      ASGI server
  Pydantic     Validation and schemas
  Axios        Frontend API communication

## Frontend

  Technology     Purpose
  -------------- --------------------------
  React          Frontend framework
  Vite           Frontend build tool
  React Router   Application routing
  Material UI    Enterprise UI components
  CSS            Theme and visual styling

## Machine Learning & AI

  Technology                  Purpose
  --------------------------- ---------------------------------
  PyTorch                     Deep learning framework
  Hugging Face Transformers   LLM loading and inference
  Llama 3.2                   Generative language model
  PEFT                        Parameter-efficient fine-tuning
  LoRA / QLoRA                Efficient model adaptation
  TRL                         Supervised fine-tuning
  Sentence Transformers       Text embeddings
  all-MiniLM-L6-v2            Embedding model
  FAISS                       Vector similarity search

------------------------------------------------------------------------

# 🏷️ Technology Badges

The repository intentionally uses technology badges that reflect the
actual project stack.

### Core Development

```{=html}
<p>
```
`<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white">`{=html}
`<img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white">`{=html}
`<img src="https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=111111">`{=html}
`<img src="https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white">`{=html}
`<img src="https://img.shields.io/badge/Material%20UI-007FFF?style=flat-square&logo=mui&logoColor=white">`{=html}
```{=html}
</p>
```
### Machine Learning & AI

```{=html}
<p>
```
`<img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white">`{=html}
`<img src="https://img.shields.io/badge/Hugging%20Face-FFD21E?style=flat-square&logo=huggingface&logoColor=111111">`{=html}
`<img src="https://img.shields.io/badge/Transformers-FFD21E?style=flat-square&logo=huggingface&logoColor=111111">`{=html}
`<img src="https://img.shields.io/badge/PEFT-LoRA-orange?style=flat-square">`{=html}
`<img src="https://img.shields.io/badge/QLoRA-Parameter%20Efficient-blueviolet?style=flat-square">`{=html}
`<img src="https://img.shields.io/badge/Sentence--Transformers-22C55E?style=flat-square">`{=html}
`<img src="https://img.shields.io/badge/FAISS-16A085?style=flat-square">`{=html}
```{=html}
</p>
```
### DevOps / Tooling

```{=html}
<p>
```
`<img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white">`{=html}
`<img src="https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white">`{=html}
`<img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white">`{=html}
```{=html}
</p>
```

------------------------------------------------------------------------

# 🖼️ Screenshots

Add your actual project screenshots here after capturing the running
application.

Recommended screenshots:

``` text
docs/
└── screenshots/
    ├── dashboard.png
    ├── documents.png
    ├── controls.png
    ├── control-details.png
    ├── audits.png
    ├── audit-result.png
    └── users.png
```

Then display them in this README:

``` markdown
## Dashboard

![Dashboard](docs/screenshots/dashboard.png)

## Documents

![Documents](docs/screenshots/documents.png)

## Controls

![Controls](docs/screenshots/controls.png)

## AI Audit

![AI Audit](docs/screenshots/audit-result.png)
```

### Recommended presentation

For a professional GitHub repository, use:

-   1 dashboard screenshot
-   1 document management screenshot
-   1 controls screenshot
-   1 AI audit result screenshot
-   1 architecture diagram

Avoid uploading screenshots containing:

-   passwords
-   access tokens
-   private documents
-   personal information
-   internal credentials

------------------------------------------------------------------------

# 🎬 Demo Video

A short demonstration video can significantly improve the project
presentation.

Recommended video:

``` text
00:00 — Login
00:15 — Dashboard
00:30 — Knowledge Base
00:50 — Upload Document
01:10 — CTDISR Controls
01:35 — Open Control
01:55 — Run AI Audit
02:20 — Review AI Result
02:45 — Audit Management
03:00 — Final Result
```

After uploading the demo to a suitable platform, add it here:

``` markdown
## 🎥 Project Demonstration

[Watch the full system demonstration](YOUR_DEMO_VIDEO_URL)
```

A GitHub-friendly alternative is to place a thumbnail above the link:

``` markdown
[![AI-Powered PTA CTDISR Compliance Audit System](docs/screenshots/demo-thumbnail.png)](YOUR_DEMO_VIDEO_URL)
```

------------------------------------------------------------------------

# 📊 Suggested GitHub Project Presentation

For the strongest professional presentation, the repository should
contain:

``` text
README.md
│
├── Project overview
├── Architecture
├── AI pipeline
├── Features
├── Screenshots
├── Demo video
├── Technology badges
├── Installation
├── API documentation
├── Model information
├── Project structure
└── Future improvements
```

A polished README should visually communicate:

``` text
What is it?
      ↓
Why does it matter?
      ↓
How does it work?
      ↓
What technologies are used?
      ↓
How can someone run it?
      ↓
What does the UI look like?
      ↓
What does the AI produce?
```

------------------------------------------------------------------------

# 🔍 Key Features

## 📚 Knowledge Base

-   Upload compliance documents
-   Categorize source material
-   Maintain document metadata
-   Process documents into searchable knowledge
-   Store embeddings and vector metadata
-   Support incremental knowledge updates

## 🛡️ CTDISR Controls

-   View control register
-   Search controls
-   Filter active/inactive controls
-   Create controls
-   Update controls
-   Deactivate controls
-   View control details
-   Run AI audit for individual controls

## 🤖 AI Auditing

-   Semantic retrieval
-   RAG context construction
-   Fine-tuned Llama model
-   Control-specific audit generation
-   PTA-oriented response generation
-   AI recommendations
-   Human auditor review

## 📊 Dashboard

-   Compliance statistics
-   Control statistics
-   Audit activity
-   Knowledge base information
-   AI engine status
-   Operational overview

## 👥 User Management

Administrator functionality includes:

-   User management
-   Role-based access
-   Account activation/deactivation where supported
-   Protected administrative routes

------------------------------------------------------------------------

# 🧭 Development Roadmap

## Completed / Implemented

-   [x] FastAPI backend
-   [x] React frontend
-   [x] Authentication
-   [x] Role-based access
-   [x] Dashboard
-   [x] Document upload
-   [x] CTDISR control management
-   [x] Control activation/deactivation workflow
-   [x] Control update workflow
-   [x] AI audit endpoint
-   [x] Document parsing
-   [x] Chunking pipeline
-   [x] Sentence Transformer embeddings
-   [x] FAISS vector indexing
-   [x] RAG retrieval
-   [x] Fine-tuned Llama inference
-   [x] Professional dark enterprise UI

## Future Improvements

-   [ ] PostgreSQL production persistence
-   [ ] pgvector integration where appropriate
-   [ ] Background processing with task queues
-   [ ] Audit report PDF export
-   [ ] Excel report export
-   [ ] Advanced audit history
-   [ ] Evidence attachment workflow
-   [ ] Explainable retrieval sources
-   [ ] Confidence scoring
-   [ ] Model evaluation dashboard
-   [ ] Automated regression testing
-   [ ] CI/CD pipeline
-   [ ] Production monitoring
-   [ ] Enterprise deployment

> Roadmap items should be marked as completed only after they are
> actually implemented in the repository.

------------------------------------------------------------------------

# 🧪 Quality & Evaluation

For an AI compliance system, evaluation should cover more than model
fluency.

Recommended evaluation dimensions:

  -----------------------------------------------------------------------
  Metric                              Purpose
  ----------------------------------- -----------------------------------
  Retrieval Precision                 Are relevant compliance documents
                                      retrieved?

  Retrieval Recall                    Are important evidence chunks
                                      missed?

  Groundedness                        Is the AI response supported by
                                      retrieved evidence?

  Control Relevance                   Does the generated response address
                                      the correct control?

  Recommendation Quality              Are recommendations useful and
                                      actionable?

  Hallucination Rate                  Does the model invent unsupported
                                      information?

  Human Agreement                     How often do auditors accept/edit
                                      AI findings?

  Latency                             How long does an audit request
                                      take?
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# ⚠️ Important AI Disclaimer

This platform is intended as an **AI-assisted compliance auditing
system**.

AI-generated outputs should be reviewed by a qualified auditor before
they are treated as final compliance findings.

The system should not be interpreted as replacing:

-   official regulatory interpretation
-   organizational compliance officers
-   auditors
-   legal advice
-   final management approval

The AI should assist the auditor by improving retrieval, analysis and
drafting.

------------------------------------------------------------------------

# 🔒 Security Recommendations

Before production deployment:

-   Never commit `.env`
-   Never commit access tokens
-   Never commit passwords
-   Protect model files where licensing requires it
-   Apply HTTPS/TLS
-   Use secure token expiration
-   Validate uploaded file types
-   Limit upload sizes
-   Scan uploaded files
-   Apply role-based authorization server-side
-   Log security-sensitive events
-   Restrict Swagger access in production if required
-   Back up audit records
-   Protect compliance documents
-   Apply least-privilege access

------------------------------------------------------------------------

# 📁 Recommended Repository Structure

A polished final repository can look like:

``` text
AI-Powered_PTA-CTDISR-Compliance-Audit-System/
│
├── backend/
│   ├── app/
│   ├── models/
│   ├── storage/
│   ├── .env.example
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── docs/
│   ├── architecture/
│   │   └── system-architecture.png
│   └── screenshots/
│       ├── dashboard.png
│       ├── documents.png
│       ├── controls.png
│       ├── audits.png
│       └── audit-result.png
│
├── training/
│   ├── dataset/
│   └── notebooks/
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

------------------------------------------------------------------------

# 👩‍💻 Development

## Backend

``` bash
cd backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

## Frontend

``` bash
cd frontend
npm install
npm run dev
```

------------------------------------------------------------------------

# 📝 Example Control Audit

A control can be processed through:

``` text
POST /api/v1/ctdisr/controls/4.4/audit
```

with parameters such as:

``` text
top_k = 5
max_new_tokens = 400
```

The system retrieves relevant knowledge and passes the resulting context
to the fine-tuned Llama inference layer.

------------------------------------------------------------------------

# 📚 Documentation

API documentation:

``` text
/api/v1
```

Swagger UI:

``` text
/docs
```

ReDoc:

``` text
/redoc
```

Local development:

``` text
Backend  → http://127.0.0.1:8000
Swagger  → http://127.0.0.1:8000/docs
Frontend → http://localhost:5173
```

------------------------------------------------------------------------

# 🤝 Contributing

Contributions should follow the project architecture.

Before submitting changes:

1.  Verify backend imports.
2.  Run the API locally.
3.  Test the relevant endpoint through Swagger.
4.  Run the frontend.
5.  Check authentication behavior.
6.  Test the affected UI workflow.
7.  Confirm no secrets are included.
8.  Update documentation when architecture changes.

------------------------------------------------------------------------

# 📜 License

This project is currently intended for academic, research, internship
and organizational development purposes.

Add the final license here once the repository owner has selected the
appropriate license.

------------------------------------------------------------------------

# ⭐ Project Summary

The **AI-Powered PTA CTDISR Compliance Audit System** combines modern
web engineering and applied artificial intelligence to create a
practical compliance-auditing workflow.

``` text
Enterprise Web Application
          +
Knowledge Base
          +
Semantic Search
          +
RAG
          +
Fine-Tuned LLM
          +
Human Auditor Review
          =
AI-Assisted CTDISR Compliance Auditing
```

------------------------------------------------------------------------

::: {align="center"}
### Built with Python • FastAPI • React • PyTorch • Transformers • RAG • FAISS • Llama

**AI-assisted. Evidence-grounded. Human-reviewed.**
:::
