# Performance Test Instructions - Unit 2: 메뉴 관리

## Performance Requirements (NFR)

| ID | 요구사항 | 목표값 |
|---|---|---|
| NFR-PERF-01 | 메뉴 목록 조회 API | 500ms 이내 |
| NFR-PERF-02 | 메뉴 등록/수정 API (이미지 포함) | 1초 이내 |
| NFR-PERF-03 | 고객용 메뉴 조회 API | 300ms 이내 |
| NFR-PERF-04 | 카테고리 CRUD API | 200ms 이내 |

---

## 테스트 도구

```bash
# locust 설치 (Python 부하 테스트 도구)
pip install locust
```

## 부하 테스트 스크립트

`backend/tests/performance/locustfile.py` 생성:

```python
from locust import HttpUser, task, between

class MenuUser(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def get_customer_menus(self):
        """고객용 메뉴 조회 (가장 빈번한 요청)"""
        self.client.get("/api/customer/stores/1/menus")

    @task(2)
    def get_admin_menus(self):
        """관리자 메뉴 목록 조회"""
        self.client.get("/api/stores/1/menus")

    @task(1)
    def get_categories(self):
        """카테고리 목록 조회"""
        self.client.get("/api/stores/1/categories")
```

## 테스트 실행

```bash
# 서버 실행 (별도 터미널)
cd backend
uvicorn backend.app.main:app --port 8000

# 부하 테스트 실행
locust -f backend/tests/performance/locustfile.py --host=http://localhost:8000
# 브라우저에서 http://localhost:8089 접속
# Users: 50, Spawn rate: 5
```

## 성능 기준

| 메트릭 | 목표 | 측정 방법 |
|---|---|---|
| 고객 메뉴 조회 P95 | < 300ms | locust 결과 |
| 관리자 메뉴 조회 P95 | < 500ms | locust 결과 |
| 동시 접속 | 50~100 테이블 | locust Users 설정 |
| 에러율 | < 1% | locust 결과 |

## 최적화 포인트 (성능 미달 시)

1. **N+1 쿼리**: `get_customer_menus()`에서 카테고리별 메뉴 개별 조회 → JOIN 쿼리로 변경
2. **인덱스**: `(store_id, category_id, display_order)` 복합 인덱스 확인
3. **캐싱**: 고객 메뉴 조회 결과 캐싱 (메뉴 변경 시 무효화)
4. **이미지**: 이미지 서빙을 Nginx static file로 분리
