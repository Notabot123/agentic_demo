import json
from io import BytesIO
from typing import Any

from openai import OpenAI

from app.config import settings
from app.providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        response = self.client.chat.completions.create(
            model=model or settings.llm_model,
            temperature=0.2,
            response_format={
                "type": "json_schema",
                "json_schema": json_schema,
            },
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    def transcribe_audio(
        self,
        *,
        file_bytes: bytes,
        filename: str,
        mime_type: str | None = None,
    ) -> str:
        audio_file = BytesIO(file_bytes)
        audio_file.name = filename
        transcript = self.client.audio.transcriptions.create(
            model=settings.openai_transcription_model,
            file=audio_file,
        )
        return getattr(transcript, "text", "") or ""
