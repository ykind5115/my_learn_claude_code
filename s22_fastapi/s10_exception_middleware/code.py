#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s10: 统一响应封装 — 所有接口返回 {code, message, data}

═══════════════════════════════════════════════════════════════
学完本章你应该能回答:
  - 为什么要统一响应格式？（前端只需要一种解析逻辑）
  - code/message/data 分别代表什么？
  - 业务状态码（code）和 HTTP 状态码有什么区别？
  - 工厂方法 (success/error) 怎么用？
═══════════════════════════════════════════════════════════════

启动:
    python s22_fastapi/s10_exception_middleware/code.py
    然后访问 http://localhost:8000/docs
"""

from enum import IntEnum
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════
# 第 1 步: 定义业务状态码
# ═══════════════════════════════════════════════════════════════
# 业务状态码 ≠ HTTP 状态码！
# 前者告诉前端"业务上发生了什么"，
# 后者是 HTTP 协议层面的。

class StatusCode(IntEnum):
    """业务状态码 — 和 HTTP 状态码独立"""
    # 成功
    SUCCESS = 20000

    # 客户端错误 (4xxxx)
    BAD_REQUEST = 40000          # 请求参数有误
    VALIDATION_ERROR = 42200     # 数据校验失败
    UNAUTHORIZED = 40100         # 未登录
    FORBIDDEN = 40300            # 没权限
    NOT_FOUND = 40400            # 资源不存在
    CONFLICT = 40900             # 冲突（如重复注册）

    # 服务器错误 (5xxxx)
    INTERNAL_ERROR = 50000       # 服务器内部错误


# ═══════════════════════════════════════════════════════════════
# 第 2 步: 定义统一响应模型
# ═══════════════════════════════════════════════════════════════

class ApiResponse(BaseModel):
    """
    统一 API 响应格式。

    无论成功还是失败，前端收到的 JSON 都是这个结构:
      {"code": 20000, "message": "success", "data": {...}}

    接口里用它:
      return ApiResponse.success(data=user)
      return ApiResponse.error(StatusCode.NOT_FOUND, "用户不存在")
    """
    code: int = StatusCode.SUCCESS.value
    message: str = "success"
    data: Any = None

    model_config = {
        "json_schema_extra": {
            "example_success": {
                "code": 20000,
                "message": "success",
                "data": {"id": 1, "name": "张三"},
            },
            "example_error": {
                "code": 40400,
                "message": "用户不存在",
                "data": None,
            },
        }
    }

    # ── 工厂方法 ────────────────────────────────────────────
    # 工厂方法 = 创建特定类型的 ApiResponse 的快捷方式

    @classmethod
    def success(cls, data: Any = None, message: str = "success") -> "ApiResponse":
        """快速创建成功响应"""
        return cls(code=StatusCode.SUCCESS.value, message=message, data=data)

    @classmethod
    def error(cls, code: StatusCode, message: str) -> "ApiResponse":
        """快速创建错误响应"""
        return cls(code=code.value, message=message, data=None)


# ═══════════════════════════════════════════════════════════════
# 业务异常类
# ═══════════════════════════════════════════════════════════════

class AppException(Exception):
    """
    自定义业务异常。

    和 HTTPException 的区别:
      HTTPException → HTTP 层面错误（404, 500...）
      AppException  → 业务层面错误（余额不足、库存不够...）

    用法:
      raise AppException(StatusCode.INSUFFICIENT_STOCK, "库存不足")
    """
    def __init__(self, code: StatusCode, message: str):
        self.code = code
        self.message = message


# ═══════════════════════════════════════════════════════════════
# Pydantic Schema（普通的请求/响应模型）
# ═══════════════════════════════════════════════════════════════

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str


# ═══════════════════════════════════════════════════════════════
# FastAPI App
# ═══════════════════════════════════════════════════════════════

app = FastAPI(
    title="s10 - 统一响应封装",
    description="所有接口返回 {code, message, data} — 前端只需一种解析逻辑",
    version="10.0.0",
)

# 模拟数据
users_db: list[dict] = [
    {"id": 1, "name": "张三", "email": "zhangsan@example.com"},
]
_id_counter = 1


# ═══════════════════════════════════════════════════════════════
# 接口 — 全部返回 ApiResponse 格式
# ═══════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return ApiResponse.success(
        data={
            "message": "s10 — 统一响应封装",
            "docs": "/docs",
        }
    )


@app.post("/users", status_code=201)
def create_user(user_in: UserCreate):
    """
    创建用户 — 成功返回 ApiResponse.success()。

    响应格式:
      {"code": 20000, "message": "创建成功", "data": {"id": 2, "name": "..."}}
    """
    global _id_counter
    _id_counter += 1

    # 检查邮箱唯一性
    for u in users_db:
        if u["email"] == user_in.email:
            return ApiResponse.error(
                code=StatusCode.CONFLICT,
                message=f"邮箱 {user_in.email} 已被注册",
            )
            # 注意: 这里 HTTP status code 还是 201（装饰器设的）
            # 但业务 code 是 40900 — 前端看 code 字段来判断成功与否

    new_user = {"id": _id_counter, "name": user_in.name, "email": user_in.email}
    users_db.append(new_user)

    return ApiResponse.success(data=new_user, message="创建成功")


@app.get("/users")
def list_users():
    """用户列表 — data 字段是一个数组"""
    return ApiResponse.success(data=users_db)


@app.get("/users/{user_id}")
def get_user(user_id: int):
    """获取单个用户 — 不存在时返回 ApiResponse.error()"""
    for u in users_db:
        if u["id"] == user_id:
            return ApiResponse.success(data=u)

    return ApiResponse.error(
        code=StatusCode.NOT_FOUND,
        message=f"用户 {user_id} 不存在",
    )


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    """删除用户 — 成功但 data 为 null"""
    global users_db
    for i, u in enumerate(users_db):
        if u["id"] == user_id:
            deleted = users_db.pop(i)
            return ApiResponse.success(data=deleted, message="删除成功")

    return ApiResponse.error(
        code=StatusCode.NOT_FOUND,
        message=f"用户 {user_id} 不存在",
    )


# ═══════════════════════════════════════════════════════════════
# 演示：对比不同格式
# ═══════════════════════════════════════════════════════════════

@app.get("/old-style")
def old_style():
    """
    旧格式（s09 之前的做法）— 没有统一封装。
    返回裸数据，出错时格式不一致。
    """
    return users_db  # 直接返回列表


@app.get("/new-style")
def new_style():
    """
    新格式（s10 之后）— 统一封装。
    所有接口都返回 {code, message, data}。
    """
    return ApiResponse.success(data=users_db)


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    print("=" * 55)
    print("s10 — 统一响应封装")
    print("   访问 http://localhost:8000/docs")
    print("   对比 GET /old-style 和 GET /new-style")
    print("   看看前端更喜欢哪种格式？")
    print("=" * 55)
    uvicorn.run(app, host="0.0.0.0", port=8000)
