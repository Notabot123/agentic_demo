from app.agents.prompts import TASK_BREAKDOWN_SYSTEM, DUPLICATE_REVIEW_SYSTEM
from app.models import DuplicateSuggestion, TaskItem, UserStory
from app.providers.base import LLMProvider
from app.schemas import DUPLICATES_SCHEMA, TASKS_SCHEMA
from uuid import uuid4

def generate_tasks(provider: LLMProvider, user_story: UserStory) -> list[TaskItem]:
    result = provider.generate_structured(
        system_prompt=TASK_BREAKDOWN_SYSTEM,
        user_prompt=(
            "Break this user story into delivery-ready tasks with BDD/Gherkin:\n\n"
            f"{user_story.model_dump_json(indent=2)}"
        ),
        json_schema=TASKS_SCHEMA,
    )

    tasks = [TaskItem.model_validate(item) for item in result["tasks"]]

    # Unique IDs
    for i, task in enumerate(tasks, start=1):
        task.id = f"{user_story.story_id}-T{i}-{uuid4().hex[:6]}"

    return tasks


def review_duplicates(provider: LLMProvider, tasks: list[TaskItem]) -> list[DuplicateSuggestion]:
    result = provider.generate_structured(
        system_prompt=DUPLICATE_REVIEW_SYSTEM,
        user_prompt=(
            "Review these tasks for duplicate or overlapping scope:\n\n"
            + "\n".join(task.model_dump_json() for task in tasks)
        ),
        json_schema=DUPLICATES_SCHEMA,
    )
    return [DuplicateSuggestion.model_validate(item) for item in result["duplicates"]]
