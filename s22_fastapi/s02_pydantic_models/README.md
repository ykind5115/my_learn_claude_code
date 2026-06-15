# s02: 返回数据 — JSON、状态码与自动文档

s01 → `s02` → [s03](../s03_path_query_params/) → ... → s17
> *"后端不只是返回 Hello World。你得知道怎么返回列表、怎么返回错误、怎么让前端明白你在说什么。"*
>
> **前提知识**: s01（会写 `@app.get()`、会启动 uvicorn）。

---

## 1. 为什么这章重要？

s01 只返回了简单的 `{"message": "..."}` 。但真实的后端接口要返回更丰富的数据：
- 有时候要返回一个**列表**（比如用户列表）
- 有时候要返回**嵌套结构**（比如用户 + 他的订单）
- 有时候要告诉前端**"你搞错了"**（用状态码 404）
- 有时候要告诉前端**"创建成功"**（用状态码 201）

这章就教你这些。

---

## 2. FastAPI 是怎么把 dict 变成 JSON 的？

你在函数里 `return {"name": "张三"}` ，浏览器收到的是：

```json
{"name": "张三"}
```

原理很简单：FastAPI 内部调用了 `json.dumps()` 把你的 dict 转成了 JSON 字符串，然后设置了 `Content-Type: application/json`。

所以你能返回的东西，本质上就是 `json.dumps()` 能处理的东西：

| Python 类型 | 对应的 JSON | 示例 |
|------------|-----------|------|
| `dict` | `{"key": "value"}` | `return {"name": "张三"}` |
| `list` | `["a", "b", "c"]` | `return [1, 2, 3]` |
| `str` | `"hello"` | `return "hello"` |
| `int` / `float` | `123` / `3.14` | `return 42` |
| `bool` | `true` / `false` | `return True` |
| `None` | `null` | `return None` |

> **但注意**：实际项目中，**几乎总是返回 `dict`**。因为 dict 可以包含 key，前端可以根据 key 来取值。
> 你返回一个裸的 `[1,2,3]`，前端没法区分"这是用户 ID 列表"还是"这是商品 ID 列表"。

---

## 3. 返回不同数据结构

### 返回列表

```python
@app.get("/users")
def list_users():
    return [
        {"id": 1, "name": "张三"},
        {"id": 2, "name": "李四"},
    ]
```

访问 `/users` 你会看到 JSON 数组。`/docs` 里也会自动展示。

### 返回嵌套结构

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {
        "id": user_id,
        "name": "张三",
        "address": {               # ← 嵌套的 dict
            "city": "北京",
            "street": "长安街 100 号",
        },
        "orders": [                # ← dict 里面嵌套 list
            {"id": 101, "total": 299.00},
            {"id": 102, "total": 159.00},
        ],
    }
```

---

## 4. HTTP 状态码 — 告诉前端结果如何

回顾 s00：状态码是服务器对请求的"评价"。

FastAPI 中默认情况下：
- 函数正常 `return` → 状态码 **200**
- 路由没写 `status_code` → 状态码 **200**（GET/PUT/PATCH/DELETE 都是）
- POST 路由 → 应该手动设为 **201**

### 指定状态码

```python
from fastapi import FastAPI

@app.post("/users", status_code=201)   # ← 创建成功用 201
def create_user():
    return {"message": "创建成功"}

@app.delete("/users/{user_id}", status_code=204)   # ← 删除成功用 204
def delete_user(user_id: int):
    # 204 No Content — 成功删除但没有返回内容
    # 函数可以 return None 或者直接不 return
    pass
```

### 常见的状态码选择

| 场景 | 状态码 | 含义 |
|------|--------|------|
| GET 查询成功 | `200`（默认） | OK |
| POST 创建成功 | `201` | Created |
| DELETE 删除成功 | `204` | No Content |
| 资源不存在 | `404` | Not Found |
| 参数校验失败 | `422` | Unprocessable Entity |

---

## 5. Swagger UI（`/docs`）详解

FastAPI 的 `/docs` 页面就是 **Swagger UI** — 一个交互式的 API 调试工具。

启动你的应用后访问 `http://localhost:8000/docs`：

```
┌─────────────────────────────────────────────────┐
│  s02 - 学习 API                     [ 选择规格 ] │
│  ─────────────────────────────────────────────── │
│                                                  │
│  ▼ GET  /                           [Try it out] │
│  ▼ GET  /users                      [Try it out] │
│  ▼ GET  /users/{user_id}            [Try it out] │
│  ▼ POST /users                      [Try it out] │
│                                                  │
│  Schemas (数据模型会出现在这里，见 s04)            │
└─────────────────────────────────────────────────┘
```

**怎么用**：
1. 点任意接口展开
2. 点 **"Try it out"** 按钮
3. 填写参数
4. 点 **"Execute"** 发送请求
5. 下面会显示 **Response**（服务器返回了什么）

> **这比 curl 和 Postman 都方便**：不需要离开浏览器，不需要记命令。

---

## 6. 返回错误 — HTTPException

不是所有请求都能成功。用户可能请求了一个不存在的 ID：

```python
from fastapi import HTTPException

@app.get("/users/{user_id}")
def get_user(user_id: int):
    # 查数据库...发现没有这个用户
    if user_id > 100:  # 模拟：ID 大于 100 的"不存在"
        raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")
    return {"id": user_id, "name": "张三"}
```

**`HTTPException` 做了什么**：
1. 停止函数执行（和普通 `raise` 一样）
2. 设置 HTTP 状态码为 404
3. 把 `detail` 字段放在响应 Body 里：`{"detail": "用户 999 不存在"}`
4. FastAPI 不会把它当成服务器崩溃

> **关键区别**：
> - `HTTPException` → FastAPI 知道这是"正常的错误"，返回 4xx
> - `ValueError` / `RuntimeError` → FastAPI 不知道，返回 500（服务器内部错误）

---

## 7. 常见错误

### ❌ 返回了一个不能序列化的东西

```python
@app.get("/bad")
def bad():
    from datetime import datetime
    return {"now": datetime.now()}   # ❌ datetime 不能直接转 JSON
```

FastAPI 会报错，因为这个 Python 对象没法用 `json.dumps()` 转换。
后面学了 Pydantic（s04）就能优雅处理这个问题。

### ❌ 忘记 import

```python
raise HTTPException(...)   # ❌ NameError: HTTPException 没有 import

# 需要在文件顶部加上:
from fastapi import HTTPException
```

---

## 8. 你学到了什么

| 你写的东西 | FastAPI 帮你做了什么 |
|-----------|---------------------|
| `return {"a": 1}` | 转成 JSON，设 Content-Type |
| `return [{...}, {...}]` | 转成 JSON 数组 |
| `status_code=201` | 改变 HTTP 状态码 |
| `raise HTTPException(404, ...)` | 返回错误响应 |
| 启动后访问 `/docs` | 自动生成交互式文档 |

---

## 9. 自己动手

1. 写一个 `GET /products` 接口，返回一个商品列表（每个商品有 id、name、price）
2. 给某个商品 ID 返回一个嵌套结构（商品 + 评价列表）
3. 给某个不存在的商品 ID 返回 404 错误
4. 打开 `/docs`，用 "Try it out" 测试这些接口
5. 观察：返回 200 和 404 时，浏览器的 Network 面板有什么区别？
