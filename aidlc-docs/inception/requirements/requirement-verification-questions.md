# 테이블오더 서비스 - 요구사항 명확화 질문

아래 질문들에 대해 각 [Answer]: 태그 뒤에 선택지 문자를 입력해 주세요.
제공된 선택지가 맞지 않으면 X)를 선택하고 설명을 추가해 주세요.

---

## Question 1
프로젝트의 기술 스택(프로그래밍 언어 및 프레임워크)은 어떤 것을 사용하시겠습니까?

A) TypeScript + React (Frontend) / TypeScript + NestJS (Backend) / PostgreSQL (DB)
B) TypeScript + React (Frontend) / TypeScript + Express.js (Backend) / PostgreSQL (DB)
C) TypeScript + Next.js (Full-stack) / PostgreSQL (DB)
D) JavaScript + React (Frontend) / Java + Spring Boot (Backend) / MySQL (DB)
X) Other (please describe after [Answer]: tag below)

[Answer]: X - JavaScript + Vue (Frontend) / Java + Spring Boot (Backend) / MySQL (DB)

---

## Question 2
배포 환경은 어떤 것을 계획하고 계십니까?

A) 클라우드 (AWS)
B) 클라우드 (Azure, GCP 등)
C) 로컬/온프레미스 서버
D) Docker 컨테이너 기반 (배포 환경 미정)
X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Question 3
매장(Store) 관리 범위는 어떻게 되나요? (멀티 테넌시 관련)

A) 단일 매장만 지원 (하나의 매장에서만 사용)
B) 다중 매장 지원 (여러 매장이 각각 독립적으로 사용, 매장별 데이터 격리)
C) 다중 매장 + 중앙 관리 (본사에서 여러 매장을 통합 관리)
X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Question 4
메뉴 이미지 관리 방식은 어떻게 하시겠습니까?

A) 외부 이미지 URL 직접 입력 (이미지 호스팅은 별도 관리)
B) 서버에 이미지 파일 업로드 기능 포함
C) 클라우드 스토리지(S3 등)에 업로드 후 URL 저장
D) MVP에서는 이미지 URL 직접 입력, 추후 업로드 기능 추가
X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question 5
동시 접속 사용자 규모(예상 트래픽)는 어느 정도입니까?

A) 소규모 (1개 매장, 동시 10~20 테이블)
B) 중규모 (5~10개 매장, 동시 50~100 테이블)
C) 대규모 (10개 이상 매장, 동시 100+ 테이블)
D) MVP 단계에서는 소규모, 추후 확장 고려
X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question 6
관리자 계정 관리 방식은 어떻게 하시겠습니까?

A) 매장당 1개의 관리자 계정 (고정, DB에 직접 등록)
B) 매장당 다수의 관리자 계정 (관리자 등록/관리 기능 포함)
C) 슈퍼 관리자 + 매장별 관리자 계층 구조
D) MVP에서는 매장당 1개 고정 계정, 추후 확장
X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Question 7
테이블 태블릿의 세션 만료 정책은 어떻게 하시겠습니까? (요구사항에 관리자는 16시간으로 명시되어 있으나, 테이블 태블릿 세션 기간은 미정)

A) 테이블 태블릿도 16시간 세션 (관리자와 동일)
B) 테이블 태블릿은 24시간 세션
C) 테이블 태블릿은 세션 만료 없음 (영구 로그인, 관리자가 수동 리셋)
D) 매장 영업시간 기반 자동 만료
X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 8
메뉴 관리 기능이 요구사항에 포함되어 있는데, MVP 범위에는 명시되지 않았습니다. 메뉴 관리를 MVP에 포함하시겠습니까?

A) 예, 메뉴 CRUD(등록/수정/삭제/조회) 전체를 MVP에 포함
B) 예, 기본적인 메뉴 등록/수정만 MVP에 포함 (삭제, 순서 조정은 제외)
C) 아니오, MVP에서는 DB에 직접 메뉴 데이터를 넣고, 관리 UI는 추후 개발
X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 9
주문 상태 실시간 업데이트(고객 화면)에 대해 요구사항에 "선택사항"으로 표시되어 있습니다. MVP에 포함하시겠습니까?

A) 예, 고객 화면에서도 SSE로 주문 상태 실시간 업데이트 포함
B) 아니오, 고객은 페이지 새로고침으로 상태 확인 (관리자만 SSE 사용)
C) 고객 화면은 주기적 폴링(예: 30초마다)으로 구현
X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 10
Security Extension 규칙을 이 프로젝트에 적용하시겠습니까?

A) 예 — 모든 SECURITY 규칙을 blocking constraint로 적용 (프로덕션 수준 애플리케이션에 권장)
B) 아니오 — SECURITY 규칙 건너뛰기 (PoC, 프로토타입, 실험적 프로젝트에 적합)
X) Other (please describe after [Answer]: tag below)

[Answer]: x- 모르겠습니다. 지금 규모에 맞게 알아서 해주세요.

---
