from dataclasses import dataclass
from collections import Counter
import sqlite3

from server.dao import session_dao, student_dao
from server.models.entities import LearningEvent, LearningSession, StudentKnowledge, StudentProfile


@dataclass(frozen=True)
class MemorySnapshot:
    profile: StudentProfile | None
    weak_knowledge: list[StudentKnowledge]
    recent_sessions: list[LearningSession]
    recent_events: list[LearningEvent]
    history_summary: str


def read_memory(connection: sqlite3.Connection, student_id: str) -> MemorySnapshot:
    profile = student_dao.get_student_profile(connection, student_id)
    weak_knowledge = student_dao.list_weak_student_knowledge(connection, student_id)
    recent_sessions = session_dao.list_recent_sessions_by_student(connection, student_id, limit=2)
    recent_events = session_dao.list_recent_events_by_student(connection, student_id, limit=3)
    parts: list[str] = []
    if profile:
        parts.append(profile.learning_summary or "")
        if profile.weak_points:
            parts.append(f"薄弱点={profile.weak_points}")
        if profile.recent_states:
            parts.append(f"近期状态={profile.recent_states}")
        if profile.effective_strategies:
            parts.append(f"有效策略={profile.effective_strategies}")
    if weak_knowledge:
        weak_ids = [record.knowledge_point_id for record in weak_knowledge]
        parts.append(f"掌握度低于60的知识点={weak_ids}")
    history_summary = "；".join(part for part in parts if part) or "暂无长期记忆"
    return MemorySnapshot(profile, weak_knowledge, recent_sessions, recent_events, history_summary)


def build_opening_message(snapshot: MemorySnapshot, student_name: str) -> str:
    if snapshot.profile and "焦虑" in (snapshot.profile.learning_summary or ""):
        return f"{student_name}来啦。我们今天先稳稳做一道题，不追速度，只抓住当前这一步。"
    if snapshot.profile and "平稳" in (snapshot.profile.learning_summary or ""):
        return f"{student_name}今天状态不错，来一道稍微绕一点的题，看看能不能一次抓住关键。"
    return f"{student_name}来啦~ 今天我们挑一道二次函数的题练练手。别急，咱们一步步来。"


def summarize_session(events: list[LearningEvent]) -> tuple[str, str | None]:
    if not events:
        return "本次会话暂无学习事件。", None
    state_counts = Counter(event.state for event in events)
    dominant_state = state_counts.most_common(1)[0][0]
    wrong_events = [event for event in events if event.is_correct is False]
    care_count = sum(1 for event in events if event.care_triggered)
    kps = sorted({kp for event in events for kp in event.knowledge_point_ids})
    summary = (
        f"本次共完成 {len(events)} 轮互动，主要状态为 {dominant_state}，"
        f"涉及知识点 {kps or ['未绑定题目']}，错题/受阻 {len(wrong_events)} 次，"
        f"主动关怀 {care_count} 次。"
    )
    return summary, dominant_state


def write_back_memory(
    connection: sqlite3.Connection,
    student_id: str,
    events: list[LearningEvent],
    ended_at: str,
) -> StudentProfile | None:
    profile = student_dao.get_student_profile(connection, student_id)
    if profile is None:
        return None

    touched_kps = sorted({kp for event in events for kp in event.knowledge_point_ids})
    for kp_id in touched_kps:
        record = student_dao.get_student_knowledge(connection, student_id, kp_id)
        if record is None:
            record = StudentKnowledge(
                id=f"sk_{student_id[-3:]}_{kp_id[-3:]}",
                student_id=student_id,
                knowledge_point_id=kp_id,
                mastery=50,
                attempts=0,
                correct_count=0,
                last_practiced_at=None,
            )
        for event in events:
            if kp_id not in event.knowledge_point_ids or event.is_correct is None:
                continue
            record.attempts += 1
            if event.is_correct:
                record.correct_count += 1
                record.mastery = min(100, record.mastery + 1)
            else:
                record.mastery = max(0, record.mastery - 2)
            record.last_practiced_at = ended_at
        student_dao.upsert_student_knowledge(connection, record)

    all_knowledge = student_dao.list_student_knowledge(connection, student_id)
    weak_points = [record.knowledge_point_id for record in all_knowledge if record.mastery < 60]
    _summary, dominant_state = summarize_session(events)
    recent_states = [*profile.recent_states, dominant_state] if dominant_state else [*profile.recent_states]
    recent_states = recent_states[-5:]
    effective = list(dict.fromkeys([*profile.effective_strategies, *_effective_strategies_from_events(events)]))
    profile.weak_points = weak_points
    profile.recent_states = recent_states
    profile.effective_strategies = effective
    profile.total_sessions += 1
    profile.updated_at = ended_at
    profile.learning_summary = _merge_learning_summary(profile.learning_summary, events)
    student_dao.update_student_profile(connection, profile)
    return profile


def _effective_strategies_from_events(events: list[LearningEvent]) -> list[str]:
    result: list[str] = []
    for event in events:
        if event.care_triggered or event.is_correct:
            result.extend(event.strategy)
    return result


def _merge_learning_summary(old_summary: str | None, events: list[LearningEvent]) -> str:
    if not events:
        return old_summary or ""
    has_frustration = any(event.state == "frustrated" for event in events)
    has_small_step = any("small_step" in event.strategy for event in events)
    note = "本次学习显示含参讨论仍需拆步引导。" if has_frustration and has_small_step else "本次学习继续沉淀了结构化练习记录。"
    base = old_summary or ""
    return f"{base} {note}".strip()
