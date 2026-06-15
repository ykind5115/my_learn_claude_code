# s17 FastAPI 生产 Dockerfile
# 构建: docker build -t s17-api -f s22_fastapi/s17_deployment/Dockerfile .
# 运行: docker run -p 8000:8000 -e SECRET_KEY=prod-secret s17-api

FROM python:3.12-slim

# 环境变量 — 让 Python 行为更可预测
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 先装依赖（利用 Docker 缓存 — 不常变的东西放前面）
COPY s22_fastapi/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY s22_fastapi/s17_deployment/code.py /app/main.py

# 创建非 root 用户（安全最佳实践）
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
