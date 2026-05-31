"""教学编排器服务。

串联记忆读取、深图分析、状态识别、策略决策、LLM 回复、事件写入和会话写回。
"""

from datetime import datetime, timezone
import sqlite3
from uuid import uuid4

from server.core.enums import LearningState, TeachingStrategy, VisualAidType
from server.dao import session_dao, student_dao
from server.llm.base import LlmError
from server.llm.client import get_llm_client
from server.llm.mock_client import MockLlmClient
from server.models.entities import LearningEvent, LearningSession
from server.models.schemas import (
    FinishSessionResponse,
    GenerateResponseInput,
    LearningTurnRequest,
    LearningTurnResponse,
    StartSessionResponse,
)
from server.services.analyzer import analyze_turn
from server.services.memory import build_opening_message, read_memory, summarize_session, write_back_memory
from server.services.review_planner import create_review_tasks
from server.services.state_recognizer import StateRecognitionResult, recognize_state


def start_session(connection: sqlite3.Connection, student_id: str) -> StartSessionResponse:
    """创建学习会话，并返回开场语、记忆摘要和推荐题目。"""

    student = student_dao.get_student(connection, student_id)
    if student is None:
        raise ValueError(f"Student not found: {student_id}")
    started_at = now_iso()
    session = LearningSession(
        id=f"sess_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{uuid4().hex[:6]}",
        student_id=student_id,
        started_at=started_at,
        event_count=0,
    )
    session_dao.insert_session(connection, session)
    memory = read_memory(connection, student_id)
    connection.commit()
    return StartSessionResponse(
        session_id=session.id,
        student_id=student_id,
        started_at=started_at,
        opening_message=build_opening_message(memory, student.name),
        memory_summary=memory.history_summary,
        recommended_question_id=_recommended_start_question(student_id, memory.profile.weak_points if memory.profile else []),
    )


def handle_learning_turn(connection: sqlite3.Connection, request: LearningTurnRequest) -> LearningTurnResponse:
    """处理一轮学习输入，写入结构化学习事件并返回教学回应。"""

    session = session_dao.get_session(connection, request.session_id)
    if session is None:
        raise ValueError(f"Session not found: {request.session_id}")
    if session.student_id != request.student_id:
        raise ValueError("Session/student mismatch")

    analysis = analyze_turn(connection, request.question_id, request.student_input, request.student_answer)
    prior_events = session_dao.list_events_by_session(connection, request.session_id)
    memory = read_memory(connection, request.student_id)
    recognition = recognize_state(
        connection,
        request.student_input,
        analysis.is_correct,
        analysis.knowledge_point_ids,
        prior_events,
        memory,
    )
    care_triggered = _care_triggered(recognition, memory)
    visual_aid_used = _visual_aid(analysis.question.visual_aid_type if analysis.question else "none", recognition, analysis.is_correct)
    strategy = _decide_strategy(recognition, analysis.is_correct, care_triggered)
    strategy_reason = _strategy_reason(recognition, analysis.is_correct, strategy, care_triggered, visual_aid_used)
    tutor_response = _generate_tutor_response(
        state=recognition.state,
        strategy=strategy,
        care_triggered=care_triggered,
        visual_aid_used=visual_aid_used,
        question_stem=analysis.question.stem if analysis.question else None,
        question_solution=analysis.question.solution if analysis.question else None,
        student_input=request.student_input,
        is_correct=analysis.is_correct,
        error_cause=analysis.error_cause,
        error_detail=analysis.error_detail,
    )

    sequence = session_dao.next_event_sequence(connection, request.session_id)
    event = LearningEvent(
        id=f"evt_{request.session_id}_{sequence}",
        session_id=request.session_id,
        student_id=request.student_id,
        question_id=request.question_id,
        sequence=sequence,
        student_input=request.student_input,
        student_answer=request.student_answer,
        is_correct=analysis.is_correct,
        knowledge_point_ids=analysis.knowledge_point_ids,
        error_cause=analysis.error_cause,
        error_detail=analysis.error_detail,
        state=recognition.state,
        state_evidence=recognition.evidence,
        strategy=strategy,
        strategy_reason=strategy_reason,
        care_triggered=care_triggered,
        visual_aid_used=visual_aid_used,
        tutor_response=tutor_response,
        created_at=now_iso(),
    )
    session_dao.insert_learning_event(connection, event)
    connection.commit()
    return LearningTurnResponse(
        event_id=event.id,
        state=event.state,
        state_evidence=event.state_evidence,
        strategy=event.strategy,
        strategy_reason=event.strategy_reason,
        care_triggered=event.care_triggered,
        visual_aid_used=event.visual_aid_used,
        tutor_response=event.tutor_response,
        is_correct=event.is_correct,
        error_cause=event.error_cause,
        error_detail=event.error_detail,
        knowledge_point_ids=event.knowledge_point_ids,
    )


