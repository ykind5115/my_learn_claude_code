#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s04: 请求体 — 用 Pydantic 接收 POST 数据

═══════════════════════════════════════════════════════════════
学完本章你应该能回答:
  - POST 请求的数据放在哪？（Body，不是 URL）
  - Pydantic BaseModel 是干什么的？
  - FastAPI 怎么自动校验 JSON body？
  - response_model 有什么用？
  - 嵌套 Pydantic 模型怎么写？
═══════════════════════════════════════════════════════════════

启动:
    python s22_fastapi/s04_request_body/code.py
    然后访问 http://localhost:8000/docs
    重点: 在 Swagger UI 里 Try it out，传入各种数据试试！
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="s04 - 请求体",
    description="第一次学 Pydantic：用 BaseModel 接收和校验 JSON Body",
    version="4.0.0",
)


# ═══════════════════════════════════════════════════════════════
# 第 1 步: 定义 Pydantic 模型
# ═══════════════════════════════════════════════════════════════
#
# Pydantic 模型 = 一个普通的 Python 类，继承 BaseModel。
# 区别是：Pydantic 会帮你做数据校验和类型转换。
#
# 写法: class 类名(BaseModel):
#           字段名: 类型


class ItemCreate(BaseModel):
    """
    创建商品时接收的数据结构。

    客户端应该发送这样的 JSON:
    {
        "title": "机械键盘",
        "price": 399.0,
        "stock": 50,
        "tags": ["电子产品", "外设"]
    }
    """
    title: str          # ← 必填，必须是字符串
    price: float        # ← 必填，必须是数字（int 或 float）
    stock: int = 0      # ← 可选，不传默认是 0
    tags: list[str] = [] # ← 可选，不传默认是空列表
    # 注意: 有默认值的字段 = 可选的；没有默认值的字段 = 必填的


class ItemResponse(BaseModel):
    """
    返回给客户端的数据结构。

    和 ItemCreate 很像，但多了 id 字段。
    真实项目中 Request 和 Response 应该用不同的模型 —
    因为接收和返回的数据结构往往不同。
    """
    id: int
    title: str
    price: float
    stock: int
    tags: list[str]


# ═══════════════════════════════════════════════════════════════
# 嵌套模型示例
# ═══════════════════════════════════════════════════════════════

class Address(BaseModel):
    """地址 — 会被 UserCreate 嵌套使用"""
    province: str       # 省
    city: str           # 市
    detail: str         # 详细地址


class UserCreate(BaseModel):
    """
    创建用户时的请求体。

    客户端应发送:
    {
        "name": "张三",
        "age": 25,
        "email": "zhangsan@example.com",
        "address": {
            "province": "北京",
            "city": "北京",
            "detail": "望京 SOHO"
        }
    }

    address 字段的类型是 Address（另一个 BaseModel）—
    这就叫"嵌套模型"。FastAPI 会递归校验每一层。
    """
    name: str
    age: int
    email: str
    address: Address | None = None  # 可选嵌套 — 可以不传地址


class UserResponse(BaseModel):
    """
    返回给客户端的数据结构。

    注意: 有 id，没有 email（演示 response_model 的过滤功能）。
    """
    id: int
    name: str
    age: int
    # 注意: 这里没有 email 字段！
    # 如果接口里用了 response_model=UserResponse，email 不会被返回
    address: Address | None = None


# ═══════════════════════════════════════════════════════════════
# 模拟数据存储
# ═══════════════════════════════════════════════════════════════

items_db: list[dict] = []
users_db: list[dict] = []
_item_id_counter = 0
_user_id_counter = 0


# ═══════════════════════════════════════════════════════════════
# 根路径
# ═══════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {
        "message": "s04 — 请求体",
        "概念": "Pydantic BaseModel 让 POST Body 校验一行都不用写",
        "试试": [
            "POST /items — 创建商品（JSON body 带 title, price 等）",
            "POST /users — 创建用户（带嵌套 Address）",
            "GET /items  — 查看所有商品",
        ],
        "文档": "http://localhost:8000/docs",
    }


# ═══════════════════════════════════════════════════════════════
# 商品接口 — POST 创建 + GET 列表
# ═══════════════════════════════════════════════════════════════

@app.post("/items", status_code=201, response_model=ItemResponse)
def create_item(item: ItemCreate):
    """
    创建商品。

    参数 item: ItemCreate:
      FastAPI 看到参数类型是 Pydantic BaseModel 子类，
      就自动从请求 Body 中解析 JSON，用 ItemCreate 校验。

    校验内容:
      - title 必须是字符串，且必须传
      - price 必须是数字，且必须传
      - stock 如果不传，默认是 0
      - tags 如果不传，默认是 []

    试试在 /docs 里故意传错的数据:
      - 不传 title → 422
      - price 传 "abc" → 422
      - 传额外的 unknown_field → 默认被忽略
    """
    global _item_id_counter
    _item_id_counter += 1

    # item 是 ItemCreate 实例 — 它的属性已经是正确类型了
    # item.title  → str
    # item.price  → float (即使客户端传了 399, 也会变成 399.0)
    new_item = {
        "id": _item_id_counter,
        "title": item.title,
        "price": item.price,
        "stock": item.stock,
        "tags": item.tags,
    }
    items_db.append(new_item)

    # response_model=ItemResponse 会在返回前过滤多余字段
    return new_item


@app.get("/items", response_model=list[ItemResponse])
def list_items():
    """
    返回所有商品。

    list[ItemResponse] 的意思:
      返回一个列表，列表里每个元素都是 ItemResponse 格式。
      FastAPI 2.0+ 支持这种写法。
    """
    return items_db


# ═══════════════════════════════════════════════════════════════
# 用户接口 — 演示嵌套模型 + response_model 过滤
# ═══════════════════════════════════════════════════════════════

@app.post("/users", status_code=201, response_model=UserResponse)
def create_user(user: UserCreate):
    """
    创建用户 — 演示嵌套模型。

    请求体应该类似:
    {
        "name": "张三",
        "age": 25,
        "email": "zhangsan@example.com",
        "address": {
            "province": "北京",
            "city": "北京",
            "detail": "望京 SOHO"
        }
    }

    FastAPI 会:
    1. 解析最外层 JSON → UserCreate
    2. 发现 address 字段的类型是 Address
    3. 递归解析 address → Address 对象
    4. 每一层都做类型校验

    response_model=UserResponse:
      UserResponse 里没有 email —
      即使 user.email 有值，返回时也会被过滤掉！
    """
    global _user_id_counter
    _user_id_counter += 1

    # user.address 是 Address 对象
    # user.address.city → "北京" (str)
    new_user = {
        "id": _user_id_counter,
        "name": user.name,
        "age": user.age,
        "email": user.email,        # 存在数据库里
        "address": user.address.model_dump() if user.address else None,
        # .model_dump() 把 Pydantic 模型转回 dict
    }
    users_db.append(new_user)

    # 返回时 response_model 会自动去掉 email
    return new_user


@app.get("/users", response_model=list[UserResponse])
def list_users():
    """返回所有用户 — 注意 email 不会出现在响应中"""
    return users_db


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    """获取单个用户"""
    for u in users_db:
        if u["id"] == user_id:
            return u
    raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn

    print("=" * 55)
    print("s04 — 请求体")
    print("   访问 http://localhost:8000/docs")
    print("   试试 POST /items 和 POST /users")
    print("   故意传错的数据类型，观察 422 错误信息")
    print("   注意 response_model 如何过滤返回字段")
    print("=" * 55)

    uvicorn.run(app, host="0.0.0.0", port=8000)
