"""报告预览业务服务。

聚合学生画像、薄弱点、近期事件和复习任务，生成教师/家长视角摘要。
"""

import sqlite3

from server.dao import review_task_dao, session_dao, student_dao
from server.models.schemas import ReportResponse


def get_student_report(connection: sqlite3.Connection, student_id: str) -> ReportResponse:
    """按学生 ID 组装报告预览数据。"""

    student = student_dao.get_student(connection, student_id)
    if student is None:
        raise ValueError(f"Student not found: {student_id}")
    profile = student_dao.get_student_profile(connection, student_id)
    weak_points = student_dao.list_weak_student_knowledge(connection, student_id)
    review_tasks = review_task_dao.list_review_tasks_by_student(connection, student_id)
    recent_events = session_dao.list_recent_events_by_student(connection, student_id, limit=8)
    weak_ids = [record.knowledge_point_id for record in weak_points]
    teacher_summary = (
        f"{student.name}当前薄弱点为 {weak_ids or ['暂无明显薄弱点']}；"
        f"最近结构化学习事件 {len(recent_events)} 条，待复习任务 {len(review_tasks)} 条。"
    )
    parent_summary = (
        f"{student.name}最近在数学练习中持续沉淀学习记录。"
        f"若出现受挫，建议多肯定坚持过程，再配合复习计划推进。"
    )
    return ReportResponse(
        student_id=student_id,
        student_name=student.name,
        teacher_summary=teacher_summary,
        parent_summary=parent_summary,
        weak_points=weak_points,
        review_tasks=review_tasks,
        recent_events=recent_events,
        profile=profile,
    )
