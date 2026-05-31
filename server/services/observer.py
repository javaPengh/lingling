import sqlite3

from server.dao import review_task_dao, session_dao
from server.models.schemas import ObserverSessionResponse
from server.services.memory import read_memory


def get_observer_session(connection: sqlite3.Connection, session_id: str) -> ObserverSessionResponse:
    session = session_dao.get_session(connection, session_id)
    if session is None:
        raise ValueError(f"Session not found: {session_id}")
    memory = read_memory(connection, session.student_id)
    events = session_dao.list_events_by_session(connection, session_id)
    tasks = review_task_dao.list_review_tasks_by_session(connection, session_id)
    return ObserverSessionResponse(
        session_id=session_id,
        student_id=session.student_id,
        memory_summary=memory.history_summary,
        events=events,
        review_tasks=tasks,
    )
