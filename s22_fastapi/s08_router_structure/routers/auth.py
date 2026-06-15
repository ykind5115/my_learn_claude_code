"""认证路由 — /auth/*"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_session
from models.user import UserModel
from schemas.user import UserCreate, UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["认证"],
)


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    """注册新用户"""
    existing = session.query(UserModel).filter(UserModel.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="用户名已存在")
    user = UserModel(username=user_in.username, role=user_in.role)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login")
def login(username: str, session: Session = Depends(get_session)):
    """登录 — 简化版（s11 换成 JWT）"""
    user = session.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return {
        "access_token": user.username,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "role": user.role},
    }
