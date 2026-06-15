"""文章路由 — /posts/*"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_session
from dependencies import get_current_user, Pagination
from models.user import UserModel
from models.post import PostModel
from schemas.post import PostCreate, PostResponse

router = APIRouter(
    prefix="/posts",
    tags=["文章管理"],
)


@router.get("/", response_model=list[PostResponse])
def list_posts(
    pagination: dict = Depends(Pagination(max_size=50)),
    session: Session = Depends(get_session),
):
    """公开 — 文章列表（不需要登录）"""
    return (
        session.query(PostModel)
        .offset(pagination["skip"])
        .limit(pagination["size"])
        .all()
    )


@router.post("/", response_model=PostResponse, status_code=201)
def create_post(
    post_in: PostCreate,
    user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """创建文章（需要登录）"""
    post = PostModel(
        title=post_in.title,
        content=post_in.content,
        author_id=user.id,
    )
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@router.patch("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post_in: PostCreate,
    user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """编辑文章（只有作者能编辑）"""
    post = session.get(PostModel, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="只能编辑自己的文章")
    post.title = post_in.title
    post.content = post_in.content
    session.commit()
    session.refresh(post)
    return post


@router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """删除文章（只有作者能删除）"""
    post = session.get(PostModel, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="只能删除自己的文章")
    session.delete(post)
    session.commit()


@router.get("/my", response_model=list[PostResponse])
def my_posts(
    user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """我的文章列表"""
    return session.query(PostModel).filter(PostModel.author_id == user.id).all()
