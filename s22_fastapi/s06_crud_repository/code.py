#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s06: 数据库入门 — SQLAlchemy + SQLite

═══════════════════════════════════════════════════════════════
学完本章你应该能回答:
  - 为什么不能一直用内存列表存数据？
  - ORM 是什么？它解决了什么问题？
  - SQLAlchemy 的 engine / Base / Session 分别干什么？
  - 怎么定义 ORM 模型（一张表）？
  - CRUD 四个操作分别怎么写？
═══════════════════════════════════════════════════════════════

启动:
    python s22_fastapi/s06_crud_repository/code.py
    然后访问 http://localhost:8000/docs

    数据库文件: s06_app.db（自动创建在项目根目录）
    这个文件就是你的数据库！删了它 → 数据全没
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import (
    create_engine,
    String,
    Integer,
    Float,
    Boolean,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    Session,
)

# ═══════════════════════════════════════════════════════════════
# 第 1 步: 创建数据库引擎
# ═══════════════════════════════════════════════════════════════
# 引擎 = 数据库的"连接工厂"。
# 你告诉它数据库文件在哪，它负责实际读写文件。

# sqlite:///  →  使用 SQLite 数据库
# s06_app.db  →  数据库文件名（在项目根目录下）
# 如果文件不存在，SQLite 会自动创建它
DATABASE_URL = "sqlite:///s06_app.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,   # ← True = 打印每条 SQL 语句（新手建议开着，理解 ORM 怎么工作的）
    connect_args={"check_same_thread": False},
    # ↑ SQLite 的特殊参数：允许不同线程访问同一个数据库文件
    #   生产环境用 PostgreSQL 不需要这个
)


# ═══════════════════════════════════════════════════════════════
# 第 2 步: 创建 ORM 基类
# ═══════════════════════════════════════════════════════════════
# 所有数据库表的 Python 类都要继承这个 Base。
# Base 内部维护了一个"注册表"，记录了所有继承它的子类。
# create_all() 时会遍历这个注册表来建表。

class Base(DeclarativeBase):
    pass


# ═══════════════════════════════════════════════════════════════
# 第 3 步: 定义 ORM 模型（数据库表）
# ═══════════════════════════════════════════════════════════════
#
# 规则:
#   class 类名(Base):            # 继承 Base
#       __tablename__ = "表名"    # Python 类名和数据库表名可以不同
#       字段名: Mapped[类型] = mapped_column(列类型, 约束...)
#
# Mapped[int]       ← Python 类型提示（给 IDE 和类型检查器看的）
# mapped_column()   ← 数据库列的实际定义（给 SQLAlchemy 看的）
# 两者要匹配（都是 int、都是 str 等）


class User(Base):
    """
    用户表 — 一个 Python 类 = 一张数据库表。

    这个类对应的 SQL（自动生成的）:
        CREATE TABLE users (
            id INTEGER NOT NULL,
            name VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL,
            age INTEGER NOT NULL,
            is_active BOOLEAN NOT NULL,
            PRIMARY KEY (id),
            UNIQUE (email)
        );
    """
    __tablename__ = "users"      # 数据库里的表名

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,        # 主键 — 唯一标识每一行
        autoincrement=True,      # 自动递增（1, 2, 3...）
        index=True,              # 建索引 — 按 id 查询更快
    )
    name: Mapped[str] = mapped_column(
        String(50),              # 数据库类型: VARCHAR(50)
        nullable=False,          # 不允许为空
    )
    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,             # 唯一约束 — 不能有两个相同的邮箱
        nullable=False,
    )
    age: Mapped[int] = mapped_column(
        Integer,
        default=0,               # 默认值
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,            # 默认激活
    )

    def __repr__(self):
        """控制 print(user) 时显示什么"""
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


class Product(Base):
    """
    商品表 — 另一个表，展示不同字段类型。
    """
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"


# ═══════════════════════════════════════════════════════════════
# 第 4 步: Session 工厂（给 FastAPI 用）
# ═══════════════════════════════════════════════════════════════

def get_session():
    """
    为每个 HTTP 请求创建一个数据库会话。

    with Session(engine) as session:
        yield session   ← 请求处理时 session 可用
        # yield 后面的代码在请求结束后执行
        # with 块退出时自动关闭 session

    Depends(get_session) 会让 FastAPI 每个请求自动调用这个函数。
    """
    with Session(engine) as session:
        yield session


# ═══════════════════════════════════════════════════════════════
# 第 5 步: Pydantic Schema（API 层 — 和 ORM 模型不同！）
# ═══════════════════════════════════════════════════════════════
# 注意: 这些是 Pydantic BaseModel（API 层），
# 上面的 User 和 Product 是 SQLAlchemy Base（数据库层）。
# 它们是不同的类，有不同的父类，有不同的用途。

class UserCreate(BaseModel):
    """创建用户的请求体"""
    name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    age: int = Field(..., ge=0, le=150)


class UserResponse(BaseModel):
    """
    用户响应。

    注意 model_config:
      from_attributes=True 告诉 Pydantic: "这个模型可以从 ORM 对象创建"
      这样就能把 User（ORM 对象）直接传给 UserResponse 了。
    """
    id: int
    name: str
    email: str
    age: int
    is_active: bool

    model_config = {"from_attributes": True}
    # ↑ 关键配置！有了它才能 user_response = UserResponse.model_validate(orm_user)


class ProductCreate(BaseModel):
    """创建商品的请求体"""
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)


class ProductResponse(BaseModel):
    """商品响应"""
    id: int
    name: str
    price: float
    stock: int
    is_available: bool
    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════
