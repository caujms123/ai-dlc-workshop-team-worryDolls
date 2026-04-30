"""FastAPI 애플리케이션 진입점."""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database import close_db, init_db
from app.middleware.error_handler import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.routers import auth, store, admin, advertisement, table

# structlog 설정
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        structlog.get_level_from_name(settings.LOG_LEVEL)
    ),
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리."""
    await init_db()
    yield
    await close_db()


def create_app() -> FastAPI:
    """FastAPI 앱 팩토리."""
    app = FastAPI(
        title="테이블오더 서비스 API",
        description="테이블오더 서비스 Backend API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # 미들웨어 등록
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # 예외 핸들러 등록
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # 라우터 등록
    app.include_router(auth.router)
    app.include_router(store.router)
    app.include_router(admin.router)
    app.include_router(advertisement.router)
    app.include_router(table.router)

    # 정적 파일 서빙
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

    return app


app = create_app()


@app.get("/health")
async def health_check():
    return {"status": "ok"}
