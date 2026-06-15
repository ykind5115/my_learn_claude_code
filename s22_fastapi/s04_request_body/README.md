# s04: 请求体 — 前端发来一大段 JSON 怎么收

s01 → s02 → s03 → `s04` → [s05](../s05_sqlalchemy/) → ... → s17
> *"POST 请求的 Body 是一大段 JSON。用 Pydantic 定义它的结构，FastAPI 自动校验。"*
>
> **前提知识**: s03（知道查询参数怎么用）。这章第一次接触 Pydantic — 只讲最基础的用法。

---

## 1. 为什么不能用查询参数？

s03 的参数都是通过 URL 传的：`?name=张三&age=25`。

但创建一个用户可能要传一大段数据：

```json
{
    "name": "张三",
    "age": 25,
    "email": "zhangsan@example.com",
    "address": {
        "province": "北京",
        "city": "北京",
        "detail": "望京 SOHO"
    },
    "tags": ["工程师", "Python"]
}
```

这堆数据没法塞进 URL（URL 有长度限制，而且嵌套结构不好表达）。所以 POST/PUT/PATCH 用 **请求体（Request Body）**。

---

## 2. 请求体怎么传？

```
POST /users HTTP/1.1
Host: localhost:8000
Content-Type: application/json       ← 告诉服务器"Body 是 JSON 格式"

{"name": "张三", "age": 25}          ← 这就是请求体
```

在 FastAPI 里，接收请求体的方式是：**定义一个 Pydantic 模型**。

---

## 3. Pydantic 是什么？（最简入门）

Pydantic 是一个 Python 库，FastAPI 用它来做数据校验。它最核心的概念是 `BaseModel`：

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    age: int
    email: str
```

这看起来就像在定义一个普通的 Python 类。区别是：

1. **继承 `BaseModel`** 之后，Pydantic 就接管了这个类的行为
2. **属性名 + 类型提示** 变成了校验规则：`name: str` 意思是"name 必须是字符串"
3. FastAPI 会自动用这个模型去**解析和校验**请求体

### 怎么用？

```python
@app.post("/users")
def create_user(user: UserCreate):    # ← 参数类型是 UserCreate
    print(user.name)                   # user 是 UserCreate 实例，不是 dict
    print(user.age)                    # 而且 age 已经是 int 类型了
    return {"name": user.name}
```

**FastAPI 做的事**：
1. 读取请求体的 JSON：`{"name": "张三", "age": 25, "email": "z@e.com"}`
2. 发现参数类型是 `UserCreate`（一个 BaseModel 子类）
3. 用 `UserCreate` 解析 JSON → 创建一个 UserCreate 对象
4. 如果 JSON 里缺少必填字段（比如没有 name）→ 自动返回 422
5. 如果类型不对（比如 age 传了 `"二十五"`）→ 自动返回 422
6. 把解析好的 `user` 对象传给你的函数

### 对比：不用 Pydantic vs 用 Pydantic

```python
# 不用 Pydantic — 手动校验
@app.post("/users")
def create_user(name: str, age: int, email: str):
    # 这三个参数 FastAPI 默认从查询参数取！
    # 要改成从 Body 取，得写 Body(...)
    if len(name) < 2:
        raise HTTPException(400, "name 太短")
    # ... 更多手动校验 ...

# 用 Pydantic — 自动校验
class UserCreate(BaseModel):
    name: str
    age: int
    email: str

@app.post("/users")
def create_user(user: UserCreate):   # ← 一行搞定
    # user 已经是校验过的 UserCreate 对象
    ...
```

---

## 4. 一步一步来

### 第 1 步：安装 Pydantic

```bash
pip install pydantic   # 安装 fastapi 时通常已经装好了
```

### 第 2 步：定义一个模型

```python
from pydantic import BaseModel

class CreateItem(BaseModel):
    title: str           # 必填，必须是字符串
    price: float         # 必填，必须是数字（整数或小数）
    stock: int = 0       # 可选，默认值是 0
    tags: list[str] = [] # 可选，默认是空列表
