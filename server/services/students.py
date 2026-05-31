import sqlite3

from server.dao.student_dao import list_students
from server.models.schemas import StudentsListResponse


def get_students(connection: sqlite3.Connection) -> StudentsListResponse:
    return StudentsListResponse(students=list_students(connection))
