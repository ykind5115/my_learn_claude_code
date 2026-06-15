#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s08: 依赖注入 — Depends() 深入

═══════════════════════════════════════════════════════════════
学完本章你应该能回答:
  - Depends() 到底做了什么？
  - 依赖链是怎么递归解析的？
  - Depends 的三种形态：函数、类、yield 各什么时候用？
  - 怎么用 Depends 链实现认证授权？
═══════════════════════════════════════════════════════════════

启动:
    python s22_fastapi/s08_router_structure/main.py
    然后访问 http://localhost:8000/docs
"""

import hashlib
import secrets
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, Header, Query
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# ═══════════════════════════════════════════════════════════════
# 数据库
# ═══════════════════════════════════════════════════════════════

engine = create_engine(
    "sqlite:///s08_app.db",
    echo=False,
    connect_args={"check_same_thread": False},
)


class Base(DeclarativeBase):
    pass


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(String(5000), default="")
    author_id: Mapped[int] = mapped_column(Integer, nullable=False)


# Pydantic Schema
class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(default="", max_length=5000)


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════
# 依赖函数 — 从简单到复杂
# ═══════════════════════════════════════════════════════════════

# ── 层级 0: 数据库会话 ──────────────────────────────────────

def get_session():
    """最底层的依赖 — 提供数据库会话"""
    with Session(engine) as session:
        yield session  # 请求结束后自动关闭


# ── 层级 1: 认证（模拟） ────────────────────────────────────
# 真实项目用 JWT（s12），这里用简化的 token 做概念演示

# 模拟 token 存储
_token_store: dict[str, dict] = {}


def create_token(user_id: int, name: str, role: str) -> str:
    """生成一个 token（模拟 JWT）"""
    token = secrets.token_hex(16)
    _token_store[token] = {"user_id": user_id, "name": name, "role": role}
    return token


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> dict:
    """
    依赖: 从 HTTP Header 中提取当前用户信息。

    Header("Authorization") — FastAPI 自动从请求头中提取。
    客户端需要带: Authorization: Bearer <token>

    这个依赖不访问数据库 — 因为它不需要。
    返回一个 dict，包含 user_id, name, role。
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="请提供 Authorization header")

    token = authorization.removeprefix("Bearer ").strip()
    user_data = _token_store.get(token)

    if user_data is None:
        raise HTTPException(status_code=401, detail="Token 无效或已过期")

    return user_data  # {"user_id": 1, "name": "张三", "role": "admin"}


# ── 层级 2: 权限检查 ────────────────────────────────────────

def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """
    叠在 get_current_user 之上的依赖 — 要求管理员角色。

    依赖链: Header → get_current_user → require_admin → 路由函数

    如果用户不是 admin，直接抛 403。
    """
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


# ── 层级 2: 分页参数（类依赖） ───────────────────────────────

class Pagination:
    """
    可参数化的依赖 — 不同接口可以有不同的分页上限。

    用法:
      Depends(Pagination())           → max_size=100
      Depends(Pagination(max_size=50)) → max_size=50
    """

    def __init__(self, max_size: int = 100):
        self.max_size = max_size

    def __call__(
        self,
        page: int = Query(default=1, ge=1, description="页码"),
        size: int = Query(default=20, ge=1, description="每页数量"),
    ) -> dict:
        if size > self.max_size:
            size = self.max_size
        return {
            "page": page,
            "size": size,
            "skip": (page - 1) * size,
        }


# ═══════════════════════════════════════════════════════════════
# FastAPI App
# ═══════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="s08 - 依赖注入",
    description="Depends() 深入 — 依赖链、类依赖、认证链",
    version="8.0.0",
    lifespan=lifespan,
)


# ═══════════════════════════════════════════════════════════════
# 接口
# ═══════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {
        "message": "s08 — 依赖注入 Depends()",
        "demo_accounts": {
            "admin_token": "先用 POST /auth/login?username=admin 获取",
            "user_token": "先用 POST /auth/login?username=user 获取",
        },
        "文档": "http://localhost:8000/docs",
    }


# ── 登录接口 ──────────────────────────────────────────────────

@app.post("/auth/login")
def login(username: str, role: str = "user"):
    """
    模拟登录 — 返回一个 token。

    role 参数: admin / user（实际项目从数据库查）
    """
    user_id = hash(username) % 10000
    token = create_token(user_id=user_id, name=username, role=role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"name": username, "role": role},
        "usage": f"在 /docs 右上角点 🔓 Authorize，输入: Bearer {token}",
    }


# ── 公开接口（不需要登录） ────────────────────────────────────

@app.get("/posts", response_model=list[PostResponse])
def list_posts(
    session: Session = Depends(get_session),
    pagination: dict = Depends(Pagination(max_size=50)),
):
    """公开接口 — 不需要登录，但用了分页依赖"""
    return (
        session.query(Post)
        .offset(pagination["skip"])
        .limit(pagination["size"])
        .all()
    )


# ── 需要登录的接口 ────────────────────────────────────────────

@app.get("/me")
def get_me(user: dict = Depends(get_current_user)):
    """
    获取当前用户信息 — 只需要一个 Depends(get_current_user)。

    不需要 session、不需要手动解析 Header —
    依赖函数已经帮你做完了这一切。
    """
    return {
        "message": "这是你的个人信息",
        "user": user,
    }


@app.post("/posts", status_code=201, response_model=PostResponse)
def create_post(
    post_in: PostCreate,
    user: dict = Depends(get_current_user),  # ← 认证
    session: Session = Depends(get_session),  # ← 数据库
):
    """
    创建文章 — 同时用了两个依赖。

    依赖间互不影响，FastAPI 并行解析它们。
    """
    post = Post(
        title=post_in.title,
        content=post_in.content,
        author_id=user["user_id"],
    )
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


# ── 管理员专用 ────────────────────────────────────────────────

@app.get("/admin/dashboard")
def admin_dashboard(
    admin: dict = Depends(require_admin),  # ← 依赖链自动执行
):
    """
    管理员仪表盘 — 三层依赖链。

    执行顺序:
      Header("Authorization")
      → get_current_user (解析 token)
      → require_admin (检查角色)
      → admin_dashboard (你的业务逻辑)
    """
    return {
        "message": f"欢迎管理员 {admin['name']}",
        "stats": {"total_users": 100, "total_posts": 500},
    }


@app.get("/admin/users")
def admin_users(
    admin: dict = Depends(require_admin),
    pagination: dict = Depends(Pagination(max_size=200)),
    # ↑ 管理员可以看到更多数据（max_size=200）
):
    """管理员用户列表 — 不同的分页上限"""
    return {
        "admin": admin["name"],
        "pagination": pagination,
        "note": "这里会展示所有用户（实际实现略）",
    }


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    print("=" * 55)
    print("s08 — 依赖注入 Depends()")
    print("   访问 http://localhost:8000/docs")
    print("   1. POST /auth/login?username=admin&role=admin")
    print("   2. 在 /docs 右上角点 🔓 Authorize 输入 token")
    print("   3. 试试 GET /me → 成功")
    print("   4. 试试 GET /admin/dashboard → 只有 admin 能访问")
    print("=" * 55)
    uvicorn.run(app, host="0.0.0.0", port=8000)
