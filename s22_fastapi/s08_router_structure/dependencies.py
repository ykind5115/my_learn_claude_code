"""公共依赖 — 所有路由模块共用的 Depends 函数"""

from fastapi import Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from typing import Annotated

from database import get_session
from models.user import UserModel


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    session: Session = Depends(get_session),
) -> UserModel:
    """
    从 Authorization header 获取当前用户。

    s08 简化版 — 只验证 token 格式，不做真正的 JWT 解密。
    真正的 JWT 认证在 s11。
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="请提供 Authorization header")

    token = authorization.removeprefix("Bearer ").strip()

    # 简化: token 就是 username
    user = session.query(UserModel).filter(UserModel.username == token).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Token 无效")

    return user


def require_admin(
    user: UserModel = Depends(get_current_user),
) -> UserModel:
    """要求管理员角色"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


class Pagination:
    """分页依赖"""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size

    def __call__(
        self,
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1),
    ):
        if size > self.max_size:
            size = self.max_size
        return {
            "page": page,
            "size": size,
            "skip": (page - 1) * size,
        }
