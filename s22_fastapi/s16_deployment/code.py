#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s16: 测试 — 用代码验证代码

本文件是被测试的 API（一个简化的待办事项应用）。
test_api.py 是测试文件。

启动 API:
    python s22_fastapi/s16_deployment/code.py

运行测试:
    cd s22_fastapi/s16_deployment
    pip install pytest httpx
    pytest test_api.py -v
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import create_engine, String, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# ═══════════════════════════════════════════════════════════════
# 数据库
# ═══════════════════════════════════════════════════════════════

engine = create_engine("sqlite:///s16_app.db", echo=False, connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Integer, default=0)  # 简化, 实际是 Float
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)


def get_session():
    with Session(engine) as session:
        yield session


# ═══════════════════════════════════════════════════════════════
# Schema
# ═══════════════════════════════════════════════════════════════

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., ge=0)


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    is_available: bool
    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# App
# ═══════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="s16 - 测试",
    description="接口写完先跑测试 — TestClient + pytest",
    version="16.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {"message": "s16 — 测试", "run": "pytest test_api.py -v"}


@app.post("/items", status_code=201, response_model=ItemResponse)
def create_item(item_in: ItemCreate, session=Depends(get_session)):
    item = Item(name=item_in.name, price=item_in.price)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@app.get("/items", response_model=list[ItemResponse])
def list_items(session=Depends(get_session)):
    return session.query(Item).all()


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, session=Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item 不存在")
    return item


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, session=Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item 不存在")
    session.delete(item)
    session.commit()


if __name__ == "__main__":
    import uvicorn
    print("s16 — 测试")
    print("启动 API 后运行: pytest test_api.py -v")
    uvicorn.run(app, host="0.0.0.0", port=8000)
