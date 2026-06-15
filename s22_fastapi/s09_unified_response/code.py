#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s09: APIRouter 路由拆分演示

这个文件展示了"拆分前"的样子（所有路由在一个文件）。

具体的拆分实践见:
  s22_fastapi/s08_router_structure/   ← 完整的拆分项目结构
  (main.py, database.py, dependencies.py, models/, schemas/, routers/)

本文件用一个简化的例子演示 APIRouter 的核心语法。

启动:
    python s22_fastapi/s09_unified_response/code.py
    然后访问 http://localhost:8000/docs — 注意 tags 分组效果！
"""

from fastapi import FastAPI, APIRouter

# ═══════════════════════════════════════════════════════════════
# 第 1 步: 按业务领域创建 Router
# ═══════════════════════════════════════════════════════════════
# 每个 Router 就像一个"迷你 FastAPI 应用"
# 可以有自己的 prefix、tags、dependencies

# 用户路由
user_router = APIRouter(
    prefix="/users",
    tags=["👤 用户"],
)

# 文章路由
post_router = APIRouter(
    prefix="/posts",
    tags=["📝 文章"],
)

# 管理路由（管理员专用）
admin_router = APIRouter(
    prefix="/admin",
    tags=["🔧 管理"],
    # dependencies=[Depends(require_admin)],  ← 可以给整个模块加依赖
)


# ═══════════════════════════════════════════════════════════════
# 第 2 步: 在各个 Router 上注册路由
# ═══════════════════════════════════════════════════════════════

@user_router.get("/")
def list_users():
    """实际路径: GET /users/（prefix 自动加上）"""
    return [{"id": 1, "name": "张三"}, {"id": 2, "name": "李四"}]


@user_router.get("/{user_id}")
def get_user(user_id: int):
    """实际路径: GET /users/{user_id}"""
    return {"id": user_id, "name": "张三"}


@user_router.post("/", status_code=201)
def create_user(name: str):
    """实际路径: POST /users/"""
    return {"id": 3, "name": name, "message": "创建成功"}


@post_router.get("/")
def list_posts():
    """实际路径: GET /posts/"""
    return [{"id": 1, "title": "FastAPI 学习笔记"}]


@post_router.post("/", status_code=201)
def create_post(title: str):
    """实际路径: POST /posts/"""
    return {"id": 2, "title": title}


@admin_router.get("/dashboard")
def admin_dashboard():
    """实际路径: GET /admin/dashboard"""
    return {"stats": {"users": 100, "posts": 500}}


# ═══════════════════════════════════════════════════════════════
# 第 3 步: 组装到主应用
# ═══════════════════════════════════════════════════════════════

app = FastAPI(
    title="s09 - APIRouter 路由拆分",
    description="每个 Router 独立管理自己的路由，主应用只负责组装",
    version="9.0.0",
)

# 像乐高积木一样插上各个模块
app.include_router(user_router)
app.include_router(post_router)
app.include_router(admin_router)


@app.get("/")
def root():
    return {
        "message": "s09 — APIRouter 路由拆分",
        "概念": "每个业务领域一个 Router，主应用只 include",
        "打开 /docs": "注意 tags 分组 — 用户/文章/管理 各一组",
        "try": [
            "GET /users/",
            "GET /posts/",
            "GET /admin/dashboard",
        ],
    }


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    print("=" * 55)
    print("s09 — APIRouter 路由拆分")
    print("   访问 http://localhost:8000/docs")
    print("   注意 Swagger UI 里的 tags 分组！")
    print("   每个 Router 的接口自动归到一组")
    print("=" * 55)
    uvicorn.run(app, host="0.0.0.0", port=8000)
