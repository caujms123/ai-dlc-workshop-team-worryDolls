FROM python:3.11-slim

WORKDIR /app

# Python 의존성 설치 (aiomysql은 순수 Python이라 시스템 의존성 불필요)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# uploads 디렉토리 생성
RUN mkdir -p uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
