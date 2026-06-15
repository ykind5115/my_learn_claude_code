#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s07: Repository 模式 — 把数据库操作封装成可复用的类

═══════════════════════════════════════════════════════════════
学完本章你应该能回答:
  - 为什么要用 Repository 模式？（不直接在路由里写 SQL）
  - Repository 的核心方法有哪些？
  - 怎么让路由函数通过 Depends() 获取 Repository？
  - 三层结构：路由层 → 仓库层 → 模型层 各管什么？
═══════════════════════════════════════════════════════════════

和 s06 的区别:
  s06: 路由函数直接操作 session.query(User)...
  s07: 路由函数调用 repo.get() / repo.list() / repo.create()
       数据库逻辑集中在 Repository 类里
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, String, Integer, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# ═══════════════════════════════════════════════════════════════
# 数据库基础设施（和 s06 完全一样）
# ═══════════════════════════════════════════════════════════════

engine = create_engine(
    "sqlite:///s07_app.db",
    echo=False,
    connect_args={"check_same_thread": False},
)


class Base(DeclarativeBase):
    pass


def get_session():
    with Session(engine) as session:
        yield session


# ═══════════════════════════════════════════════════════════════
# ORM 模型
# ═══════════════════════════════════════════════════════════════

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    age: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"


# ═══════════════════════════════════════════════════════════════
# Pydantic Schema
# ═══════════════════════════════════════════════════════════════

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    age: int = Field(..., ge=0, le=150)


class UserUpdate(BaseModel):
    """更新用的 Schema — 所有字段可选（PATCH 语义）"""
    name: str | None = Field(None, min_length=1, max_length=50)
    email: str | None = Field(None, min_length=5, max_length=100)
    age: int | None = Field(None, ge=0, le=150)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int
    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════
# ★ 重点: UserRepository — 封装所有 User 数据访问逻辑
# ═══════════════════════════════════════════════════════════════

class UserRepository:
    """
    User 表的 Repository — 所有用户相关的数据库操作都在这里。

    为什么叫 "Repository"？
      来自 Martin Fowler 的《企业应用架构模式》—
      一个在内存对象和数据库之间的中介层。

    职责:
      - 只有数据库操作（查询、插入、更新、删除）
      - 不处理 HTTP 协议（不关心状态码、不关心 JSON）
      - 不处理业务逻辑（不计算年龄、不发送邮件）
    """

    def __init__(self, session: Session):
        """
        构造函数 — 接收一个数据库 Session。

        为什么不在 __init__ 里创建 session？
          每个 HTTP 请求有独立的 session，所以 session 从外面传进来。
        """
        self.session = session

    # ── 查询方法 ──────────────────────────────────────────────

    def get(self, user_id: int) -> User | None:
        """按主键查询 — 可能返回 None"""
        return self.session.get(User, user_id)

    def get_or_404(self, user_id: int) -> User:
        """按主键查询 — 不存在就抛 HTTPException(404)"""
        user = self.get(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")
        return user

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        min_age: int | None = None,
    ) -> list[User]:
        """
        列表查询 — 支持分页和过滤。

        用法:
          repo.list()                          → 全部
          repo.list(skip=10, limit=10)          → 第 2 页
          repo.list(min_age=18)                 → 过滤成年人
        """
        query = self.session.query(User)

        if min_age is not None:
            query = query.filter(User.age >= min_age)

        return query.offset(skip).limit(limit).all()

    def find_by_email(self, email: str) -> User | None:
        """按邮箱查询 — 用于唯一性检查"""
        return self.session.query(User).filter(User.email == email).first()

    def count(self) -> int:
        """用户总数"""
        return self.session.query(User).count()

    # ── 创建方法 ──────────────────────────────────────────────

    def create(self, name: str, email: str, age: int = 0) -> User:
        """
        创建用户。

        参数:
          name: 用户名
          email: 邮箱（会检查唯一性）
          age: 年龄
        """
        # 先检查邮箱是否已存在
        if self.find_by_email(email):
            raise HTTPException(status_code=409, detail="邮箱已被注册")

        user = User(name=name, email=email, age=age)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    # ── 更新方法 ──────────────────────────────────────────────

    def update(self, user_id: int, **kwargs) -> User:
        """
        部分更新 — 只更新传入的字段。

        用法:
          repo.update(1, name="新名字")              → 只改 name
          repo.update(1, name="新", age=30)          → 改 name 和 age

        kwargs 是一个 dict，包含所有传入的字段名和值。
        比如调用 update(1, name="张三", age=30):
          kwargs = {"name": "张三", "age": 30}
        """
        user = self.get_or_404(user_id)

        # 遍历所有要更新的字段
        for field_name, field_value in kwargs.items():
            if field_value is not None:  # 只更新实际传了的字段
                setattr(user, field_name, field_value)
                # setattr(obj, "name", "张三") 等价于 obj.name = "张三"
                # 但可以动态设置属性名

        self.session.commit()
        self.session.refresh(user)
        return user

    # ── 删除方法 ──────────────────────────────────────────────

    def delete(self, user_id: int) -> User:
        """删除用户 — 返回被删除的用户对象"""
        user = self.get_or_404(user_id)
        self.session.delete(user)
        self.session.commit()
        return user


