from app.agents.prompts import TRANSCRIPT_CLEAN_SYSTEM, INTERVIEW_SUMMARY_SYSTEM
from app.models import InterviewSummary
from app.providers.base import LLMProvider
from app.schemas import TRANSCRIPT_CLEAN_SCHEMA, INTERVIEW_SUMMARY_SCHEMA


def clean_transcript(provider: LLMProvider, transcript: str) -> str:
    result = provider.generate_structured(
        system_prompt=TRANSCRIPT_CLEAN_SYSTEM,
        user_prompt=f"Clean this Teams interview transcript:\n\n{transcript}",
        json_schema=TRANSCRIPT_CLEAN_SCHEMA,
    )
    return result["cleaned_transcript"]


def summarise_interview(provider: LLMProvider, cleaned_transcript: str) -> InterviewSummary:
    result = provider.generate_structured(
        system_prompt=INTERVIEW_SUMMARY_SYSTEM,
        user_prompt=f"Summarise this cleaned interview transcript:\n\n{cleaned_transcript}",
        json_schema=INTERVIEW_SUMMARY_SCHEMA,
    )
    return InterviewSummary.model_validate(result)
