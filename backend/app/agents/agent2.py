from app.agents.prompts import USER_STORY_SYSTEM
from app.models import InterviewSummary, UserStory
from app.providers.base import LLMProvider
from app.schemas import USER_STORY_SCHEMA


def generate_user_story(provider: LLMProvider, interview_summary: InterviewSummary) -> UserStory:
    result = provider.generate_structured(
        system_prompt=USER_STORY_SYSTEM,
        user_prompt=(
            "Create a parent user story from this interview summary:\n\n"
            f"{interview_summary.model_dump_json(indent=2)}"
        ),
        json_schema=USER_STORY_SCHEMA,
    )
    return UserStory.model_validate(result)
