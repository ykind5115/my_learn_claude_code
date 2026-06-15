# s16 FastAPI 生产 Dockerfile
# 构建: docker build -t s16-api -f s16_deployment/Dockerfile .
# 运行: docker run -p 8000:8000 --env-file .env s16-api

FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装依赖
COPY s22_fastapi/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# 复制应用代码（只复制需要的文件）
COPY s22_fastapi/s16_deployment/code.py /app/main.py

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# 暴露端口
EXPOSE 8000

# 启动命令（生产环境用 gunicorn）
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "main:app"]
