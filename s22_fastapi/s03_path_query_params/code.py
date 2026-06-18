#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s03: 接收参数 — 路径参数和查询参数

═══════════════════════════════════════════════════════════════
学完本章你应该能回答:
  - 路径参数和查询参数有什么区别？什么时候用哪个？
  - FastAPI 怎么知道一个参数来自路径还是来自查询？
  - Query() 和 Path() 的 ge/le/min_length 怎么用？
  - 怎么用 Enum 限定参数只能取某几个值？
═══════════════════════════════════════════════════════════════

启动:
    python s22_fastapi/s03_path_query_params/code.py
    然后访问 http://localhost:8000/docs — 重点看参数校验！
"""

from enum import Enum

from fastapi import FastAPI, Query, Path

app = FastAPI(
    title="s03 - 接收参数",
    description="学习：路径参数、查询参数、校验、枚举",
    version="3.0.0",
)


# ═══════════════════════════════════════════════════════════════
# 枚举类 — 限定可选值
# ═══════════════════════════════════════════════════════════════
# 枚举让参数只能取预设的几个值，传别的值 → 422 错误

class Category(str, Enum):
    """商品分类 — 只能选这三个"""
    electronics = "electronics"
    clothing = "clothing"
    books = "books"


class SortBy(str, Enum):
    """排序字段"""
    price = "price"       # 按价格
    name = "name"         # 按名称
    rating = "rating"     # 按评分


class SortOrder(str, Enum):
    """排序方向"""
    asc = "asc"           # 升序: 1,2,3 或 a,b,c
    desc = "desc"         # 降序: 3,2,1 或 c,b,a


# ═══════════════════════════════════════════════════════════════
# 模拟数据
# ═══════════════════════════════════════════════════════════════

products_db = [
    {"id": 1, "name": "Python 编程入门", "category": "books", "price": 89.0, "rating": 4.8},
    {"id": 2, "name": "算法导论", "category": "books", "price": 128.0, "rating": 4.9},
    {"id": 3, "name": "机械键盘", "category": "electronics", "price": 399.0, "rating": 4.5},
    {"id": 4, "name": "无线鼠标", "category": "electronics", "price": 199.0, "rating": 4.3},
    {"id": 5, "name": "蓝牙耳机", "category": "electronics", "price": 599.0, "rating": 4.6},
    {"id": 6, "name": "T恤 白色", "category": "clothing", "price": 159.0, "rating": 4.1},
    {"id": 7, "name": "牛仔裤", "category": "clothing", "price": 399.0, "rating": 4.2},
    {"id": 8, "name": "运动鞋", "category": "clothing", "price": 699.0, "rating": 4.4},
]


# ═══════════════════════════════════════════════════════════════
# 根路径
# ═══════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {
        "message": "s03 — 接收参数",
        "试试": [
            "GET /products?category=electronics",
            "GET /products?min_price=100&max_price=500&sort_by=rating&order=desc",
            "GET /products?keyword=键盘&page=1&size=5",
            "GET /users/42               ← 路径参数",
            "GET /users/abc              ← 422 错误（不是 int）",
        ],
        "文档": "http://localhost:8000/docs",
    }


# ═══════════════════════════════════════════════════════════════
# 路径参数复习（s01 的内容）
# ═══════════════════════════════════════════════════════════════

@app.get("/users/{user_id}")
def get_user(
    user_id: int = Path(
        ...,                     # ... 表示必填（路径参数本来就是必填的）
        ge=1,                    # greater or equal — 必须 >= 1
        description="用户的唯一 ID",
        examples=[42],           # 在 /docs 里显示的示例值
    ),
):
    """
    路径参数 + Path() 校验。

    试试:
      /users/42   → 正常
      /users/0    → 422 (ge=1 要求 >= 1)
      /users/abc  → 422 (不是 int)
    """
    return {"user_id": user_id, "message": f"查询用户 {user_id}"}


@app.get("/articles/{slug}")
def get_article(
    slug: str = Path(
        ...,
        min_length=3,            # 最少 3 个字符
        max_length=100,          # 最多 100 个字符
        description="文章的 URL 友好标识",
    ),
):
    """
    路径参数用字符串类型 + 长度校验。

    /articles/hello-world  ✅ (长度 >= 3)
    /articles/ab           ❌ 422 (长度不足)
    """
    return {"slug": slug, "title": f"文章: {slug}"}


# ═══════════════════════════════════════════════════════════════
# ★ 重点：查询参数 + 校验
# ═══════════════════════════════════════════════════════════════
# 规则: 函数参数不在 URL 路径模板里 → 自动成为查询参数

@app.get("/products")
def list_products(
    # ── 过滤参数 ──────────────────────────────────────────────
    category: Category | None = Query(
        default=None,
        description="按分类过滤（三选一）",
    ),
    keyword: str | None = Query(
        default=None,
        min_length=2,            # 如果传了，至少 2 个字符
        max_length=50,
        description="搜索商品名（模糊匹配）",
    ),

    # ── 价格区间 ──────────────────────────────────────────────
    min_price: float | None = Query(
        default=None,
        ge=0,                    # 价格不能为负
        description="最低价格",
    ),
    max_price: float | None = Query(
        default=None,
        ge=0,
        description="最高价格",
    ),

    # ── 排序 ──────────────────────────────────────────────────
    sort_by: SortBy = Query(
        default=SortBy.rating,   # 默认按评分排序
        description="按什么字段排序",
    ),
    order: SortOrder = Query(
        default=SortOrder.desc,  # 默认降序（分数高的在前）
        description="升序还是降序",
    ),

    # ── 分页 ──────────────────────────────────────────────────
    page: int = Query(
        default=1,
        ge=1,                    # 页码从 1 开始
        description="第几页",
    ),
    size: int = Query(
        default=20,
        ge=1,
        le=100,                  # 最多一页 100 条
        description="每页几条",
    ),
):
    """
    商品列表 — 完整的查询参数实战。

    组合示例:
      /products?category=electronics&sort_by=price&order=asc
      /products?keyword=键盘&page=1&size=3
      /products?min_price=100&max_price=500&sort_by=rating

    在 /docs 里试试不同的参数组合！
    """
    # ── 第 1 步: 过滤 ────────────────────────────────────────
    result = list(products_db)

    if category is not None:
        result = [p for p in result if p["category"] == category.value]
    if keyword is not None:
        result = [p for p in result if keyword.lower() in p["name"].lower()]
    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]
    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    # ── 第 2 步: 排序 ────────────────────────────────────────
    reverse_flag = (order == SortOrder.desc)
    result.sort(key=lambda p: p[sort_by.value], reverse=reverse_flag)

    # ── 第 3 步: 分页 ────────────────────────────────────────
    total = len(result)
    start_index = (page - 1) * size
    end_index = start_index + size
    page_data = result[start_index:end_index]

    # ── 返回结果 ──────────────────────────────────────────────
    return {
        "items": page_data,               # 当前页的数据
        "total": total,                   # 总共多少条
        "page": page,                     # 第几页
        "size": size,                     # 每页几条
        "pages": (total + size - 1) // size,  # 总共多少页（向上取整）
        "filters": {                      # 当前用的过滤条件
            "category": category.value if category else None,
            "keyword": keyword,
            "min_price": min_price,
            "max_price": max_price,
            "sort_by": sort_by.value,
            "order": order.value,
        },
    }


# ═══════════════════════════════════════════════════════════════
# 演示: 必填 vs 可选查询参数
# ═══════════════════════════════════════════════════════════════

@app.get("/search")
def search(
    q: str = Query(                 # ← 没有默认值 = 必填！
        ...,
        min_length=1,
        description="搜索关键词（必填）",
    ),
    limit: int = Query(             # ← 有默认值 = 可选
        default=10,
        ge=1,
        le=100,
    ),
):
    """
    演示必填和可选查询参数的区别。

    /search?q=Python           ✅
    /search?q=Python&limit=5   ✅
    /search                    ❌ 422（q 是必填的）
    """
    return {
        "query": q,
        "limit": limit,
        "message": f"搜索 '{q}'，返回前 {limit} 条",
    }


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn

    print("=" * 55)
    print("s03 — 接收参数")
    print("   访问 http://localhost:8000/docs")
    print("   重点看看 /products 的参数校验效果！")
    print("   试试传越界的参数值，看 422 错误")
    print("=" * 55)

    uvicorn.run(app, host="0.0.0.0", port=8000)
