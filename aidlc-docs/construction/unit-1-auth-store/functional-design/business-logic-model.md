# Unit 1: 비즈니스 로직 모델 - 인증 + 매장 + 관리자 + 광고

---

## 1. 인증 플로우

### 1.1 관리자 로그인 플로우
```
입력: store_code (매장 관리자만), username, password
    |
    v
[로그인 시도 제한 확인] -- 잠금 상태 --> 429 Too Many Requests
    |
    v (허용)
[매장 조회] -- 매장 없음/비활성 --> 401 Unauthorized
    |
    v (매장 확인)
[관리자 조회] -- 관리자 없음/비활성 --> 401 Unauthorized
    |
    v (관리자 확인)
[비밀번호 검증] -- 불일치 --> 실패 횟수 증가 --> 401 Unauthorized
    |
    v (일치)
[실패 횟수 리셋]
    |
    v
[JWT 토큰 생성] (sub, role, store_id, exp)
    |
    v
출력: { access_token, token_type, expires_in, role, store_id }
```

### 1.2 테이블 로그인 플로우
```
입력: store_code, table_number, password
    |
    v
[매장 조회] -- 매장 없음/비활성 --> 401
    |
    v
[테이블 조회] -- 테이블 없음 --> 401
    |
    v
[비밀번호 검증] -- 불일치 --> 401
    |
    v
[JWT 토큰 생성] (sub: table_id, role: TABLE, store_id, exp: 16h)
    |
    v
출력: { access_token, token_type, expires_in, store_id, table_id }
```

### 1.3 토큰 검증 플로우
```
입력: Authorization: Bearer {token}
    |
    v
[JWT 디코딩] -- 유효하지 않음 --> 401
    |
    v
[만료 확인] -- 만료됨 --> 401
    |
    v
[사용자 정보 추출] (sub, role, store_id)
    |
    v
[요청 컨텍스트에 주입]
    |
    v
출력: UserInfo { id, role, store_id }
```

---

## 2. 매장 관리 플로우

### 2.1 매장 등록
```
입력: { store_code, name, address?, phone? }
    |
    v
[필수 필드 검증] -- 누락 --> 422 Validation Error
    |
    v
[store_code 형식 검증] -- 부적합 --> 422
    |
    v
[store_code 고유성 확인] -- 중복 --> 409 Conflict
    |
    v
[DB 저장]
    |
    v
출력: Store 객체
```

### 2.2 매장 수정
```
입력: store_id, { name?, address?, phone? }
    |
    v
[매장 존재 확인] -- 없음 --> 404
    |
    v
[필수 필드 검증]
    |
    v
[DB 업데이트]
    |
    v
출력: 수정된 Store 객체
```

---

## 3. 관리자 계정 관리 플로우

### 3.1 관리자 생성
```
입력: store_id, { username, password, role }
    |
    v
[매장 존재 확인] -- 없음 --> 404
    |
    v
[username 중복 확인] -- 중복 --> 409 Conflict
    |
    v
[비밀번호 해싱] (bcrypt, cost=12)
    |
    v
[DB 저장]
    |
    v
출력: Admin 객체 (password_hash 제외)
```

---

## 4. 광고 관리 플로우

### 4.1 광고 이미지 업로드
```
입력: store_id, image_file
    |
    v
[매장 존재 확인] -- 없음 --> 404
    |
    v
[이미지 검증] -- 형식/크기 부적합 --> 422
    |
    v
[UUID 파일명 생성]
    |
    v
[파일 저장] (uploads/advertisements/{store_id}/{uuid}.ext)
    |
    v
[DB 저장] (store_id, image_path, display_order=마지막+1)
    |
    v
출력: Advertisement 객체
```

### 4.2 광고 삭제
```
입력: ad_id
    |
    v
[광고 존재 확인] -- 없음 --> 404
    |
    v
[물리적 파일 삭제]
    |
    v
[DB 삭제]
    |
    v
[나머지 광고 display_order 재정렬]
    |
    v
출력: 204 No Content
```

---

## 5. 미들웨어 로직

### 5.1 AuthMiddleware
```
요청 수신
    |
    v
[공개 엔드포인트 확인] -- 공개 --> 통과
    |
    v (인증 필요)
[Authorization 헤더 확인] -- 없음 --> 401
    |
    v
[Bearer 토큰 추출] -- 형식 오류 --> 401
    |
    v
[토큰 검증] -- 실패 --> 401
    |
    v
[사용자 정보를 request.state에 주입]
    |
    v
다음 핸들러로 전달
```

### 5.2 RBAC 데코레이터
```
@require_role(SUPER_ADMIN)
    |
    v
[request.state.user.role 확인]
    |
    v
[역할 일치] -- 불일치 --> 403 Forbidden
    |
    v
핸들러 실행
```

### 5.3 Store Scope 검증
```
@require_store_access
    |
    v
[SUPER_ADMIN] --> 모든 매장 접근 허용
    |
    v
[STORE_ADMIN] --> request의 store_id == user.store_id 확인
    |
    v
[불일치] --> 403 Forbidden
```

### 5.4 GlobalErrorHandler
```
예외 발생
    |
    v
[HTTPException] --> { status_code, detail } 반환
    |
    v
[ValidationError] --> 422 { detail: 검증 오류 목록 }
    |
    v
[기타 예외] --> 500 { detail: "Internal Server Error" }
    |              (스택 트레이스는 로그에만 기록)
    v
에러 로깅 (timestamp, request_id, error_type, message)
```
