FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 創建數據庫目錄
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 8000

# 運行應用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