# ═══════════════════════════════════════════════════════════════
# FastAPI 依赖: 获取 Repository 实例
# ═══════════════════════════════════════════════════════════════

def get_user_repo(session: Session = Depends(get_session)) -> UserRepository:
    """
    为每个请求创建一个 UserRepository 实例。

    依赖链:
      请求进来 → get_session() 创建 session
               → get_user_repo(session) 创建 UserRepository
               → 路由函数拿到 repo
               → 请求结束 → session 自动关闭
    """
    return UserRepository(session)


# ═══════════════════════════════════════════════════════════════
# FastAPI App
# ═══════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="s07 - Repository 模式",
    description="增删改查的标准套路 — 把数据库操作封装成可复用的类",
    version="7.0.0",
    lifespan=lifespan,
)


# ═══════════════════════════════════════════════════════════════
# 接口 — 注意这些函数有多么简洁！
# ═══════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {
        "message": "s07 — Repository 模式",
        "核心": "路由函数只调用 repo.xxx() — 没有一行 SQL",
        "对比": "回头看看 s06 的代码，感受封装的威力",
        "文档": "http://localhost:8000/docs",
    }


@app.post("/users", status_code=201, response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    repo: UserRepository = Depends(get_user_repo),
):
    """
    创建用户 — 一行搞定数据库操作。

    对比 s06 的创建:
      s06: 手动建 User 对象 → add → commit → refresh（4 步）
      s07: repo.create(name=..., email=...) → 1 步
    """
    return repo.create(
        name=user_in.name,
        email=user_in.email,
        age=user_in.age,
    )


@app.get("/users", response_model=list[UserResponse])
def list_users(
    page: int = 1,
    size: int = 20,
    min_age: int | None = None,
    repo: UserRepository = Depends(get_user_repo),
):
    """用户列表 — 分页和过滤都在 Repository 里处理"""
    skip = (page - 1) * size
    return repo.list(skip=skip, limit=size, min_age=min_age)


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    repo: UserRepository = Depends(get_user_repo),
):
    """获取单个用户 — get_or_404 自动处理不存在的情况"""
    return repo.get_or_404(user_id)


@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    repo: UserRepository = Depends(get_user_repo),
):
    """
    更新用户 — model_dump(exclude_unset=True) 只取传了的字段。

    如果客户端发 {"name": "新名字"}:
      user_in.model_dump(exclude_unset=True) → {"name": "新名字"}
      （age 和 email 不会出现在字典里）
    """
    update_data = user_in.model_dump(exclude_unset=True)
    return repo.update(user_id, **update_data)


@app.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    repo: UserRepository = Depends(get_user_repo),
):
    """删除用户"""
    repo.delete(user_id)


@app.get("/stats")
def stats(repo: UserRepository = Depends(get_user_repo)):
    """统计 — 演示 Repository 可以扩展任意查询"""
    return {
        "total_users": repo.count(),
    }


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    print("=" * 55)
    print("s07 — Repository 模式")
    print("   访问 http://localhost:8000/docs")
    print("   注意路由函数多么简洁 — 没有一行 SQL！")
    print("   对比 s06 的代码，理解封装的价值")
    print("=" * 55)
    uvicorn.run(app, host="0.0.0.0", port=8000)
