"""数据库基础设施 — engine、Base、get_session"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

DATABASE_URL = "sqlite:///s08_app.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


class Base(DeclarativeBase):
    pass


def get_session():
    """FastAPI 依赖 — 每个请求一个数据库会话"""
    with Session(engine) as session:
        yield session
