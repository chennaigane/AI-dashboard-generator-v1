# Automated Dashboard Generator & Insights Provider (Micro SaaS)

This repo is a turnkey starter to upload CSV/Excel data and get back:
- A dataset profile & preview
- Suggested dashboard visuals
- Actionable insights
- Power BI DAX templates

## Tech Stack
- **Backend:** FastAPI (Python 3.11)
- **Frontend:** Vite + React
- **AI Prompt Library:** YAML prompt spec to guide LLM outputs
- **Deploy:** Render (backend), Vercel/Static host (frontend), Dockerfiles included

## Local Dev
### 1) Backend
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

### 2) Frontend
```bash
cd frontend
npm install
# Create .env with: VITE_API_BASE=http://localhost:8000
npm run dev
```

## Deploy (Render + Vercel)
- Backend: connect your GitHub repo to Render using `infrastructure/render/render.yaml` or choose "FastAPI" and set start command:
  `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`
- Frontend: Deploy to Vercel or any static host. Set `VITE_API_BASE` env to your backend URL.

## Endpoints
- `GET /api/health/ping` → health
- `POST /api/analyze/upload` (multipart file: csv/xlsx) → JSON with profile + specs + insights

## Folder Structure
- `backend/` FastAPI app and services
- `frontend/` React app (file upload + results viewer)
- `ai/` Prompt library YAML
- `infrastructure/` Dockerfiles + sample Render config
- `samples/` Example CSV
- `powerbi/` Notes and DAX helpers

## Notes
- This is a heuristic starter. You can plug in an LLM (OpenAI/Anthropic) server-side to enrich insights using `ai/prompt_library/master.yaml`.
- For Excel uploads larger than a few MB, consider streaming & chunked processing.
