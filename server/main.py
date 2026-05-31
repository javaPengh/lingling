from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.api.routes import health, learning, observer, report, students
from server.core.config import settings
from server.dao.connection import create_connection
from server.dao.student_dao import count_students
from server.scripts.seed import seed_database


def create_app() -> FastAPI:
    app = FastAPI(title="Lingling Teacher API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.web_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router, prefix="/api")
    app.include_router(students.router, prefix="/api")
    app.include_router(learning.router, prefix="/api")
    app.include_router(observer.router, prefix="/api")
    app.include_router(report.router, prefix="/api")

    @app.on_event("startup")
    def bootstrap_database() -> None:
        with create_connection() as connection:
            if count_students(connection) == 0:
                seed_database(connection)

    return app


app = create_app()