def finish_session(connection: sqlite3.Connection, session_id: str) -> FinishSessionResponse:
    """结束学习会话，完成长期记忆写回和复习任务生成。"""

    session = session_dao.get_session(connection, session_id)
    if session is None:
        raise ValueError(f"Session not found: {session_id}")
    events = session_dao.list_events_by_session(connection, session_id)
    summary, dominant_state = summarize_session(events)
    ended_at = now_iso()
    profile = write_back_memory(connection, session.student_id, events, ended_at)
    review_tasks = create_review_tasks(connection, session.student_id, session_id, events, ended_at)
    session_dao.update_session_finish(connection, session_id, ended_at, dominant_state, summary, len(events))
    connection.commit()
    return FinishSessionResponse(
        session_id=session_id,
        student_id=session.student_id,
        summary=summary,
        dominant_state=dominant_state,
        event_count=len(events),
        review_tasks=review_tasks,
        updated_profile=profile,
    )


def now_iso() -> str:
    """返回 UTC ISO 8601 时间字符串。"""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _recommended_start_question(student_id: str, weak_points: list[str]) -> str:
    if student_id == "stu_002" or "kp_008" in weak_points:
        return "q_006"
    if student_id == "stu_003":
        return "q_007"
    return "q_001"


def _care_triggered(recognition: StateRecognitionResult, memory_snapshot) -> bool:
    del memory_snapshot
    codes = {signal.code for signal in recognition.rule_signals}
    if recognition.state in {LearningState.FRUSTRATED, LearningState.ANXIOUS, LearningState.TIRED}:
        return True
    if {"sig_giveup", "sig_self_doubt", "sig_consecutive_wrong"} & codes:
        return True
    return False


def _visual_aid(
    question_visual: str,
    recognition: StateRecognitionResult,
    is_correct: bool | None,
) -> VisualAidType:
    if question_visual == "none" or (recognition.state == LearningState.STABLE and is_correct is True):
        return VisualAidType.NONE
    if recognition.obstruction_count >= 2 or recognition.state in {LearningState.CONFUSED, LearningState.FRUSTRATED}:
        return VisualAidType(question_visual)
    return VisualAidType.NONE


def _decide_strategy(
    recognition: StateRecognitionResult, is_correct: bool | None, care_triggered: bool
) -> list[TeachingStrategy]:
    state = recognition.state
    if state == LearningState.FRUSTRATED:
        strategies = [TeachingStrategy.CARE, TeachingStrategy.HUMOR, TeachingStrategy.SMALL_STEP]
    elif state == LearningState.ANXIOUS:
        strategies = [TeachingStrategy.CARE, TeachingStrategy.HINT]
    elif state == LearningState.TIRED:
        strategies = [TeachingStrategy.CARE]
    elif state == LearningState.CONFUSED:
        strategies = [TeachingStrategy.HINT, TeachingStrategy.SOCRATIC]
    elif is_correct is True:
        strategies = [TeachingStrategy.SOCRATIC]
    elif is_correct is False:
        strategies = [TeachingStrategy.HINT, TeachingStrategy.SOCRATIC]
    else:
        strategies = [TeachingStrategy.SOCRATIC]

    if recognition.obstruction_count >= 3 and TeachingStrategy.SMALL_STEP not in strategies:
        strategies.append(TeachingStrategy.SMALL_STEP)
    if care_triggered and TeachingStrategy.CARE not in strategies:
        strategies.insert(0, TeachingStrategy.CARE)
    return list(dict.fromkeys(strategies))


def _strategy_reason(
    recognition: StateRecognitionResult,
    is_correct: bool | None,
    strategy: list[TeachingStrategy],
    care_triggered: bool,
    visual_aid_used: VisualAidType,
) -> str:
    answer_part = "本轮答对" if is_correct else "本轮答错" if is_correct is False else "本轮为追问/困惑表达"
    care_part = "触发主动关怀" if care_triggered else "未触发关怀"
    visual_part = f"视觉辅助={visual_aid_used}"
    return (
        f"{answer_part}，状态={recognition.state}，受阻次数={recognition.obstruction_count}，"
        f"策略={[str(item) for item in strategy]}，{care_part}，{visual_part}。依据：{recognition.evidence}"
    )


def _generate_tutor_response(
    state: LearningState,
    strategy: list[TeachingStrategy],
    care_triggered: bool,
    visual_aid_used: VisualAidType,
    question_stem: str | None,
    question_solution: str | None,
    student_input: str,
    is_correct: bool | None,
    error_cause: str | None,
    error_detail: str | None,
) -> str:
    payload = GenerateResponseInput(
        state=state,
        strategy=strategy,
        care_triggered=care_triggered,
        visual_aid_used=visual_aid_used,
        question={"stem": question_stem, "solution": question_solution} if question_stem else None,
        student_input=student_input,
        is_correct=is_correct,
        error_cause=error_cause,
        error_detail=error_detail,
    )
    try:
        return get_llm_client().generate_response(payload).tutor_response
    except LlmError:
        return MockLlmClient().generate_response(payload).tutor_response
