import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from server.api.deps import get_db
from server.models.schemas import ReportResponse
from server.services.reporting import get_student_report


router = APIRouter(prefix="/report", tags=["report"])


@router.get("/students/{student_id}", response_model=ReportResponse)
def report_endpoint(student_id: str, db: sqlite3.Connection = Depends(get_db)) -> ReportResponse:
    try:
        return get_student_report(db, student_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