```

### 第 3 步：在接口里使用它

```python
@app.post("/items", status_code=201)
def create_item(item: CreateItem):
    return {
        "title": item.title,
        "price": item.price,
        "stock": item.stock,
    }
```

### 第 4 步：用 /docs 测试

打开 `http://localhost:8000/docs`，找到 POST `/items`，点 **Try it out**。你会发现 Swagger UI 自动展示了 CreateItem 的所有字段 — 包括类型、默认值、哪些是必填的。

---

## 5. `response_model` — 控制返回什么

有时候你不想返回全部字段。比如 `password` 不能返回给前端：

```python
class UserCreate(BaseModel):
    username: str
    password: str    # 创建时用

class UserResponse(BaseModel):
    username: str
    # 注意：没有 password！这样返回值里就不会包含密码

@app.post("/users", response_model=UserResponse)   # ← response_model
def create_user(user: UserCreate):
    # 返回 user 的全部信息，但 response_model 会自动过滤掉 password
    return user
```

`response_model` 的作用就像**过滤器**：只保留 UserResponse 里定义过的字段。

---

## 6. 嵌套模型 — 一个模型嵌另一个

```python
class Address(BaseModel):
    province: str
    city: str
    detail: str

class UserCreate(BaseModel):
    name: str
    age: int
    address: Address      # ← 嵌套！address 字段的类型是另一个 BaseModel

# 请求体的 JSON:
# {
#     "name": "张三",
#     "age": 25,
#     "address": {
#         "province": "北京",
#         "city": "北京",
#         "detail": "望京 SOHO"
#     }
# }
```

FastAPI 会**递归校验**：先校验 UserCreate，再校验嵌套的 Address。

---

## 7. 常见错误

### ❌ 把 Body 和 Query 搞混

```python
# 错误理解：认为 POST 的参数也是 URL 参数
# POST /users?name=张三&age=25  ← 这是 GET 的传参方式

# 正确：POST 的数据在 Body 里，定义 Pydantic 模型来接收
@app.post("/users")
def create_user(user: UserCreate):   # 从 Body 取
    ...

# 查询参数只在 GET（和 DELETE 等）用
@app.get("/users")
def list_users(page: int = 1):       # 从 Query 取
    ...
```

### ❌ 忘记在 POST 路由上设 `status_code=201`

```python
@app.post("/items")               # 默认 status_code 是 200
def create_item(item: CreateItem):
    ...
    return item                    # 创建成功应该返回 201 Created

@app.post("/items", status_code=201)  # ✅
```

### ❌ 以为 Pydantic 模型 = 数据库表

```python
# Pydantic 模型：用来校验 HTTP 请求/响应的数据（API 层）
class UserCreate(BaseModel):
    ...

# 数据库模型：用来定义数据库表结构（数据层）— s06 才学
# 这是两个不同的东西！
```

---

## 8. 你学到了什么

| 概念 | 一句话 |
|------|--------|
| 请求体 (Body) | POST/PUT 请求中放在 Body 里的 JSON 数据 |
| Pydantic BaseModel | 定义一个类来描述 Body 的结构和校验规则 |
| FastAPI 怎么用模型 | 函数参数类型是 BaseModel 子类 → 自动从 Body 解析 |
| `response_model` | 控制返回给前端的数据结构（过滤敏感字段） |
| 嵌套模型 | 一个 BaseModel 可以作为另一个的字段类型 |

---

## 9. 自己动手

1. 定义一个 `CreateOrder` 模型，包含 `items`（列表）、`total`（数字）、`address`（嵌套 Address 模型）
2. 写 POST 接口接收 CreateOrder 并返回它（先不存数据库）
3. 用 `/docs` 的 Try it out 发送请求，故意缺字段、错类型，观察 422 响应
4. 定义 `OrderResponse` 模型（和 CreateOrder 一样但多一个 `order_id`），用 `response_model` 过滤
