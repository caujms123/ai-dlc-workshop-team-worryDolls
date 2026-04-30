# Unit 4: Tech Stack Decisions - 고객 UI + 테이블 관리

> Unit 1에서 정의한 공통 Tech Stack을 그대로 사용합니다.
> Unit 4 특화 추가 사항만 기술합니다.

## Frontend (Customer) 추가 사항

| 영역 | 기술 | 선택 이유 |
|---|---|---|
| **사다리 타기 렌더링** | HTML5 Canvas 또는 SVG | 부드러운 애니메이션, 60fps |
| **애니메이션** | requestAnimationFrame + CSS | 사다리 이동 애니메이션 |
| **효과음** | Web Audio API 또는 HTML5 Audio | 사다리 타기 효과음 |
| **슬라이드** | CSS transition + setInterval | 광고 자동 슬라이드 |
| **로컬 저장** | localStorage API | 장바구니, 인증 토큰 저장 |
| **비활성 감지** | 이벤트 리스너 (touch, click, scroll) | 2분 비활성 타이머 |

## Backend 추가 사항
- Unit 1의 AuthService 활용 (테이블 로그인)
- TableInfo, TableSession 모델은 SQLAlchemy로 정의
