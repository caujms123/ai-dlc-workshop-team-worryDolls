# Unit 2: API Documentation - 메뉴 관리

> FastAPI 자동 문서: `http://localhost:8000/docs` (Swagger UI)

---

## Category API

### POST /api/stores/{store_id}/categories
카테고리 등록

**Request Body** (JSON):
```json
{ "name": "메인 메뉴" }
```

**Response** (201):
```json
{
  "id": 1,
  "store_id": 1,
  "name": "메인 메뉴",
  "display_order": 0,
  "created_at": "2026-04-30T09:00:00"
}
```

### GET /api/stores/{store_id}/categories
카테고리 목록 조회

**Response** (200):
```json
{
  "categories": [...],
  "total": 3
}
```

### PUT /api/categories/{category_id}
카테고리 수정

### DELETE /api/categories/{category_id}
카테고리 삭제 (메뉴 존재 시 409)

---

## Menu API (Admin)

### POST /api/stores/{store_id}/menus
메뉴 등록 (multipart/form-data)

**Form Fields**: name, price, category_id, description?, image?

### GET /api/stores/{store_id}/menus?category_id={id}
메뉴 목록 조회

### GET /api/menus/{menu_id}
메뉴 상세 조회

### PUT /api/menus/{menu_id}
메뉴 수정 (multipart/form-data)

### DELETE /api/menus/{menu_id}
메뉴 삭제

### PUT /api/menus/{menu_id}/order
노출 순서 변경

**Request Body** (JSON):
```json
{ "display_order": 0 }
```

---

## Menu API (Customer)

### GET /api/customer/stores/{store_id}/menus
고객용 메뉴 조회 (카테고리별 그룹화)

**Response** (200):
```json
{
  "data": [
    {
      "category": { "id": 1, "name": "메인 메뉴", ... },
      "menus": [
        { "id": 1, "name": "김치찌개", "price": 9000, "description": "...", "image_path": "..." },
        ...
      ]
    }
  ]
}
```
