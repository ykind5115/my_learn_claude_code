"""
s15 测试文件 — 用 pytest + TestClient 测试 API

运行:
    cd s22_fastapi/s15_testing
    pip install pytest httpx
    pytest test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from code import app, Base, get_session, ItemModel

# ============================================================
# 测试数据库 — 每次测试用独立的内存数据库
# ============================================================

TEST_DATABASE_URL = "sqlite:///test_s15.db"


@pytest.fixture(autouse=True)
def setup_database():
    """每个测试前后：创建表 → 运行测试 → 清空表"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    # 用 dependency_overrides 替换数据库依赖
    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    yield

    # 清理
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    """创建测试客户端"""
    return TestClient(app)


# ============================================================
# 测试用例
# ============================================================

class TestRoot:
    """根路径测试"""

    def test_root_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "s15" in data["message"]


class TestCreateItem:
    """创建 Item 测试"""

    def test_create_item_success(self, client):
        response = client.post("/items", json={"name": "测试商品", "price": 99.9})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "测试商品"
        assert data["price"] == 99.9
        assert data["is_available"] == True
        assert "id" in data

    def test_create_item_missing_name(self, client):
        """缺少必填字段 → 422"""
        response = client.post("/items", json={"price": 99.9})
        assert response.status_code == 422

    def test_create_item_empty_name(self, client):
        """空名称 → 422"""
        response = client.post("/items", json={"name": "", "price": 99.9})
        assert response.status_code == 422

    def test_create_item_negative_price(self, client):
        """负价格 → 422"""
        response = client.post("/items", json={"name": "商品", "price": -10})
        assert response.status_code == 422


class TestListItems:
    """列表测试"""

    def test_empty_list(self, client):
        response = client.get("/items")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_with_items(self, client):
        # 先创建几个
        client.post("/items", json={"name": "A", "price": 10})
        client.post("/items", json={"name": "B", "price": 20})

        response = client.get("/items")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "A"
        assert data[1]["name"] == "B"


class TestGetItem:
    """获取单个 Item 测试"""

    def test_get_existing_item(self, client):
        # 创建一个
        created = client.post("/items", json={"name": "商品", "price": 50})
        item_id = created.json()["id"]

        # 获取它
        response = client.get(f"/items/{item_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "商品"

    def test_get_nonexistent_item(self, client):
        response = client.get("/items/99999")
        assert response.status_code == 404


class TestDeleteItem:
    """删除测试"""

    def test_delete_existing_item(self, client):
        created = client.post("/items", json={"name": "待删除", "price": 1})
        item_id = created.json()["id"]

        response = client.delete(f"/items/{item_id}")
        assert response.status_code == 204

        # 确认删了
        response = client.get(f"/items/{item_id}")
        assert response.status_code == 404

    def test_delete_nonexistent_item(self, client):
        response = client.delete("/items/99999")
        assert response.status_code == 404


# ============================================================
# 运行说明
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
