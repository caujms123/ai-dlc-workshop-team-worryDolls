# Unit 2: NFR Design Patterns - 메뉴 관리

---

## 1. 이미지 관리 패턴

### 1.1 메뉴 이미지 업로드 (Unit 1 FileUploadService 활용)
```python
async def create_menu(self, store_id, menu_data, image, db):
    # 이미지 업로드 (있으면)
    image_path = None
    if image:
        image_path = await file_upload_service.upload_image(image, f"menus/{store_id}")
    
    menu = Menu(store_id=store_id, image_path=image_path, ...)
    db.add(menu)
    return menu
```

### 1.2 이미지 교체 패턴
```python
async def update_menu(self, menu_id, menu_data, new_image, db):
    menu = await self.get_menu(menu_id, db)
    if new_image:
        # 기존 이미지 삭제
        if menu.image_path:
            await file_upload_service.delete_image(menu.image_path)
        # 새 이미지 업로드
        menu.image_path = await file_upload_service.upload_image(new_image, f"menus/{menu.store_id}")
    # 나머지 필드 업데이트
    ...
```

---

## 2. 순서 관리 패턴

### 2.1 Display Order 재정렬
```python
async def reorder_items(self, items: list, db: AsyncSession):
    """삭제 후 남은 항목들의 display_order를 0부터 재정렬"""
    for i, item in enumerate(sorted(items, key=lambda x: x.display_order)):
        item.display_order = i
    await db.flush()
```

---

## 3. 고객용 메뉴 조회 패턴

### 3.1 카테고리별 그룹화 응답
```python
async def get_customer_menus(self, store_id: int, db) -> list[CategoryWithMenus]:
    categories = await self.category_repo.get_by_store(store_id, db)
    result = []
    for cat in categories:
        menus = await self.menu_repo.get_available_by_category(cat.id, db)
        result.append(CategoryWithMenus(category=cat, menus=menus))
    return result
```
