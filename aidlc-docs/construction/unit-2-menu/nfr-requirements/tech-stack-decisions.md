# Unit 2: Tech Stack Decisions - 메뉴 관리

> Unit 1에서 정의한 공통 Tech Stack을 그대로 사용합니다.
> Unit 2 특화 추가 사항만 기술합니다.

## Backend 추가 사항
- Unit 1의 FileUploadService 활용 (메뉴 이미지 업로드)
- Category, Menu 모델은 SQLAlchemy로 정의

## Frontend (Customer) 추가 사항

| 영역 | 기술 | 선택 이유 |
|---|---|---|
| **이미지 Lazy Loading** | Vue 내장 또는 vue-lazyload | 메뉴 이미지 성능 최적화 |
| **스크롤 관리** | 네이티브 scrollIntoView | 카테고리 빠른 이동 |
