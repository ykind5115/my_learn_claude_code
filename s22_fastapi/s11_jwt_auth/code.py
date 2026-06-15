#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s11: 异常处理与中间件

═══════════════════════════════════════════════════════════════
学完本章你应该能回答:
  - 异常处理器怎么把"崩溃"变成"体面的 JSON"？
  - 三层异常处理金字塔是什么？
  - 中间件和 Depends 有什么区别？
  - CORS 是什么？怎么配？
═══════════════════════════════════════════════════════════════

启动:
    python s22_fastapi/s11_jwt_auth/code.py
    然后访问 http://localhost:8000/docs
"""

import time
import logging
from contextlib import asynccontextmanager
from collections import defaultdict

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ═══════════════════════════════════════════════════════════════
# 日志配置
# ═══════════════════════════════════════════════════════════════
# 生产环境不要用 print()，用 logging。
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("s11")


# ═══════════════════════════════════════════════════════════════
# 统一响应（从 s10 来）
# ═══════════════════════════════════════════════════════════════

class ApiResponse(BaseModel):
    code: int = 20000
    message: str = "success"
    data: object = None


# ═══════════════════════════════════════════════════════════════
# FastAPI App
# ═══════════════════════════════════════════════════════════════

app = FastAPI(
    title="s11 - 异常与中间件",
    description="错误统一处理，CORS 一行配好，请求自动记日志",
    version="11.0.0",
)


# ═══════════════════════════════════════════════════════════════
# 中间件 1: CORS — 允许跨域
# ═══════════════════════════════════════════════════════════════
# 前端在 localhost:3000，后端在 localhost:8000，
# 浏览器默认禁止这种"跨域"请求。
# CORS 中间件让后端告诉浏览器"我允许你来访问"。

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 学习阶段允许所有来源
    allow_credentials=True,       # 允许携带 cookie
    allow_methods=["*"],          # 允许所有 HTTP 方法
    allow_headers=["*"],          # 允许所有请求头
    expose_headers=["X-Request-ID", "X-Process-Time"],
)


# ═══════════════════════════════════════════════════════════════
# 中间件 2: 请求日志 — 记录每个请求
# ═══════════════════════════════════════════════════════════════

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    记录每个请求的: 方法、路径、状态码、耗时。

    async def middleware(request, call_next):
        # ← 请求进来（路由执行前）
        response = await call_next(request)  # 执行后续中间件 → 路由函数
        # ← 响应出去（路由执行后）
        return response
    """
    start = time.time()

    # 请求进来
    logger.info(f"→ {request.method} {request.url.path}")

    # 让请求继续往下走（经过所有中间件、路由函数）
    response = await call_next(request)

    # 响应出去
    duration_ms = (time.time() - start) * 1000
    status = response.status_code

    if status >= 500:
        logger.error(f"← {status} ({duration_ms:.0f}ms) ❌")
    elif status >= 400:
        logger.warning(f"← {status} ({duration_ms:.0f}ms) ⚠️")
    else:
        logger.info(f"← {status} ({duration_ms:.0f}ms)")

    # 在响应头里加上耗时（前端可以看到）
    response.headers["X-Process-Time"] = f"{duration_ms:.0f}ms"
    return response


# ═══════════════════════════════════════════════════════════════
# 中间件 3: 简易限流 — 防止滥用
# ═══════════════════════════════════════════════════════════════
# 每个 IP 每分钟最多 30 次请求。

class RateLimiter:
    def __init__(self, max_requests=30, window=60):
        self.max_requests = max_requests
        self.window = window
        self.buckets: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, ip: str) -> bool:
        now = time.time()
        # 清理过期的请求记录
        self.buckets[ip] = [t for t in self.buckets[ip] if now - t < self.window]
        if len(self.buckets[ip]) >= self.max_requests:
            return False
        self.buckets[ip].append(now)
        return True

rate_limiter = RateLimiter(max_requests=30)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """限流中间件"""
    # 获取客户端 IP
    client_ip = request.client.host if request.client else "unknown"

    if not rate_limiter.is_allowed(client_ip):
        logger.warning(f"🚫 限流触发: {client_ip}")
        return JSONResponse(
            status_code=429,
            content=ApiResponse(
                code=42900,
                message="请求太频繁，请稍后重试",
            ).model_dump(),
        )

    return await call_next(request)


# ═══════════════════════════════════════════════════════════════
# 异常处理器 — 三层金字塔
# ═══════════════════════════════════════════════════════════════

# 第 1 层: HTTPException
@app.exception_handler(HTTPException)
async def http_handler(request: Request, exc: HTTPException):
    """把 HTTPException 转为统一 JSON 格式"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            code=40000 + exc.status_code,
            message=exc.detail if isinstance(exc.detail, str) else "请求错误",
        ).model_dump(),
    )


# 第 2 层: ValueError（常见的业务校验异常）
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content=ApiResponse(code=40001, message=str(exc)).model_dump(),
    )


# 第 3 层: Exception — 兜底，捕获一切未预料的异常
@app.exception_handler(Exception)
async def global_handler(request: Request, exc: Exception):
    """兜底 — 任何未预料的异常都变成 500 + 统一格式"""
    logger.exception(f"未处理异常: {exc}")  # 记录完整堆栈
    return JSONResponse(
        status_code=500,
        content=ApiResponse(code=50000, message="服务器内部错误").model_dump(),
    )


# ═══════════════════════════════════════════════════════════════
# 演示接口
# ═══════════════════════════════════════════════════════════════

# 模拟数据
items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]


@app.get("/")
def root():
    return ApiResponse(
        message="s11 — 异常与中间件",
        data={
            "中间件": "CORS、请求日志、限流",
            "异常处理": "HTTPException → ValueError → Exception 兜底",
            "试试": [
                "GET /items/999  → 404",
                "POST /items     → 传空 name 触发 ValueError",
                "GET /crash      → 500（兜底异常处理器）",
                "快速刷新多次     → 429（限流触发）",
            ],
        },
    ).model_dump()


@app.get("/items")
def list_items():
    return ApiResponse(data=items).model_dump()


@app.get("/items/{item_id}")
def get_item(item_id: int):
    """演示 404 — 触发 HTTPException 处理器"""
    for item in items:
        if item["id"] == item_id:
            return ApiResponse(data=item).model_dump()
    raise HTTPException(status_code=404, detail=f"Item {item_id} 不存在")


@app.post("/items", status_code=201)
def create_item(name: str):
    """演示参数校验 — 触发 ValueError 处理器"""
    if not name or len(name) < 2:
        raise ValueError("name 至少需要 2 个字符")
    new_item = {"id": len(items) + 1, "name": name}
    items.append(new_item)
    return ApiResponse(data=new_item).model_dump()


@app.get("/crash")
def crash():
    """演示兜底异常 — 触发 Exception 处理器"""
    raise RuntimeError("模拟一个未预料的服务器错误")


@app.get("/health")
def health():
    """健康检查（监控系统用）"""
    return {"status": "ok"}


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    print("=" * 55)
    print("s11 — 异常与中间件")
    print("   访问 http://localhost:8000/docs")
    print("   观察控制台日志输出！")
    print("   试试 GET /crash → 异常处理器会接住它")
    print("   快速刷新多次 → 限流中间件触发 429")
    print("=" * 55)
    uvicorn.run(app, host="0.0.0.0", port=8000)
