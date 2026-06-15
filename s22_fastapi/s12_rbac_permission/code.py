#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s12: JWT 认证 — 登录拿 token，访问带 token

═══════════════════════════════════════════════════════════════
学完本章你应该能回答:
  - JWT 的三个部分分别是什么？
  - 怎么用 bcrypt 哈希和验证密码？
  - OAuth2PasswordBearer 做了什么？
  - Access Token 和 Refresh Token 有什么区别？
═══════════════════════════════════════════════════════════════

依赖安装:
    pip install python-jose[cryptography] passlib[bcrypt]

启动:
    python s22_fastapi/s12_rbac_permission/code.py
    然后访问 http://localhost:8000/docs
    点右上角 🔓 Authorize，输入 token
"""

from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import create_engine, String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# ═══════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════
# 生产环境这些必须从环境变量读取！
SECRET_KEY = "s12-learning-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# ═══════════════════════════════════════════════════════════════
# 密码哈希
# ═══════════════════════════════════════════════════════════════
# bcrypt 是目前最安全的密码哈希算法之一。
# 它自带"盐"（salt），相同的密码每次哈希结果都不一样。
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """密码 → 哈希值（不可逆）"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码是否匹配哈希值"""
    return pwd_context.verify(plain_password, hashed_password)


# ═══════════════════════════════════════════════════════════════
# 数据库
# ═══════════════════════════════════════════════════════════════

engine = create_engine(
    "sqlite:///s12_app.db",
    echo=False,
    connect_args={"check_same_thread": False},
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


def get_session():
    with Session(engine) as session:
        yield session


# ═══════════════════════════════════════════════════════════════
# Pydantic Schema
# ═══════════════════════════════════════════════════════════════

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒


# ═══════════════════════════════════════════════════════════════
# JWT 工具函数
# ═══════════════════════════════════════════════════════════════

def create_access_token(user_id: int, username: str) -> str:
    """生成 Access Token（短有效期）"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),     # subject — 主体（用户 ID）
        "username": username,
        "type": "access",
        "exp": expire,           # expiration — 过期时间
    }
    # 用密钥签名生成 JWT 字符串
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: int, username: str) -> str:
    """生成 Refresh Token（长有效期）"""
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "username": username,
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str, expected_type: str = "access") -> dict:
    """
    解码并验证 JWT。

    验证: 签名是否正确？是否过期？type 是否匹配？
    如果验证失败 → 抛 HTTPException(401)。
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != expected_type:
            raise HTTPException(status_code=401, detail="Token 类型不匹配")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token 无效或已过期")


# ═══════════════════════════════════════════════════════════════
# OAuth2 方案
# ═══════════════════════════════════════════════════════════════
# OAuth2PasswordBearer 是一个 FastAPI 内置的"安全方案"。
# 它做了两件事:
#   1. 从 Authorization: Bearer xxx 中提取 token
#   2. 在 /docs 里加一个 🔓 Authorize 按钮

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    description="输入从 /auth/login 获取的 access_token",
)


# ═══════════════════════════════════════════════════════════════
# 依赖: 获取当前用户
# ═══════════════════════════════════════════════════════════════

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> User:
    """
    从 JWT 中获取当前用户 — 最核心的认证依赖。

    流程:
      1. oauth2_scheme 从 Header 提取 token
      2. jwt.decode 验证签名和有效期
      3. 从数据库查用户
      4. 返回 User 对象（或 401）
    """
    payload = decode_token(token, expected_type="access")
    user_id = int(payload["sub"])

    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="用户已被禁用")
    return user


# ═══════════════════════════════════════════════════════════════
# FastAPI App
# ═══════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="s12 - JWT 认证",
    description="登录拿 token，访问带 token — 注册/登录/Token 刷新",
    version="12.0.0",
    lifespan=lifespan,
)


# ═══════════════════════════════════════════════════════════════
# 认证路由
# ═══════════════════════════════════════════════════════════════

@app.post("/auth/register", response_model=UserResponse, status_code=201)
def register(user_in: UserRegister, session: Session = Depends(get_session)):
    """注册 — 密码加盐哈希后存储（不存明文！）"""
    # 检查唯一性
    if session.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=409, detail="用户名已存在")
    if session.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=409, detail="邮箱已被注册")

    # 创建用户（密码已哈希）
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),  # ← 哈希！
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.post("/auth/login", response_model=TokenResponse)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
):
    """
    登录 — 验证用户名密码，返回 JWT。

    OAuth2PasswordRequestForm 期望的是 application/x-www-form-urlencoded 格式
    （和 HTML 表单一样），不是 JSON 格式。

    在 /docs 里这个接口使用起来就像填一个登录表单。
    """
    # 查用户
    user = session.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 签发 token
    return TokenResponse(
        access_token=create_access_token(user.id, user.username),
        refresh_token=create_refresh_token(user.id, user.username),
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@app.post("/auth/refresh", response_model=TokenResponse)
def refresh_token(refresh_token: str):
    """用 Refresh Token 换新的 Access Token"""
    payload = decode_token(refresh_token, expected_type="refresh")
    return TokenResponse(
        access_token=create_access_token(int(payload["sub"]), payload["username"]),
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ═══════════════════════════════════════════════════════════════
# 受保护的接口
# ═══════════════════════════════════════════════════════════════

@app.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    """获取当前用户 — 只需要 Depends(get_current_user)"""
    return user


@app.get("/protected")
def protected(user: User = Depends(get_current_user)):
    """任何登录用户都能访问"""
    return {
        "message": f"你好 {user.username}，你已通过认证",
        "user_id": user.id,
    }


@app.get("/")
def root():
    return {
        "message": "s12 — JWT 认证",
        "流程": [
            "1. POST /auth/register — 注册",
            "2. POST /auth/login    — 登录，获取 token",
            "3. 在 /docs 右上角 🔓 Authorize 输入 token",
            "4. GET /me              — 你的信息",
            "5. GET /protected       — 受保护的接口",
        ],
        "文档": "/docs",
    }


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    print("=" * 55)
    print("s12 — JWT 认证")
    print("   访问 http://localhost:8000/docs")
    print("   1. POST /auth/register 注册账号")
    print("   2. POST /auth/login 获取 token")
    print("   3. 点 🔓 Authorize 输入 token")
    print("   4. 然后访问 GET /me → 成功！")
    print("=" * 55)
    uvicorn.run(app, host="0.0.0.0", port=8000)
