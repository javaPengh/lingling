import sqlite3

from fastapi import APIRouter, Depends

from server.api.deps import get_db
from server.models.schemas import StudentsListResponse
from server.services.students import get_students


router = APIRouter(tags=["students"])


@router.get("/students", response_model=StudentsListResponse)
def list_students_endpoint(db: sqlite3.Connection = Depends(get_db)) -> StudentsListResponse:
    return get_students(db)
