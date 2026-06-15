#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s13: RBAC 权限控制 — 管理员能删，用户只能看

═══════════════════════════════════════════════════════════════
学完本章你应该能回答:
  - 认证和授权有什么区别？
  - RBAC 的三个概念：User → Role → Permissions？
  - 怎么用 Depends 链实现权限检查？
  - require_role 和 require_permission 的区别？
═══════════════════════════════════════════════════════════════

启动:
    python s22_fastapi/s13_background_tasks/code.py
    然后访问 http://localhost:8000/docs
"""

from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# ═══════════════════════════════════════════════════════════════
# 权限与角色定义
# ═══════════════════════════════════════════════════════════════

class Permission(str, Enum):
    """系统所有权限点"""
    USERS_READ = "users:read"
    USERS_CREATE = "users:create"
    USERS_DELETE = "users:delete"
    POSTS_READ = "posts:read"
    POSTS_CREATE = "posts:create"
    POSTS_DELETE = "posts:delete"


class Role(str, Enum):
    """预定义角色"""
    ADMIN = "admin"
    EDITOR = "editor"
    USER = "user"


# 角色 → 权限映射
ROLE_PERMISSIONS = {
    Role.ADMIN: list(Permission),           # 管理员 = 全部权限
    Role.EDITOR: [                          # 编辑 = 文章管理 + 查看用户
        Permission.POSTS_READ,
        Permission.POSTS_CREATE,
        Permission.POSTS_DELETE,
        Permission.USERS_READ,
    ],
    Role.USER: [                            # 普通用户 = 只看文章
        Permission.POSTS_READ,
        Permission.POSTS_CREATE,
        Permission.USERS_READ,
    ],
}


def has_permission(role: Role, perm: Permission) -> bool:
    """检查角色是否有某权限"""
    return perm in ROLE_PERMISSIONS.get(role, [])


# ═══════════════════════════════════════════════════════════════
# JWT 配置（和 s12 一样）
# ═══════════════════════════════════════════════════════════════

SECRET_KEY = "s13-learning-secret"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# 数据库
engine = create_engine("sqlite:///s13_app.db", echo=False, connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default=Role.USER.value)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


def get_session():
    with Session(engine) as session:
        yield session


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


# ═══════════════════════════════════════════════════════════════
# 依赖: 认证 + 授权（三层依赖链）
# ═══════════════════════════════════════════════════════════════

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> User:
    """第 1 层: 认证 — 从 JWT 获取用户"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Token 无效")

    user = session.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    return user


def require_role(*roles: Role):
    """
    第 2 层: 角色检查（工厂函数）。

    用法:
      admin = Depends(require_role(Role.ADMIN))
      staff = Depends(require_role(Role.ADMIN, Role.EDITOR))
    """
    def checker(user: User = Depends(get_current_user)) -> User:
        user_role = Role(user.role)
        if user_role not in roles:
            allowed = " / ".join(r.value for r in roles)
            raise HTTPException(
                status_code=403,
                detail=f"需要 {allowed} 角色，当前角色: {user.role}",
            )
        return user
    return checker


def require_permission(permission: Permission):
    """
    第 3 层: 权限点检查（工厂函数）。

    用法:
      user = Depends(require_permission(Permission.USERS_DELETE))
    """
    def checker(user: User = Depends(get_current_user)) -> User:
        user_role = Role(user.role)
        if not has_permission(user_role, permission):
            raise HTTPException(
                status_code=403,
                detail=f"需要权限 {permission.value}，当前角色: {user.role}",
            )
        return user
    return checker


# ═══════════════════════════════════════════════════════════════
# App
# ═══════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    # 预创建三种角色的用户
    with Session(engine) as s:
        for name, pwd, role in [
            ("admin", "admin123", Role.ADMIN),
            ("editor", "editor123", Role.EDITOR),
            ("user", "user123", Role.USER),
        ]:
            if not s.query(User).filter(User.username == name).first():
                s.add(User(username=name, hashed_password=pwd_context.hash(pwd), role=role.value))
        s.commit()
    yield


app = FastAPI(
    title="s13 - RBAC 权限控制",
    description="认证 = 你是谁 | 授权 = 你能做什么",
    version="13.0.0",
    lifespan=lifespan,
)


# ═══════════════════════════════════════════════════════════════
# 接口
# ═══════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {
        "message": "s13 — RBAC 权限控制",
        "测试账号": "admin/admin123 | editor/editor123 | user/user123",
        "试试": "用不同账号登录后访问不同接口",
        "文档": "/docs",
    }


@app.post("/auth/login", response_model=TokenResponse)
def login(username: str, password: str, session=Depends(get_session)):
    """登录"""
    user = session.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {"sub": str(user.id), "username": user.username, "role": user.role, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return TokenResponse(access_token=token, role=user.role)


@app.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return user


@app.get("/my-permissions")
def my_permissions(user: User = Depends(get_current_user)):
    role = Role(user.role)
    return {"role": role.value, "permissions": [p.value for p in ROLE_PERMISSIONS[role]]}


# ── 需要特定权限的接口 ────────────────────────────────────────

@app.delete("/admin/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    admin: User = Depends(require_permission(Permission.USERS_DELETE)),
    session: Session = Depends(get_session),
):
    """删除用户 — 需要 users:delete 权限"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    session.delete(user)
    session.commit()


@app.get("/admin/dashboard")
def dashboard(
    user: User = Depends(require_role(Role.ADMIN, Role.EDITOR)),
    session: Session = Depends(get_session),
):
    """管理员/编辑仪表盘"""
    return {
        "total_users": session.query(User).count(),
        "accessible_by": "admin 和 editor",
    }


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    print("=" * 55)
    print("s13 — RBAC 权限控制")
    print("   访问 http://localhost:8000/docs")
    print("   用 user/user123 登录 → GET /admin/dashboard → 403")
    print("   用 admin/admin123 登录 → GET /admin/dashboard → 成功")
    print("=" * 55)
    uvicorn.run(app, host="0.0.0.0", port=8000)
