# Unit 2: 비즈니스 로직 모델 - 메뉴 관리

---

## 1. 메뉴 등록 플로우
```
입력: store_id, { name, price, description?, category_id, image? }
    |
    v
[권한 확인] -- STORE_ADMIN, 해당 매장 --> 403 if 불일치
    |
    v
[필수 필드 검증] -- 누락/부적합 --> 422
    |
    v
[카테고리 존재 확인] -- 없음/다른 매장 --> 404
    |
    v
[가격 검증] -- 0 미만 또는 10,000,000 초과 --> 422
    |
    v
[이미지 업로드] (있으면) -- FileUploadService
    |
    v
[display_order 자동 할당] (해당 카테고리 내 마지막+1)
    |
    v
[DB 저장]
    |
    v
출력: Menu 객체
```

## 2. 메뉴 수정 플로우
```
입력: menu_id, { name?, price?, description?, category_id?, image? }
    |
    v
[메뉴 존재 확인] -- 없음 --> 404
    |
    v
[권한 확인] -- 해당 매장 소속 --> 403
    |
    v
[필드 검증]
    |
    v
[새 이미지 있으면] --> 기존 이미지 삭제 + 새 이미지 업로드
    |
    v
[DB 업데이트]
    |
    v
출력: 수정된 Menu 객체
```

## 3. 메뉴 삭제 플로우
```
입력: menu_id
    |
    v
[메뉴 존재 확인] -- 없음 --> 404
    |
    v
[권한 확인]
    |
    v
[이미지 파일 삭제] (있으면)
    |
    v
[DB 삭제]
    |
    v
[해당 카테고리 내 display_order 재정렬]
    |
    v
출력: 204 No Content
```

## 4. 고객용 메뉴 조회 플로우
```
입력: store_id
    |
    v
[카테고리 목록 조회] (display_order 순)
    |
    v
[각 카테고리별 메뉴 조회] (is_available=true, display_order 순)
    |
    v
출력: [ { category: {...}, menus: [...] }, ... ]
```
