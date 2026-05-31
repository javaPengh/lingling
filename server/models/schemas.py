from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from server.core.enums import LearningState, TeachingStrategy, VisualAidType
from server.models.entities import LearningEvent, ReviewTask, StudentKnowledge, StudentProfile


def to_camel(value: str) -> str:
    head, *tail = value.split("_")
    return head + "".join(part.capitalize() for part in tail)


class ApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        use_enum_values=True,
    )


class HealthResponse(ApiModel):
    ok: bool = True
    service: str = "lingling-server"
    mode: str


class StudentSummary(ApiModel):
    id: str
    name: str
    grade: str
    profile_label: str | None = None


class StudentsListResponse(ApiModel):
    students: list[StudentSummary]


class StartSessionRequest(ApiModel):
    student_id: str


class StartSessionResponse(ApiModel):
    session_id: str
    student_id: str
    started_at: str
    opening_message: str
    memory_summary: str
    recommended_question_id: str | None = None


class LearningTurnRequest(ApiModel):
    session_id: str
    student_id: str
    question_id: str | None = None
    student_input: str
    student_answer: str | None = None


class LearningTurnResponse(ApiModel):
    event_id: str
    state: LearningState
    state_evidence: str
    strategy: list[TeachingStrategy]
    strategy_reason: str
    care_triggered: bool
    visual_aid_used: VisualAidType
    tutor_response: str
    is_correct: bool | None = None
    error_cause: str | None = None
    error_detail: str | None = None
    knowledge_point_ids: list[str] = Field(default_factory=list)


class FinishSessionResponse(ApiModel):
    session_id: str
    student_id: str
    summary: str
    dominant_state: LearningState | None
    event_count: int
    review_tasks: list[ReviewTask]
    updated_profile: StudentProfile | None


class ObserverEvent(ApiModel):
    event: LearningEvent
    signals: list[str]


class ObserverSessionResponse(ApiModel):
    session_id: str
    student_id: str
    memory_summary: str
    events: list[LearningEvent]
    review_tasks: list[ReviewTask]


class ReportResponse(ApiModel):
    student_id: str
    student_name: str
    teacher_summary: str
    parent_summary: str
    weak_points: list[StudentKnowledge]
    review_tasks: list[ReviewTask]
    recent_events: list[LearningEvent]
    profile: StudentProfile | None


class RuleSignal(ApiModel):
    code: str
    description: str
    severity: str = "low"


class EmotionRecognitionInput(ApiModel):
    student_input: str
    is_correct: bool | None = None
    knowledge_point_ids: list[str] = Field(default_factory=list)
    rule_signals: list[RuleSignal] = Field(default_factory=list)
    history_summary: str | None = None
    recent_turns: list[str] = Field(default_factory=list)


class EmotionRecognitionResult(ApiModel):
    state: LearningState
    confidence: float
    evidence: str


class GenerateResponseInput(ApiModel):
    state: LearningState
    strategy: list[TeachingStrategy]
    care_triggered: bool
    visual_aid_used: VisualAidType
    question: dict[str, Any] | None = None
    student_input: str
    is_correct: bool | None = None
    error_cause: str | None = None
    error_detail: str | None = None


class GenerateResponseResult(ApiModel):
    tutor_response: str
