#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s17: 部署 — 生产环境准备

═══════════════════════════════════════════════════════════════
学完本章你应该能回答:
  - 生产部署和开发环境有什么不同？
  - Dockerfile 怎么写的？
  - 健康检查（/health + /ready）是干嘛的？
  - 为什么配置要从环境变量读？
═══════════════════════════════════════════════════════════════

启动（开发模式）:
    python s22_fastapi/s17_deployment/code.py

Docker 部署:
    docker build -t s17-api -f s22_fastapi/s17_deployment/Dockerfile .
    docker run -p 8000:8000 -e SECRET_KEY=mykey s17-api

Gunicorn（Linux/Mac）:
    pip install gunicorn
    cd s22_fastapi && gunicorn -w 4 -k uvicorn.workers.UvicornWorker s17_deployment.code:app
"""

import os
import time
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ═══════════════════════════════════════════════════════════════
# 环境变量配置
# ═══════════════════════════════════════════════════════════════
# 生产环境所有配置从环境变量读取！
# 硬编码 = 密码泄露到 Git 仓库 = 安全事故

APP_NAME = os.getenv("APP_NAME", "s17-api")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# 生产环境检查必需的环境变量
if not DEBUG and not SECRET_KEY:
    raise RuntimeError("生产环境必须设置 SECRET_KEY 环境变量！")

# ═══════════════════════════════════════════════════════════════
# 结构化日志
# ═══════════════════════════════════════════════════════════════
# 生产环境不能用 print() — 日志要能导出、能搜索、能聚合

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(APP_NAME)


# ═══════════════════════════════════════════════════════════════
# App
# ═══════════════════════════════════════════════════════════════

app = FastAPI(
    title=APP_NAME,
    version="17.0.0",
    docs_url="/docs" if DEBUG else None,    # 生产环境隐藏 API 文档
    redoc_url=None,
)

# CORS — 控制哪些前端可以访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全中间件
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# 请求日志
@app.middleware("http")
async def request_log(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration:.0f}ms)")
    response.headers["X-Process-Time"] = f"{duration:.0f}ms"
    return response


# ═══════════════════════════════════════════════════════════════
# 健康检查（Kubernetes / 负载均衡器必需）
# ═══════════════════════════════════════════════════════════════

@app.get("/health")
def liveness_check():
    """Liveness probe — 服务还活着吗？"""
    return {"status": "healthy", "app": APP_NAME}


@app.get("/ready")
def readiness_check():
    """Readiness probe — 准备好接受请求了吗？"""
    # 实际项目要检查数据库、Redis 等依赖
    # db_ok = check_database_connection()
    db_ok = True
    if db_ok:
        return {"status": "ready"}
    return JSONResponse(status_code=503, content={"status": "not ready"})


# ═══════════════════════════════════════════════════════════════
# 业务接口
# ═══════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {
        "app": APP_NAME,
        "version": "17.0.0",
        "debug": DEBUG,
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "docs": "/docs" if DEBUG else "(已隐藏)",
        },
    }


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    logger.info(f"启动 {APP_NAME}...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=DEBUG)
