"""学生业务服务。

当前只封装学生选择页需要的列表能力。
"""

import sqlite3

from server.dao.student_dao import list_students
from server.models.schemas import StudentsListResponse


def get_students(connection: sqlite3.Connection) -> StudentsListResponse:
    """返回学生列表响应对象。"""

    return StudentsListResponse(students=list_students(connection))
