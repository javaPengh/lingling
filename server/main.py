"""FastAPI 应用入口。

负责创建 app、配置 CORS、挂载 API 路由，并在启动时初始化数据库与种子数据。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.api.routes import health, learning, observer, report, students
from server.core.config import settings
from server.dao.connection import create_connection
from server.dao.student_dao import count_students
from server.scripts.seed import seed_database


def create_app() -> FastAPI:
    """构造并配置灵灵后端 FastAPI 应用。"""

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
        """启动时建表；若库为空则写入演示种子数据。"""

        with create_connection() as connection:
            if count_students(connection) == 0:
                seed_database(connection)

    return app


app = create_app()
