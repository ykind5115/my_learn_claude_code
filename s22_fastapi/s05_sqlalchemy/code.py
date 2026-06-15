#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s05: 数据校验 — 用 Field() 加约束

═══════════════════════════════════════════════════════════════
学完本章你应该能回答:
  - Field() 的 ge/le/min_length/max_length/pattern 怎么用？
  - 校验失败时 FastAPI 返回的 422 长什么样？
  - 枚举 Enum 怎么限制参数只能取某几个值？
  - model_validator 什么时候用？（跨字段校验）
═══════════════════════════════════════════════════════════════

启动:
    python s22_fastapi/s05_sqlalchemy/code.py
    然后访问 http://localhost:8000/docs
    重点: 在 Swagger UI 里故意传违规数据，观察 422 的详细信息
"""

from datetime import date
from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, model_validator

app = FastAPI(
    title="s05 - 数据校验",
    description="学习 Field() 约束：长度、范围、正则、枚举",
    version="5.0.0",
)

# ═══════════════════════════════════════════════════════════════
# 枚举类
# ═══════════════════════════════════════════════════════════════

class UserRole(str, Enum):
    """用户角色 — 只能是这三个值之一"""
    admin = "admin"
    editor = "editor"
    user = "user"


class OrderStatus(str, Enum):
    """订单状态"""
    pending = "pending"       # 待处理
    shipped = "shipped"       # 已发货
    delivered = "delivered"   # 已送达
    cancelled = "cancelled"   # 已取消


# ═══════════════════════════════════════════════════════════════
# Pydantic 模型 — 带详细校验
# ═══════════════════════════════════════════════════════════════

class UserRegister(BaseModel):
    """
    用户注册 — 每个字段都有精细约束。

    试试在 /docs 里传各种违规数据:
      - name: "" (空字符串)     → 422 (min_length=1)
      - name: "a" * 51         → 422 (max_length=50)
      - age: -1                → 422 (ge=0)
      - age: 200               → 422 (le=150)
      - email: "not-an-email"  → 422 (pattern 不匹配)
      - password: "12345"      → 422 (min_length=6)
      - role: "superadmin"     → 422 (不在枚举中)
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="用户名（1-50 字符）",
        examples=["张三"],
    )
    age: int = Field(
        ...,
        ge=0,        # greater or equal — 0 岁
        le=150,      # less or equal — 150 岁
        description="年龄（0-150）",
        examples=[25],
    )
    email: str = Field(
        ...,
        min_length=5,
        max_length=100,
        # 正则表达式: 校验邮箱格式
        # 逐段解读:
        #   ^                    字符串开头
        #   [a-zA-Z0-9_.+-]+     用户名部分（字母数字 + 一些符号）
        #   @                    必须有一个 @
        #   [a-zA-Z0-9-]+        域名部分
        #   \.                   必须有一个点
        #   [a-zA-Z0-9-.]+       顶级域名
        #   $                    字符串结尾
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="邮箱地址",
        examples=["zhangsan@example.com"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="密码（至少 6 位）",
    )
    confirm_password: str = Field(
        ...,
        min_length=6,
        description="确认密码（必须和 password 一致）",
    )
    role: UserRole = Field(
        default=UserRole.user,     # 默认普通用户
        description="用户角色",
    )

    @model_validator(mode="after")
    def passwords_match(self):
        """
        跨字段校验: 确认密码必须和密码一致。

        mode="after" 表示在每个字段单独校验完之后再执行。
        如果校验失败，抛 ValueError 即可，FastAPI 会自动转为 422。
        """
        if self.password != self.confirm_password:
            raise ValueError("两次输入的密码不一致")
        return self


class UserResponse(BaseModel):
    """用户响应（不包含密码）"""
    id: int
    name: str
    age: int
    email: str
    role: UserRole


class OrderCreate(BaseModel):
    """
    创建订单 — 演示枚举 + Field 混用。
    """
    product_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="商品名称",
    )
    quantity: int = Field(
        ...,
        ge=1,        # 至少 1 件
        le=999,      # 最多 999 件
        description="数量",
    )
    price: float = Field(
        ...,
        gt=0,        # 大于 0（不能用 ge=0，价格不能是 0）
        description="单价",
    )
    status: OrderStatus = Field(
        default=OrderStatus.pending,
        description="订单状态",
    )


# ═══════════════════════════════════════════════════════════════
# 模拟数据库
# ═══════════════════════════════════════════════════════════════

users_db: list[dict] = []
_user_counter = 0


# ═══════════════════════════════════════════════════════════════
# 接口
# ═══════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {
        "message": "s05 — 数据校验",
        "核心": "Field() 给每个字段加约束，model_validator 做跨字段校验",
        "试试": [
            "POST /users — 传违规数据，观察 422 错误详情",
            "POST /users — 传 confirm_password 和 password 不一致",
            "POST /orders — 传 price=0（gt=0 会拒绝）",
        ],
        "文档": "http://localhost:8000/docs",
    }


@app.post("/users", status_code=201, response_model=UserResponse)
def register_user(user: UserRegister):
    """
    用户注册。

    如果数据校验失败，FastAPI 返回 422。
    注意 422 的 detail 字段：它是一个数组，列出了所有不合法的字段，
    而不是只报第一个错误。
    """
    global _user_counter
    _user_counter += 1

    # 模拟: 检查邮箱是否已被注册
    for u in users_db:
        if u["email"] == user.email:
            raise HTTPException(status_code=409, detail="邮箱已被注册")

    new_user = {
        "id": _user_counter,
        "name": user.name,
        "age": user.age,
        "email": user.email,
        "role": user.role.value,     # Enum 的 .value 拿到原始字符串
        "password": user.password,    # 真实项目要哈希（s12）
    }
    users_db.append(new_user)

    # response_model 自动去掉 password 和 confirm_password
    return new_user


@app.get("/users", response_model=list[UserResponse])
def list_users():
    """列出所有用户"""
    return users_db


@app.post("/orders", status_code=201)
def create_order(order: OrderCreate):
    """创建订单 — 演示 gt=0 的校验效果"""
    return {
        "message": "订单创建成功",
        "order": order.model_dump(),
    }


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn

    print("=" * 55)
    print("s05 — 数据校验")
    print("   访问 http://localhost:8000/docs")
    print("   试试 POST /users 传各种违规数据:")
    print("   - name 为空 → 422")
    print("   - age=999 → 422")
    print("   - email='abc' → 422 (pattern)")
    print("   - 两个密码不一致 → 422 (model_validator)")
    print("   注意: 422 的 detail 列出了所有不合法的字段！")
    print("=" * 55)

    uvicorn.run(app, host="0.0.0.0", port=8000)
