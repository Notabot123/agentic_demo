# Agentic AI Demo: Teams Transcript → User Story → Tasks → Excel

A demo-friendly requirements engineering workflow using **FastAPI**, **LangGraph**, **React**, and a **modular AI provider layer**.

## What it does

1. Accepts a **Teams transcript** pasted into the UI.
2. Optionally accepts **audio upload** and transcribes it with OpenAI speech-to-text.
3. Cleans and structures the interview.
4. Produces:
   - interview summary
   - parent user story
   - task-level technical requirements
   - Gherkin / BDD acceptance criteria
   - simple task dependencies
   - duplicate / near-duplicate suggestions
5. Persists the results to canonical JSON.
6. Regenerates an `.xlsx` workbook with **one row per task** and a link back to the parent user story.
7. Exposes search and graph endpoints for the frontend.

## Why this structure works well for a live demo

- The pipeline is deterministic and stepwise.
- Every stage is visible in the UI.
- The spreadsheet is updated on every run.
- The provider layer is swappable with an environment variable.
- Optional transcription is available, but **Teams native transcripts are usually the simplest live-demo path**.

## Recommended live-demo path

Use a real or synthetic Teams transcript export if one is already available. Microsoft documents that meeting transcripts can be downloaded after the meeting, and Microsoft Graph can also fetch transcripts programmatically in post-meeting flows. Optional speech-to-text remains useful when you only have audio or want to demonstrate a second input path. See the sources cited in the chat response for the current Microsoft and OpenAI references.

## Project structure

```text
agentic-ai-demo/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── providers/
│   │   ├── services/
│   │   ├── config.py
│   │   ├── graph.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── data/
│   │   ├── requirements_store.json
│   │   └── sample_transcript.txt
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── .env.example
├── .gitignore
└── README.md
```

## Features included

- FastAPI backend
- React + Vite frontend
- LangGraph orchestration
- OpenAI and Gemini provider abstraction
- Optional OpenAI transcription endpoint
- Task-level Excel export
- Search over generated requirements
- Status view for agent stages
- Simple dependency graph
- Duplicate recommendation panel

## Environment variables

Copy `.env.example` to `.env` and fill in what you need.

### Core
- `LLM_PROVIDER=openai` or `gemini`
- `OPENAI_API_KEY=...`
- `GEMINI_API_KEY=...`
- `LLM_MODEL=gpt-4o-mini`
- `OPENAI_TRANSCRIPTION_MODEL=whisper-1`
- `ENABLE_AUDIO_TRANSCRIPTION=true`

### Frontend
- `VITE_API_BASE_URL=http://localhost:8000`

## Run locally

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn app.main:app --reload --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL:
- http://localhost:5173

Backend default URL:
- http://localhost:8000

## Typical demo script

1. Paste a Teams transcript into the UI.
2. Click **Run pipeline**.
3. Walk through:
   - cleaned transcript
   - summary
   - user story
   - generated tasks
   - duplicate recommendations
   - dependency graph
4. Download or open the exported spreadsheet path shown in the result.
5. Use the search box to show retrieval over the generated dataset.

## Example parent / child model

- `story_id`: `STORY-20260422-001`
- task rows:
  - `TASK-20260422-001`
  - `TASK-20260422-002`
  - `TASK-20260422-003`

Each task row keeps the parent `story_id` so the sheet works for both delivery tracking and story roll-up.

## Provider abstraction

The backend imports a provider implementation from:

- `app/providers/openai_provider.py`
- `app/providers/gemini_provider.py`

The active provider is selected by the `LLM_PROVIDER` environment variable through a single `get_provider()` factory.

## Notes on transcription

For a stakeholder demo, native Teams transcript input is usually more reliable than live audio transcription. Optional OpenAI speech-to-text is included because:
- it shows multimodal capability
- it covers situations where only audio exists
- it gives you a second demo path

## Follow-up ideas already scaffolded

The current structure makes it easy to extend with:
- retrieval-augmented search over historic requirements
- duplicate clustering
- impact analysis
- Jira / Azure DevOps push
- Microsoft Graph ingestion of Teams transcripts
- approval workflows
- embeddings-based similarity search

## Troubleshooting

### CORS
If the frontend cannot call the API, confirm `FRONTEND_ORIGIN` in `.env`.

### No transcription
Set:
- `ENABLE_AUDIO_TRANSCRIPTION=true`
- `OPENAI_API_KEY`
- `OPENAI_TRANSCRIPTION_MODEL=whisper-1`

### Gemini support
Gemini support is intentionally thin and modular. If you prefer, you can swap it to the OpenAI-compatible Gemini endpoint later without changing the graph shape.

## Suggested git commit message

```text
feat: add agentic requirements demo with fastapi, react, langgraph, excel export, and modular llm providers
```
