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
