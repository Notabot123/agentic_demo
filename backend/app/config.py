from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # project root

class Settings(BaseSettings):
    app_name: str = "Agentic AI Demo"
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    openai_api_key: str | None = None
    openai_transcription_model: str = "whisper-1"
    enable_audio_transcription: bool = True

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    frontend_origin: str = "http://localhost:5173"
    data_dir: Path = BASE_DIR / "data"
    export_filename: str = "requirements_export.xlsx"

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def data_path(self) -> Path:
        path = Path(self.data_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def export_path(self) -> Path:
        return self.data_path / self.export_filename

    @property
    def store_path(self) -> Path:
        return self.data_path / "requirements_store.json"

    @property
    def sample_transcript_path(self) -> Path:
        return self.data_path / "sample_transcript.txt"


settings = Settings()
