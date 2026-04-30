"""FastAPI 앱 진입점 (Unit 4 - 테이블 라우터 등록)"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import table as table_router

app = FastAPI(
    title="테이블오더 서비스",
    description="테이블오더 MVP API",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# 라우터 등록
# Unit 1: auth, store, admin, advertisement 라우터 (추후 통합)
# Unit 2: category, menu 라우터 (추후 통합)
# Unit 3: order, sse 라우터 (추후 통합)
app.include_router(table_router.router)  # Unit 4

# 정적 파일 서빙 (업로드 이미지)
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "ok"}
