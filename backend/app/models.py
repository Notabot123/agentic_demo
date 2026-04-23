from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class StageStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class InterviewSummary(BaseModel):
    problem: str
    user_goals: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    key_quotes: list[str] = Field(default_factory=list)
    actors: list[str] = Field(default_factory=list)
    signals_of_value: list[str] = Field(default_factory=list)


class UserStory(BaseModel):
    story_id: str
    title: str
    as_a: str
    i_want: str
    so_that: str
    narrative: str
    acceptance_criteria: list[str] = Field(default_factory=list)
    business_value: str
    priority: str = "Medium"


class TaskItem(BaseModel):
    task_id: str
    story_id: str
    title: str
    description: str
    task_type: str
    priority: str
    owner_hint: str
    dependencies: list[str] = Field(default_factory=list)
    gherkin: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    status: str = "Proposed"


class DuplicateSuggestion(BaseModel):
    task_id: str
    possible_duplicate_of: str
    reason: str
    recommendation: str


class PipelineResponse(BaseModel):
    cleaned_transcript: str
    interview_summary: InterviewSummary
    user_story: UserStory
    tasks: list[TaskItem]
    duplicates: list[DuplicateSuggestion]
    export_path: str
    stage_status: dict[str, StageStatus]
    dataset_size: int
    raw: dict[str, Any] = Field(default_factory=dict)


class RunPipelineRequest(BaseModel):
    transcript: str = Field(min_length=20)


class RequirementRow(BaseModel):
    story_id: str
    story_title: str
    task_id: str
    task_title: str
    task_type: str
    priority: str
    status: str
    owner_hint: str
    dependencies: str
    gherkin: str
    acceptance_criteria: str
    business_value: str
    source_excerpt: str


class SearchResponse(BaseModel):
    count: int
    items: list[RequirementRow]


class GraphNode(BaseModel):
    id: str
    label: str
    kind: str


class GraphEdge(BaseModel):
    source: str
    target: str


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
