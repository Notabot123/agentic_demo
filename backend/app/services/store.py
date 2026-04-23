import json
from pathlib import Path
from typing import Any

from app.config import settings
from app.models import RequirementRow, TaskItem, UserStory


def _read_store() -> dict[str, Any]:
    path = settings.store_path
    if not path.exists():
        return {"stories": [], "rows": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_store(data: dict[str, Any]) -> None:
    settings.store_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def append_story_and_tasks(
    *,
    user_story: UserStory,
    tasks: list[TaskItem],
    source_excerpt: str,
) -> dict[str, Any]:
    store = _read_store()

    store["stories"].append(user_story.model_dump())

    rows: list[dict[str, Any]] = []
    for task in tasks:
        row = RequirementRow(
            story_id=user_story.story_id,
            story_title=user_story.title,
            task_id=task.task_id,
            task_title=task.title,
            task_type=task.task_type,
            priority=task.priority,
            status=task.status,
            owner_hint=task.owner_hint,
            dependencies=", ".join(task.dependencies),
            gherkin="\n".join(task.gherkin),
            acceptance_criteria="\n".join(task.acceptance_criteria),
            business_value=user_story.business_value,
            source_excerpt=source_excerpt[:500],
        )
        rows.append(row.model_dump())

    store["rows"].extend(rows)
    _write_store(store)
    return store


def search_rows(search: str | None = None) -> list[RequirementRow]:
    store = _read_store()
    rows = [RequirementRow.model_validate(row) for row in store.get("rows", [])]
    if not search:
        return rows
    needle = search.lower().strip()
    return [
        row
        for row in rows
        if needle in row.task_title.lower()
        or needle in row.story_title.lower()
        or needle in row.acceptance_criteria.lower()
        or needle in row.gherkin.lower()
        or needle in row.owner_hint.lower()
        or needle in row.status.lower()
    ]
