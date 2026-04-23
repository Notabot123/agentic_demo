import json
from typing import Any

from google import genai

from app.config import settings
from app.providers.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")
        self.client = genai.Client(api_key=settings.gemini_api_key)

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        response = self.client.models.generate_content(
            model=model or settings.gemini_model,
            contents=f"{system_prompt}\n\n{user_prompt}",
            config={
                "response_mime_type": "application/json",
                "response_json_schema": json_schema["schema"],
                "temperature": 0.2,
            },
        )
        text = getattr(response, "text", "") or "{}"
        return json.loads(text)

    def transcribe_audio(
        self,
        *,
        file_bytes: bytes,
        filename: str,
        mime_type: str | None = None,
    ) -> str:
        raise NotImplementedError(
            "Audio transcription is only wired for OpenAI in this starter. "
            "Use transcript input or switch transcription implementation."
        )
