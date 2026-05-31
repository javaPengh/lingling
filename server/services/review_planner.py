"""复习任务规划服务。

根据本次会话中的薄弱点、连续受阻和挫败事件生成主动复习任务。
"""

from datetime import datetime, timedelta, timezone
import sqlite3

from server.core.enums import ReviewStatus
from server.dao import review_task_dao, student_dao
from server.models.entities import LearningEvent, ReviewTask


def create_review_tasks(
    connection: sqlite3.Connection,
    student_id: str,
    session_id: str,
    events: list[LearningEvent],
    created_at: str,
) -> list[ReviewTask]:
    """为会话中暴露的薄弱知识点创建复习任务。"""

    candidates = _candidate_knowledge_points(connection, student_id, events)
    if not candidates:
        return []
    source_event = _source_event(events)
    tasks: list[ReviewTask] = []
    for kp_id in candidates[:2]:
        task = ReviewTask(
            id=f"review_{session_id}_{kp_id}",
            student_id=student_id,
            knowledge_point_id=kp_id,
            source_event_id=source_event.id if source_event else None,
            reason=_reason(kp_id, events),
            recommended_question_id=_recommended_question(kp_id),
            status=ReviewStatus.PENDING,
            due_date=_due_date(created_at),
            created_at=created_at,
        )
        review_task_dao.upsert_review_task(connection, task)
        tasks.append(task)
    return tasks


def _candidate_knowledge_points(
    connection: sqlite3.Connection, student_id: str, events: list[LearningEvent]
) -> list[str]:
    touched = sorted({kp for event in events for kp in event.knowledge_point_ids})
    weak = {record.knowledge_point_id for record in student_dao.list_weak_student_knowledge(connection, student_id)}
    frustrated = {kp for event in events if event.state == "frustrated" for kp in event.knowledge_point_ids}
    ordered = [kp for kp in ["kp_004", "kp_003", "kp_008", "kp_009"] if kp in touched and (kp in weak or kp in frustrated)]
    ordered.extend(kp for kp in touched if kp in weak and kp not in ordered)
    return ordered


def _source_event(events: list[LearningEvent]) -> LearningEvent | None:
    for event in reversed(events):
        if event.state == "frustrated" or event.care_triggered or event.is_correct is False:
            return event
    return events[-1] if events else None


def _reason(kp_id: str, events: list[LearningEvent]) -> str:
    obstruction_count = sum(1 for event in events if kp_id in event.knowledge_point_ids and event.is_correct is not True)
    if kp_id == "kp_004":
        return f"含参二次函数最值连续受阻 {obstruction_count} 次、出现放弃倾向，需专项练分类讨论"
    return f"本次学习中知识点 {kp_id} 出现受阻 {obstruction_count} 次，需安排主动复习"


def _recommended_question(kp_id: str) -> str | None:
    return {
        "kp_004": "q_005",
        "kp_003": "q_005",
        "kp_008": "q_006",
        "kp_009": "q_007",
        "kp_006": "q_004",
    }.get(kp_id, "q_002")


def _due_date(created_at: str) -> str:
    base = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    return (base + timedelta(days=2)).date().isoformat()
