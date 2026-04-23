from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def transcribe_audio(
        self,
        *,
        file_bytes: bytes,
        filename: str,
        mime_type: str | None = None,
    ) -> str:
        raise NotImplementedError
