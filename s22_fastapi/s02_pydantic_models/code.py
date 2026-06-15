#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s02: 返回数据 — JSON、状态码与自动文档

═══════════════════════════════════════════════════════════════
学完本章你应该能回答:
  - dict 怎么变成 JSON 的？
  - 怎么返回列表？嵌套结构？
  - 什么场景用什么状态码？
  - 怎么用 HTTPException 告诉前端"出错了"？
  - /docs 页面怎么用？
═══════════════════════════════════════════════════════════════

启动:
    python s22_fastapi/s02_pydantic_models/code.py
    然后访问 http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException

# ═══════════════════════════════════════════════════════════════
# 创建 FastAPI 应用（和 s01 一样）
# ═══════════════════════════════════════════════════════════════
app = FastAPI(
    title="s02 - 返回数据",
    description="学习：JSON 转换、状态码、错误返回、/docs 文档",
    version="2.0.0",
)

# ═══════════════════════════════════════════════════════════════
# 模拟数据 — 假装这是数据库
# ═══════════════════════════════════════════════════════════════
# 在 s06 之前，我们用列表 + 字典模拟数据库。
# 这样服务器重启数据就没了 — 但学习阶段不影响。

users_db = [
    {"id": 1, "name": "张三", "role": "admin", "active": True},
    {"id": 2, "name": "李四", "role": "user", "active": True},
    {"id": 3, "name": "王五", "role": "user", "active": False},
]

products_db = [
    {"id": 101, "name": "机械键盘", "price": 399, "stock": 50},
    {"id": 102, "name": "鼠标", "price": 199, "stock": 120},
    {"id": 103, "name": "显示器", "price": 1999, "stock": 30},
]


# ═══════════════════════════════════════════════════════════════
# 根路径 — 导航
# ═══════════════════════════════════════════════════════════════
@app.get("/")
def root():
    """欢迎页 + 导航"""
    return {
        "message": "s02 — 返回数据",
        "试试这些": [
            "GET /users           — 返回列表",
            "GET /users/1         — 返回单个 + 嵌套",
            "GET /users/999       — 返回 404 错误",
            "GET /products        — 商品列表",
            "POST /users?name=新用户 — 创建（状态码 201）",
        ],
        "文档": "http://localhost:8000/docs",
    }


# ═══════════════════════════════════════════════════════════════
# 1. 返回列表
# ═══════════════════════════════════════════════════════════════

@app.get("/users")
def list_users():
    """
    返回用户列表。

    FastAPI 看到 return 了一个 list，会自动转成 JSON 数组:
      [{"id": 1, ...}, {"id": 2, ...}, ...]
    """
    return users_db  # ← 直接返回整个列表


# ═══════════════════════════════════════════════════════════════
# 2. 返回单个 + 嵌套结构
# ═══════════════════════════════════════════════════════════════

@app.get("/users/{user_id}")
def get_user(user_id: int):
    """
    返回单个用户 + 嵌套的订单信息。

    返回结构:
      {
        "id": 1,
        "name": "张三",
        "orders": [        ← 嵌套列表
          {"order_id": 201, "total": 299.00}
        ],
        "address": {...}   ← 嵌套 dict
      }
    """
    # 先找到用户
    user = None
    for u in users_db:
        if u["id"] == user_id:
            user = u
            break

    # 如果找不到 → 返回 404
    if user is None:
        raise HTTPException(
            status_code=404,
            detail=f"用户 {user_id} 不存在",
        )

    # 返回嵌套结构 — dict 里面可以无限嵌套
    return {
        "id": user["id"],
        "name": user["name"],
        "role": user["role"],
        "active": user["active"],
        # 嵌套: 这个用户的订单（模拟数据）
        "orders": [
            {"order_id": 201, "total": 299.00, "status": "已完成"},
            {"order_id": 205, "total": 159.00, "status": "配送中"},
        ],
        # 嵌套: 地址对象
        "address": {
            "province": "北京市",
            "city": "北京市",
            "detail": "朝阳区望京 SOHO",
        },
    }


# ═══════════════════════════════════════════════════════════════
# 3. 创建用 201 状态码
# ═══════════════════════════════════════════════════════════════

@app.post("/users", status_code=201)
def create_user(name: str, role: str = "user"):
    """
    创建一个新用户 — 返回 HTTP 201 Created。

    注意 status_code=201:
      - GET 默认 200
      - POST 创建成功应该用 201 (Created)
      - DELETE 成功应该用 204 (No Content)
    """
    # 简单参数校验
    if not name:
        raise HTTPException(status_code=400, detail="name 不能为空")

    new_id = max(u["id"] for u in users_db) + 1 if users_db else 1
    new_user = {"id": new_id, "name": name, "role": role, "active": True}
    users_db.append(new_user)

    # 返回新创建的用户，HTTP 状态码是 201
    return new_user


# ═══════════════════════════════════════════════════════════════
# 4. 删除用 204 状态码
# ═══════════════════════════════════════════════════════════════

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    """
    删除用户 — 返回 HTTP 204 No Content。

    204 表示"操作成功，但没有响应体"。
    函数不需要 return 任何东西。
    """
    for i, u in enumerate(users_db):
        if u["id"] == user_id:
            users_db.pop(i)
            # 不需要 return — FastAPI 自动返回 204
            return

    # 如果循环完没找到 → 404
    raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")


# ═══════════════════════════════════════════════════════════════
# 5. 商品数据 — 看 /docs 怎么展示
# ═══════════════════════════════════════════════════════════════

@app.get("/products")
def list_products(available_only: bool = False):
    """
    返回商品列表，可以选择只看有库存的。

    查询参数: ?available_only=true
    （查询参数的用法下一章 s03 会详细讲）
    """
    if available_only:
        return [p for p in products_db if p["stock"] > 0]
    return products_db


@app.get("/products/{product_id}")
def get_product(product_id: int):
    """返回单个商品"""
    for p in products_db:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail=f"商品 {product_id} 不存在")


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn

    print("=" * 55)
    print("s02 — 返回数据")
    print("   访问 http://localhost:8000/docs")
    print("   在 Swagger UI 里试试:")
    print("   - GET /users         → 返回列表")
    print("   - GET /users/1       → 返回嵌套结构")
    print("   - GET /users/999     → 返回 404 错误")
    print("   - POST /users        → 创建用户（201 状态码）")
    print("   - DELETE /users/1    → 删除用户（204 状态码）")
    print("=" * 55)

    uvicorn.run(app, host="0.0.0.0", port=8000)
