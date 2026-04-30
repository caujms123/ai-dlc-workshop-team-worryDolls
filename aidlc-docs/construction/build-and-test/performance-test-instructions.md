# Performance Test Instructions - Unit 3 (주문 + SSE)

## 목적

NFR Requirements에 정의된 성능 목표를 검증합니다.

## 성능 목표

| ID | 항목 | 목표값 |
|---|---|---|
| NFR-PERF-01 | 주문 생성 API 응답 시간 | 1초 이내 |
| NFR-PERF-02 | SSE 이벤트 전달 지연 | 2초 이내 |
| NFR-PERF-03 | 주문 목록 조회 API 응답 시간 | 500ms 이내 |
| NFR-PERF-04 | 주문 상태 변경 API 응답 시간 | 300ms 이내 |
| NFR-PERF-05 | 과거 주문 이력 조회 | 1초 이내 |
| NFR-SCALE-01 | 동시 SSE 연결 (관리자) | 매장당 최대 10개 |
| NFR-SCALE-02 | 동시 SSE 연결 (고객) | 테이블당 최대 3개 |
| NFR-SCALE-03 | 동시 주문 처리 | 50~100 테이블 |

---

## 테스트 도구

- **Locust** (Python 기반 부하 테스트): `pip install locust`
- 또는 **k6** (Go 기반): `https://k6.io/`

---

## Locust 테스트 스크립트

```python
# backend/tests/performance/locustfile.py
from locust import HttpUser, task, between
import json
import random

class OrderUser(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        # 테이블 로그인 (토큰 발급)
        response = self.client.post("/api/auth/table/login", json={
            "store_code": "TEST01",
            "table_number": random.randint(1, 100),
            "password": "password"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")

    @task(3)
    def create_order(self):
        """주문 생성 (NFR-PERF-01: 1초 이내)"""
        self.client.post("/api/orders",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "table_id": random.randint(1, 100),
                "payment_type": random.choice(["SINGLE_PAY", "DUTCH_PAY"]),
                "items": [
                    {"menu_id": random.randint(1, 20), "quantity": random.randint(1, 5)}
                ]
            }
        )

    @task(5)
    def get_store_orders(self):
        """매장 주문 조회 (NFR-PERF-03: 500ms 이내)"""
        self.client.get("/api/stores/1/orders",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(2)
    def update_order_status(self):
        """주문 상태 변경 (NFR-PERF-04: 300ms 이내)"""
        self.client.patch(f"/api/orders/{random.randint(1, 100)}/status",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"status": "PREPARING"}
        )
```

## 실행

```bash
# Locust 실행
cd backend
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# 웹 UI: http://localhost:8089
# 설정: Users=100, Spawn rate=10
```

---

## SSE 성능 테스트

```python
# backend/tests/performance/sse_test.py
import asyncio
import aiohttp
import time

async def test_sse_latency(store_id: int, token: str):
    """SSE 이벤트 전달 지연 측정 (NFR-PERF-02: 2초 이내)"""
    url = f"http://localhost:8000/api/sse/admin/stores/{store_id}/orders"
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            start = time.time()
            async for line in resp.content:
                if line.startswith(b"data:"):
                    latency = time.time() - start
                    print(f"SSE 이벤트 수신 지연: {latency:.3f}초")
                    start = time.time()

async def test_concurrent_sse(store_id: int, count: int, token: str):
    """동시 SSE 연결 테스트 (NFR-SCALE-01: 매장당 10개)"""
    tasks = [test_sse_latency(store_id, token) for _ in range(count)]
    await asyncio.gather(*tasks)
```

---

## 결과 분석 기준

| 항목 | Pass 기준 | Fail 기준 |
|---|---|---|
| 주문 생성 P95 | < 1000ms | >= 1000ms |
| 주문 조회 P95 | < 500ms | >= 500ms |
| 상태 변경 P95 | < 300ms | >= 300ms |
| SSE 전달 지연 P95 | < 2000ms | >= 2000ms |
| 에러율 | < 1% | >= 1% |
| 동시 SSE 연결 | 10개 유지 | 연결 끊김 |
