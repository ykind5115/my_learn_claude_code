#!/usr/bin/env python3
"""
s16 的测试文件

运行:
    cd s22_fastapi/s16_deployment
    pip install pytest httpx
    pytest test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from code import app, Base, get_session, Item

# ═══════════════════════════════════════════════════════════════
# 测试 fixture: 用独立的测试数据库
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
def client():
    """
    每个测试用独立的内存数据库。

    dependency_overrides 是 FastAPI 的"测试模式开关"—
    可以把真的依赖替换成测试版本。
    """
    engine = create_engine("sqlite:///test_s16.db", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    def override_get_session():
        with Session(engine) as s:
            yield s

    # 临时替换
    app.dependency_overrides[get_session] = override_get_session

    yield TestClient(app)

    # 清理: 删表 + 恢复原依赖
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


# ═══════════════════════════════════════════════════════════════
# 测试用例
# ═══════════════════════════════════════════════════════════════

class TestCreateItem:
    """创建 Item 的各种情况"""

    def test_create_success(self, client):
        """正常创建 → 201 + 返回正确数据"""
        r = client.post("/items", json={"name": "测试商品", "price": 99.9})
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "测试商品"
        assert data["price"] == 99.9
        assert "id" in data

    def test_create_missing_name(self, client):
        """缺少必填字段 → 422"""
        r = client.post("/items", json={"price": 99.9})
        assert r.status_code == 422

    def test_create_empty_name(self, client):
        """空字符串（min_length=1 不满足）→ 422"""
        r = client.post("/items", json={"name": "", "price": 99})
        assert r.status_code == 422

    def test_create_negative_price(self, client):
        """负价格（ge=0 不满足）→ 422"""
        r = client.post("/items", json={"name": "商品", "price": -10})
        assert r.status_code == 422


class TestListItems:
    """列表查询"""

    def test_empty(self, client):
        r = client.get("/items")
        assert r.status_code == 200
        assert r.json() == []

    def test_with_items(self, client):
        client.post("/items", json={"name": "A", "price": 10})
        client.post("/items", json={"name": "B", "price": 20})
        r = client.get("/items")
        assert len(r.json()) == 2


class TestGetItem:
    """查单个"""

    def test_found(self, client):
        created = client.post("/items", json={"name": "X", "price": 50})
        item_id = created.json()["id"]
        r = client.get(f"/items/{item_id}")
        assert r.status_code == 200
        assert r.json()["name"] == "X"

    def test_not_found(self, client):
        r = client.get("/items/99999")
        assert r.status_code == 404


class TestDeleteItem:
    """删除"""

    def test_delete(self, client):
        created = client.post("/items", json={"name": "待删", "price": 1})
        item_id = created.json()["id"]
        r = client.delete(f"/items/{item_id}")
        assert r.status_code == 204
        # 确认删了
        assert client.get(f"/items/{item_id}").status_code == 404

    def test_delete_nonexistent(self, client):
        assert client.delete("/items/99999").status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
