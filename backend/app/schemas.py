TRANSCRIPT_CLEAN_SCHEMA = {
    "name": "transcript_clean",
    "schema": {
        "type": "object",
        "properties": {
            "cleaned_transcript": {"type": "string"},
            "speaker_map": {
                "type": "array",
                "items": {"type": "string"},
            },
            "notes": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "required": ["cleaned_transcript", "speaker_map", "notes"],
        "additionalProperties": False,
    },
    "strict": True,
}

INTERVIEW_SUMMARY_SCHEMA = {
    "name": "interview_summary",
    "schema": {
        "type": "object",
        "properties": {
            "problem": {"type": "string"},
            "user_goals": {"type": "array", "items": {"type": "string"}},
            "pain_points": {"type": "array", "items": {"type": "string"}},
            "constraints": {"type": "array", "items": {"type": "string"}},
            "key_quotes": {"type": "array", "items": {"type": "string"}},
            "actors": {"type": "array", "items": {"type": "string"}},
            "signals_of_value": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "problem",
            "user_goals",
            "pain_points",
            "constraints",
            "key_quotes",
            "actors",
            "signals_of_value",
        ],
        "additionalProperties": False,
    },
    "strict": True,
}

USER_STORY_SCHEMA = {
    "name": "user_story",
    "schema": {
        "type": "object",
        "properties": {
            "story_id": {"type": "string"},
            "title": {"type": "string"},
            "as_a": {"type": "string"},
            "i_want": {"type": "string"},
            "so_that": {"type": "string"},
            "narrative": {"type": "string"},
            "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
            "business_value": {"type": "string"},
            "priority": {"type": "string"},
        },
        "required": [
            "story_id",
            "title",
            "as_a",
            "i_want",
            "so_that",
            "narrative",
            "acceptance_criteria",
            "business_value",
            "priority",
        ],
        "additionalProperties": False,
    },
    "strict": True,
}

TASKS_SCHEMA = {
    "name": "task_breakdown",
    "schema": {
        "type": "object",
        "properties": {
            "tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "story_id": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "task_type": {"type": "string"},
                        "priority": {"type": "string"},
                        "owner_hint": {"type": "string"},
                        "dependencies": {"type": "array", "items": {"type": "string"}},
                        "gherkin": {"type": "array", "items": {"type": "string"}},
                        "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
                        "status": {"type": "string"},
                    },
                    "required": [
                        "task_id",
                        "story_id",
                        "title",
                        "description",
                        "task_type",
                        "priority",
                        "owner_hint",
                        "dependencies",
                        "gherkin",
                        "acceptance_criteria",
                        "status",
                    ],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["tasks"],
        "additionalProperties": False,
    },
    "strict": True,
}

DUPLICATES_SCHEMA = {
    "name": "duplicate_review",
    "schema": {
        "type": "object",
        "properties": {
            "duplicates": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "possible_duplicate_of": {"type": "string"},
                        "reason": {"type": "string"},
                        "recommendation": {"type": "string"},
                    },
                    "required": [
                        "task_id",
                        "possible_duplicate_of",
                        "reason",
                        "recommendation",
                    ],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["duplicates"],
        "additionalProperties": False,
    },
    "strict": True,
}
