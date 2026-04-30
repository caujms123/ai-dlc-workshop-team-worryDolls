# Unit 1: Logical Components - 인증 + 매장 + 관리자 + 광고

---

## 1. 미들웨어 스택 (요청 처리 순서)

```
Request
  |
  v
[1. SecurityHeadersMiddleware] → HTTP 보안 헤더 추가
  |
  v
[2. CORSMiddleware] → CORS 정책 적용
  |
  v
[3. RequestIdMiddleware] → 요청 ID 생성 (로깅용)
  |
  v
[4. LoggingMiddleware] → 요청/응답 로깅
  |
  v
[5. RateLimitMiddleware] → Rate Limiting (로그인 엔드포인트)
  |
  v
[6. AuthMiddleware] → JWT 검증 + 사용자 정보 주입
  |
  v
[Router → Service → Repository → DB]
  |
  v
[GlobalErrorHandler] → 예외 처리 (모든 레이어)
  |
  v
Response
```

---

## 2. 인증 컴포넌트 구조

```
+---------------------------+
| AuthRouter                |
| POST /auth/admin/login    |
| POST /auth/table/login    |
| POST /auth/logout         |
| GET  /auth/me             |
+---------------------------+
            |
            v
+---------------------------+
| AuthService               |
| - login_admin()           |
| - login_table()           |
| - verify_token()          |
| - check_login_attempts()  |
+---------------------------+
     |              |
     v              v
+-----------+  +-----------+
| JWTUtil   |  | PassUtil  |
| - encode  |  | - hash    |
| - decode  |  | - verify  |
+-----------+  +-----------+
     |
     v
+---------------------------+
| LoginAttemptRepository    |
| AdminRepository           |
| TableRepository           |
+---------------------------+
```

---

## 3. 파일 업로드 컴포넌트 구조

```
+---------------------------+
| FileUploadService         |
| - upload_image()          |
| - delete_image()          |
| - validate_image()        |
+---------------------------+
            |
            v
+---------------------------+
| Local File System         |
| uploads/                  |
|   advertisements/{sid}/   |
|   menus/{sid}/            |
+---------------------------+
```

---

## 4. 설정 관리 구조

```
+---------------------------+
| config.py (Settings)      |
| - DATABASE_URL            |
| - JWT_SECRET_KEY          |
| - JWT_ALGORITHM           |
| - JWT_EXPIRE_HOURS        |
| - UPLOAD_DIR              |
| - MAX_UPLOAD_SIZE         |
| - CORS_ORIGINS            |
| - LOG_LEVEL               |
+---------------------------+
            |
            v
+---------------------------+
| .env (환경 변수 파일)     |
| (gitignore에 포함)        |
+---------------------------+
```

---

## 5. 프로젝트 초기화 구조

```
main.py
  |
  +-- create_app()
       |
       +-- 미들웨어 등록 (순서대로)
       +-- 라우터 등록 (auth, store, admin, ad, category, menu, order, table, sse)
       +-- 이벤트 핸들러 (startup: DB 연결, shutdown: DB 종료)
       +-- 정적 파일 서빙 (uploads/)
       +-- GlobalErrorHandler 등록
```
