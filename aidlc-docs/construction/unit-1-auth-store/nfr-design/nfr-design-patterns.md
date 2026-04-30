# Unit 1: NFR Design Patterns - 인증 + 매장 + 관리자 + 광고

> 이 문서는 전체 시스템의 공통 NFR 패턴을 정의합니다 (Unit 1이 기반 인프라 담당).

---

## 1. 인증/인가 패턴

### 1.1 JWT 미들웨어 패턴
```python
# 패턴: Dependency Injection 기반 인증
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInfo:
    """JWT 토큰에서 사용자 정보 추출"""
    payload = decode_token(token)
    return UserInfo(id=payload["sub"], role=payload["role"], store_id=payload["store_id"])

# 역할 기반 접근 제어 데코레이터 패턴
def require_role(*roles: str):
    def dependency(current_user: UserInfo = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user
    return Depends(dependency)

# 매장 스코프 검증 패턴
def require_store_access(store_id: int, current_user: UserInfo = Depends(get_current_user)):
    if current_user.role != "SUPER_ADMIN" and current_user.store_id != store_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return current_user
```

### 1.2 Rate Limiting 패턴
```python
# slowapi 기반 Rate Limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/15minutes")  # 15분에 5회
async def login(request: Request, credentials: LoginRequest):
    ...
```

---

## 2. 에러 처리 패턴

### 2.1 Global Error Handler 패턴
```python
# 전역 예외 핸들러
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": format_errors(exc.errors())})

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception", exc_info=exc, request_id=request.state.request_id)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
```

### 2.2 Fail-Closed 패턴
- 인증 실패 → 접근 거부 (401/403)
- 검증 실패 → 요청 거부 (422)
- 서버 오류 → 일반 에러 메시지 (500, 스택 트레이스 숨김)
- DB 오류 → 트랜잭션 롤백 + 에러 응답

---

## 3. 로깅 패턴

### 3.1 구조화된 로깅
```python
# structlog 기반 JSON 로깅
import structlog
logger = structlog.get_logger()

# 로그 포맷
{
    "timestamp": "2026-04-30T12:00:00Z",
    "level": "INFO",
    "event": "order_created",
    "request_id": "uuid",
    "user_id": 1,
    "store_id": 1,
    "details": {...}
}
```

### 3.2 민감 데이터 필터링
- 비밀번호, 토큰 값은 절대 로깅하지 않음
- 로그에 `password`, `token`, `secret` 필드 자동 마스킹

---

## 4. 입력 검증 패턴

### 4.1 Pydantic 스키마 기반 검증
```python
class StoreCreate(BaseModel):
    store_code: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-z0-9-]+$")
    name: str = Field(..., min_length=2, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
```

### 4.2 파일 업로드 검증 패턴
```python
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

async def validate_image(file: UploadFile):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(422, "Unsupported file format")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(422, "File too large")
    await file.seek(0)
```

---

## 5. HTTP 보안 헤더 패턴

### 5.1 SecurityHeadersMiddleware
```python
class SecurityHeadersMiddleware:
    async def __call__(self, request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
```

---

## 6. CORS 패턴

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # 명시적 오리진만
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## 7. 데이터베이스 패턴

### 7.1 비동기 세션 관리
```python
# Dependency Injection 기반 DB 세션
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### 7.2 Repository 패턴
```python
class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, model, id: int):
        result = await self.session.get(model, id)
        if not result:
            raise HTTPException(404, "Not found")
        return result
```
