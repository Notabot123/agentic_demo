from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.agent1 import clean_transcript, summarise_interview
from app.agents.agent2 import generate_user_story
from app.agents.agent3 import generate_tasks, review_duplicates
from app.models import DuplicateSuggestion, InterviewSummary, TaskItem, UserStory
from app.providers.factory import get_provider


class PipelineState(TypedDict, total=False):
    transcript: str
    cleaned_transcript: str
    interview_summary: InterviewSummary
    user_story: UserStory
    tasks: list[TaskItem]
    duplicates: list[DuplicateSuggestion]


def clean_node(state: PipelineState) -> PipelineState:
    provider = get_provider()
    return {"cleaned_transcript": clean_transcript(provider, state["transcript"])}


def summary_node(state: PipelineState) -> PipelineState:
    provider = get_provider()
    return {
        "interview_summary": summarise_interview(provider, state["cleaned_transcript"])
    }


def story_node(state: PipelineState) -> PipelineState:
    provider = get_provider()
    return {"user_story": generate_user_story(provider, state["interview_summary"])}


def tasks_node(state: PipelineState) -> PipelineState:
    provider = get_provider()
    tasks = generate_tasks(provider, state["user_story"])
    return {"tasks": tasks}


def duplicates_node(state: PipelineState) -> PipelineState:
    provider = get_provider()
    duplicates = review_duplicates(provider, state["tasks"])
    return {"duplicates": duplicates}


def build_graph():
    workflow = StateGraph(PipelineState)
    workflow.add_node("clean_transcript", clean_node)
    workflow.add_node("summarise_interview", summary_node)
    workflow.add_node("generate_user_story", story_node)
    workflow.add_node("generate_tasks", tasks_node)
    workflow.add_node("review_duplicates", duplicates_node)

    workflow.add_edge(START, "clean_transcript")
    workflow.add_edge("clean_transcript", "summarise_interview")
    workflow.add_edge("summarise_interview", "generate_user_story")
    workflow.add_edge("generate_user_story", "generate_tasks")
    workflow.add_edge("generate_tasks", "review_duplicates")
    workflow.add_edge("review_duplicates", END)

    return workflow.compile()


pipeline_graph = build_graph()