# 第 6 步: FastAPI 应用 + 启动时建表
# ═══════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用启动时自动建表。

    create_all() 会检查 Base 的所有子类，
    为每张表生成 CREATE TABLE 语句（如果表还不存在）。
    表已存在 → 跳过，不会重复创建。
    """
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表已就绪（如果尚不存在，已自动创建）")
    yield


app = FastAPI(
    title="s06 - 数据库入门",
    description="第一次学数据库：SQLite + SQLAlchemy 基础 CRUD",
    version="6.0.0",
    lifespan=lifespan,
)


# ═══════════════════════════════════════════════════════════════
# 接口：用户 CRUD
# ═══════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {
        "message": "s06 — 数据库入门",
        "概念": "ORM = 用 Python 类操作数据库表",
        "数据库文件": "s06_app.db（在当前目录）",
        "试试": [
            "POST /users → 创建用户 → 观察终端里打印的 SQL",
            "GET /users  → 查询列表",
            "GET /users/1 → 查单个",
            "PATCH /users/1 → 更新",
            "DELETE /users/1 → 删除",
            "重启服务器 → 数据还在！",
        ],
        "文档": "http://localhost:8000/docs",
    }


# ── Create — 创建用户 ──────────────────────────────────────

@app.post("/users", status_code=201, response_model=UserResponse)
def create_user(user_in: UserCreate, session: Session = Depends(get_session)):
    """
    创建用户。

    流程:
      1. 客户端发来的 JSON → Pydantic UserCreate 校验
      2. 检查邮箱是否已存在
      3. UserCreate 数据 → ORM User 对象
      4. session.add(user) — 加入待插入列表
      5. session.commit() — 写入数据库
      6. session.refresh(user) — 获取数据库生成的 id
      7. ORM User 对象 → Pydantic UserResponse（from_attributes）
    """
    # 检查邮箱唯一性
    existing = session.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="邮箱已被注册")

    # 创建 ORM 对象（Python 对象 → 数据库行）
    user = User(
        name=user_in.name,
        email=user_in.email,
        age=user_in.age,
    )
    session.add(user)        # 加入待办列表
    session.commit()          # 写入数据库（观察终端里的 INSERT 语句！）
    session.refresh(user)     # 刷新 — 获取数据库生成的 id

    return user               # FastAPI 用 UserResponse(from_attributes=True) 转换


# ── Read — 查询用户列表 ──────────────────────────────────────

@app.get("/users", response_model=list[UserResponse])
def list_users(
    session: Session = Depends(get_session),
    active_only: bool = False,
    min_age: int | None = None,
):
    """
    查询用户列表，支持过滤。

    SQLAlchemy 的查询是链式调用:
      query.filter(A).filter(B).order_by(C).limit(10)
      等价于: SELECT ... WHERE A AND B ORDER BY C LIMIT 10

    注意终端里打印的 SQL 语句 — ORM 自动生成的！
    """
    query = session.query(User)

    if active_only:
        query = query.filter(User.is_active == True)
        # .filter() 返回一个新的 query 对象，可以继续链式调用
    if min_age is not None:
        query = query.filter(User.age >= min_age)

    users = query.order_by(User.id.desc()).all()

    # users 是 User 对象的列表
    # FastAPI 用 UserResponse.model_validate() 转换每个 → JSON
    return users


# ── Read — 查询单个用户 ──────────────────────────────────────

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Session = Depends(get_session)):
    """
    按 ID 查单个用户。

    session.get(Model, primary_key) 是按主键查询的快捷方式。
    等价于: session.query(User).filter(User.id == user_id).first()
    """
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")
    return user


# ── Update — 更新用户 ─────────────────────────────────────

@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    name: str | None = None,
    age: int | None = None,
    session: Session = Depends(get_session),
):
    """
    更新用户（部分更新）。

    流程:
      1. 查到 ORM 对象
      2. 直接修改对象的属性
      3. session.commit() → SQLAlchemy 自动生成 UPDATE 语句

    不需要 session.update() 方法！
    只要修改了 ORM 对象的属性 + commit，数据库就会更新。
    """
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")

    # 只更新传了的字段
    if name is not None:
        user.name = name
    if age is not None:
        if age < 0 or age > 150:
            raise HTTPException(status_code=422, detail="年龄必须在 0-150 之间")
        user.age = age

    session.commit()   # 修改了属性 → SQLAlchemy 检测到变化 → 生成 UPDATE SQL
    session.refresh(user)  # 刷新 — 确保拿到数据库最终状态

    return user


# ── Delete — 删除用户 ─────────────────────────────────────

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    """
    删除用户。

    session.delete(obj) → 标记删除
    session.commit()    → 执行 DELETE SQL
    """
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")

    session.delete(user)
    session.commit()
    # 204 No Content — 不需要 return


# ═══════════════════════════════════════════════════════════════
# 商品接口（简版 — 演示另一个表）
# ═══════════════════════════════════════════════════════════════

@app.post("/products", status_code=201, response_model=ProductResponse)
def create_product(product_in: ProductCreate, session: Session = Depends(get_session)):
    """创建商品 — 和创建用户一样的模式"""
    product = Product(**product_in.model_dump())
    # **dict 语法: Product(name="机械键盘", price=399, stock=50)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@app.get("/products", response_model=list[ProductResponse])
def list_products(session: Session = Depends(get_session)):
    """商品列表"""
    return session.query(Product).all()


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn

    print("=" * 55)
    print("s06 — 数据库入门")
    print("   访问 http://localhost:8000/docs")
    print("   数据库文件: s06_app.db")
    print("   注意观察终端里打印的 SQL 语句！")
    print("   echo=True → 每条 SQL 都会打印出来")
    print("=" * 55)

    uvicorn.run(app, host="0.0.0.0", port=8000)
