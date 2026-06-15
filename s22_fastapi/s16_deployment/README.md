# s16: 测试 — 用代码验证代码

s01 → ... → s15 → `s16` → [s17](../s17_deployment/)
> *"没有测试的 API 就像没有刹车的车 — 能跑，但不敢开快。改了代码怎么确认没弄坏别处？"*
>
> **前提知识**: s11-s13（理解认证和权限）。

---

## 1. 为什么需要测试？

手动测试的弊端：
- 50 个接口 × 3 种情况 = 150 个手动步骤，没人会做
- 改了 A 接口 → B 接口悄悄坏了 → 上线才发现
- 不敢重构代码（"万一搞坏了呢？"）

自动化测试 = **写代码来测试代码**。每次改完，一行命令跑完所有测试。

---

## 2. FastAPI 的 TestClient

FastAPI 提供了 `TestClient`（基于 httpx），它让你**像调用函数一样调用 API**：

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello"}
```

关键点：
- `TestClient` 不需要启动服务器 — 它直接在内存里模拟 HTTP 请求
- `response.status_code` — 检查 HTTP 状态码
- `response.json()` — 获取响应 JSON

---

## 3. 测试数据库

测试不能用生产数据库（会污染真实数据）。解决方案：**用独立的内存数据库**。

```python
import pytest
from sqlalchemy import create_engine

@pytest.fixture
def client():
    """每个测试用独立的数据库"""
    # 创建测试数据库
    engine = create_engine("sqlite:///test.db")
    Base.metadata.create_all(bind=engine)

    # 用 FastAPI 的 dependency_overrides 替换依赖
    def override_get_session():
        with Session(engine) as s:
            yield s
    app.dependency_overrides[get_session] = override_get_session

    yield TestClient(app)

    # 清理
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
```

`dependency_overrides` 是 FastAPI 的**测试模式开关** — 可以临时把 `get_session` 替换成测试版本。

---

## 4. 测试认证接口

```python
def test_protected_route(client):
    # 不带 token → 401
    response = client.get("/me")
    assert response.status_code == 401

    # 带 token → 200
    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == 200
```

---

## 5. 测试金字塔

```
    /\
   /E2E\          ← 少量端到端测试（完整用户流程）
  /------\
 / 集成测试 \       ← 中量（API + 数据库）
/----------\
  单元测试         ← 大量（单个函数/组件）
```

新手从**集成测试**开始（测 API 端点），它性价比最高。

---

## 6. 自己动手

1. 给 s06 或 s12 的 code.py 写 3 个测试: 创建成功、创建失败（缺字段）、获取列表
2. 跑 `pytest -v` 看到绿色 ✅
3. 试着改坏一个接口，看测试能不能抓到
