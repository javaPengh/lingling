from typing import Any

from pydantic import BaseModel, ConfigDict

from server.core.enums import (
    Difficulty,
    ErrorCause,
    LearningState,
    ReviewStatus,
    TeachingStrategy,
    VisualAidType,
)


JsonObject = dict[str, Any]


class EntityModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class Student(EntityModel):
    id: str
    name: str
    grade: str
    created_at: str


class StudentProfile(EntityModel):
    id: str
    student_id: str
    weak_points: list[str]
    recent_states: list[LearningState]
    effective_strategies: list[TeachingStrategy]
    learning_summary: str | None
    total_sessions: int
    updated_at: str


class KnowledgePoint(EntityModel):
    id: str
    name: str
    subject: str
    chapter: str | None = None
    parent_id: str | None = None


class StudentKnowledge(EntityModel):
    id: str
    student_id: str
    knowledge_point_id: str
    mastery: int
    attempts: int
    correct_count: int
    last_practiced_at: str | None = None


class TypicalError(EntityModel):
    cause: ErrorCause
    detail: str


class Question(EntityModel):
    id: str
    stem: str
    standard_answer: str
    solution: str
    difficulty: Difficulty
    typical_errors: list[TypicalError]
    visual_aid_type: VisualAidType
    visual_aid_spec: JsonObject | None = None


class QuestionKnowledge(EntityModel):
    id: str
    question_id: str
    knowledge_point_id: str


class LearningSession(EntityModel):
    id: str
    student_id: str
    started_at: str
    ended_at: str | None = None
    dominant_state: LearningState | None = None
    summary: str | None = None
    event_count: int = 0


class LearningEvent(EntityModel):
    id: str
    session_id: str
    student_id: str
    question_id: str | None
    sequence: int
    student_input: str | None
    student_answer: str | None
    is_correct: bool | None
    knowledge_point_ids: list[str]
    error_cause: ErrorCause | None
    error_detail: str | None
    state: LearningState
    state_evidence: str
    strategy: list[TeachingStrategy]
    strategy_reason: str
    care_triggered: bool
    visual_aid_used: VisualAidType
    tutor_response: str
    created_at: str


class ReviewTask(EntityModel):
    id: str
    student_id: str
    knowledge_point_id: str
    source_event_id: str | None
    reason: str
    recommended_question_id: str | None
    status: ReviewStatus
    due_date: str | None
    created_at: str
