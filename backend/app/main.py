from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.graph import pipeline_graph
from app.models import PipelineResponse, RunPipelineRequest, SearchResponse, StageStatus
from app.providers.factory import get_provider
from app.services.excel_export import export_rows_to_excel
from app.services.graph_view import build_graph
from app.services.store import append_story_and_tasks, search_rows


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.data_path.mkdir(parents=True, exist_ok=True)
    if not settings.store_path.exists():
        settings.store_path.write_text('{"stories": [], "rows": []}', encoding="utf-8")
    if not settings.sample_transcript_path.exists():
        settings.sample_transcript_path.write_text(
            "Interviewer: Can you walk me through the pain points in capturing user requirements?\n"
            "User: Notes live in Teams calls, then someone manually copies them into backlog items and spreadsheets. "
            "We lose nuance, repeat work, and miss acceptance criteria.\n",
            encoding="utf-8",
        )
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] #[settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "provider": settings.llm_provider, "model": settings.llm_model}


@app.get("/api/sample-transcript")
def sample_transcript():
    return {"transcript": settings.sample_transcript_path.read_text(encoding="utf-8")}


@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    if not settings.enable_audio_transcription:
        raise HTTPException(status_code=400, detail="Audio transcription is disabled.")
    provider = get_provider()
    try:
        content = await file.read()
        transcript = provider.transcribe_audio(
            file_bytes=content,
            filename=file.filename or "audio.wav",
            mime_type=file.content_type,
        )
        return {"transcript": transcript}
    except NotImplementedError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {exc}") from exc


@app.post("/api/run", response_model=PipelineResponse)
def run_pipeline(payload: RunPipelineRequest):
    stage_status = {
        "clean_transcript": StageStatus.running,
        "summarise_interview": StageStatus.pending,
        "generate_user_story": StageStatus.pending,
        "generate_tasks": StageStatus.pending,
        "review_duplicates": StageStatus.pending,
        "export_excel": StageStatus.pending,
    }

    try:
        result = pipeline_graph.invoke({"transcript": payload.transcript})

        stage_status["clean_transcript"] = StageStatus.completed
        stage_status["summarise_interview"] = StageStatus.completed
        stage_status["generate_user_story"] = StageStatus.completed
        stage_status["generate_tasks"] = StageStatus.completed
        stage_status["review_duplicates"] = StageStatus.completed

        store = append_story_and_tasks(
            user_story=result["user_story"],
            tasks=result["tasks"],
            source_excerpt=result["cleaned_transcript"],
        )
        export_path = export_rows_to_excel(store["rows"])
        stage_status["export_excel"] = StageStatus.completed

        return PipelineResponse(
            cleaned_transcript=result["cleaned_transcript"],
            interview_summary=result["interview_summary"],
            user_story=result["user_story"],
            tasks=result["tasks"],
            duplicates=result["duplicates"],
            export_path=str(export_path),
            stage_status=stage_status,
            dataset_size=len(store["rows"]),
            raw={
                "story_count": len(store["stories"]),
                "task_count": len(store["rows"]),
            },
        )
    except Exception as exc:
        for key, value in list(stage_status.items()):
            if value == StageStatus.running:
                stage_status[key] = StageStatus.failed
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {exc}") from exc


@app.get("/api/requirements", response_model=SearchResponse)
def requirements(search: str | None = None):
    rows = search_rows(search)
    return SearchResponse(count=len(rows), items=rows)


@app.get("/api/graph")
def graph():
    return build_graph()
