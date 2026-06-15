"""用户路由 — /users/*"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_session
from dependencies import get_current_user, require_admin, Pagination
from models.user import UserModel
from schemas.user import UserResponse

router = APIRouter(
    prefix="/users",
    tags=["用户管理"],
)


@router.get("/me", response_model=UserResponse)
def get_me(user: UserModel = Depends(get_current_user)):
    """获取当前用户信息"""
    return user


@router.get("/", response_model=list[UserResponse])
def list_users(
    pagination: dict = Depends(Pagination()),
    session: Session = Depends(get_session),
    _admin: UserModel = Depends(require_admin),
):
    """管理员 — 查看所有用户"""
    return (
        session.query(UserModel)
        .offset(pagination["skip"])
        .limit(pagination["size"])
        .all()
    )


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    _admin: UserModel = Depends(require_admin),
):
    """管理员 — 删除用户"""
    user = session.get(UserModel, user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="用户不存在")
    session.delete(user)
    session.commit()
