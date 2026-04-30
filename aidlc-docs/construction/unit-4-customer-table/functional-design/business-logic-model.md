# Unit 4: 비즈니스 로직 모델 - 고객 UI + 테이블 관리

---

## 1. 테이블 등록/설정 플로우
```
입력: store_id, { table_number, password }
    |
    v
[권한 확인] -- STORE_ADMIN, 해당 매장
    |
    v
[table_number 중복 확인] -- 중복 --> 409 Conflict
    |
    v
[비밀번호 해싱] (bcrypt)
    |
    v
[DB 저장]
    |
    v
출력: TableInfo 객체
```

## 2. 이용 완료 플로우
```
입력: table_id
    |
    v
[권한 확인] -- STORE_ADMIN
    |
    v
[현재 활성 세션 확인] -- 없음 --> 404 (활성 세션 없음)
    |
    v
[OrderService.move_to_history(session_id)] (Unit 3)
    |
    v
[세션 종료] (is_active=false, ended_at=now)
    |
    v
[SSE 이벤트 발행] → 관리자 (table_completed)
    |
    v
출력: { message: "이용 완료 처리됨" }
```

## 3. 세션 시작 플로우 (주문 생성 시 자동)
```
입력: table_id
    |
    v
[현재 활성 세션 확인]
    |-- 있음 --> 기존 세션 반환
    |-- 없음 --> 새 세션 생성
    v
[새 세션 생성] (table_id, store_id, started_at=now, is_active=true)
    |
    v
출력: TableSession 객체
```

## 4. 광고 화면 플로우 (Frontend)
```
[페이지 로드]
    |
    v
[API: 활성 광고 목록 조회]
    |-- 광고 있음 --> 슬라이드 시작 (5초 간격)
    |-- 광고 없음 --> 기본 이미지 또는 메뉴 화면 직행
    v
[사용자 터치 감지]
    |
    v
[메뉴 화면으로 라우팅]

[비활성 타이머] (2분)
    |
    v
[메뉴 화면 → 광고 화면 자동 복귀]
```

## 5. 장바구니 플로우 (Frontend, 서버 통신 없음)
```
[메뉴 추가]
    |
    v
[localStorage에서 장바구니 로드]
    |
    v
[동일 메뉴 존재?]
    |-- 있음 --> quantity + 1
    |-- 없음 --> 새 항목 추가
    v
[총 금액 재계산]
    |
    v
[localStorage에 저장]

[수량 변경]
    |
    v
[quantity 업데이트]
    |-- quantity == 0 --> 항목 제거
    v
[총 금액 재계산 + localStorage 저장]
```

## 6. 사다리 타기 플로우 (Frontend, 서버 통신 없음)
```
[인원 수 선택] (2~10명)
    |
    v
[사다리 생성]
    |-- 세로줄: 인원 수만큼
    |-- 가로줄: 각 구간에 랜덤 0~2개
    |-- 꽝 위치: 랜덤 1개
    v
["시작" 버튼 클릭]
    |
    v
[각 참가자 경로 계산]
    |
    v
[이동 애니메이션 실행] (위→아래, 가로줄 만나면 이동)
    |
    v
[꽝 결정 + 결과 강조 연출]
    |-- 색상 변경 (빨간색)
    |-- 크기 확대 애니메이션
    |-- 효과음 재생
    v
[5초 대기]
    |
    v
[결제 방식 선택 팝업으로 복귀]
```
