# PTA CTDISR Compliance Audit System — React Frontend

This is the first production-oriented React frontend slice for the existing FastAPI backend.

## Implemented

- Dark graphite / emerald enterprise design
- JWT login using `/api/v1/auth/login`
- Role-aware navigation for Administrator vs Auditor
- Dashboard using live `/api/v1/dashboard/statistics`
- CTDISR control list/search
- Admin-only control creation
- Control details and editing
- AI audit execution using `/api/v1/ctdisr/controls/{control_id}/audit`
- Saved audit list/detail/edit
- Document upload + automatic processing
- Admin-only auditor account creation
- Axios authentication interceptor
- Vite development proxy to `http://localhost:8000`

## Important backend alignment

The current `backend/app/main.py` mounts authentication, uploads, CTDISR controls, saved audit results, and dashboard routes. It does **not** currently mount a document inventory/list endpoint, policy/advisory/assets listing endpoints, or report/export endpoints.

Therefore this frontend does not invent those endpoints. The Documents page currently implements the real upload/processing workflow and explicitly identifies the missing inventory API.

## Run locally

From `frontend/`:

```powershell
npm install
npm run dev
```

Open:

`http://localhost:5173`

The Vite proxy sends `/api/*` requests to `http://localhost:8000`.

For a different backend URL, create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Next backend slice

To reproduce the full supplied UI mockup, the next backend additions should be:

1. `GET /api/v1/documents`
2. `GET /api/v1/documents/{document_id}`
3. `GET /api/v1/documents/{document_id}/content` or a secure file-stream endpoint
4. `GET /api/v1/reports`
5. PDF/Excel export download endpoints

Those can then be wired into the document table, PDF viewer, metadata slide-over, and reports/export screens without mock data.
