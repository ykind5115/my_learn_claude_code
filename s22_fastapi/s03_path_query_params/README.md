# s03: 接收参数 — 前端怎么把数据传进来

s01 → s02 → `s03` → [s04](../s04_request_body/) → ... → s17
> *"URL 里的每个参数都不是随便放的 — FastAPI 让它们自动变成你函数的参数，顺带校验。"*
>
> **前提知识**: s02（会返回 JSON、会用状态码）。

---

## 1. 为什么需要这一章？

s01-s02 的接口要么不接收参数（`GET /hello`），要么只接收简单的路径参数（`GET /users/{id}`）。

但真实世界长这样：

```
GET /products?category=electronics&min_price=1000&max_price=5000&sort=price&page=1&size=20
```

怎么让 FastAPI 读懂这串东西？怎么保证 `page` 不会是负数？这就是本章要解决的问题。

---

## 2. 两种传参方式：路径参数 vs 查询参数

```
https://example.com/users/42?active=true&page=1
                      └─┬─┘ └──────┬──────┘
                    路径参数      查询参数
                 (在路径里)    (在 ? 后面)
```

| 路径参数 | 查询参数 |
|---------|---------|
| 写在哪 | URL 路径中：`/users/{id}` | URL `?` 后面：`?key=value` |
| 用来干嘛 | 定位**哪一个**资源 | 过滤/排序/分页 |
| 必须还是可选 | 通常是必须的 | 通常有默认值（可选） |
| 例子 | `/users/42` — 42 号用户 | `/users?active=true` — 激活的用户 |
| FastAPI 里怎么写 | `{id}` + 函数参数同名 | 不在路径模板中的参数自动成为查询参数 |

---

## 3. 路径参数 — 深入

s01 已经用过 `{user_id}`。这节说说你还不知道的：

### FastAPI 怎么知道参数的顺序？

URL 匹配时只看**参数名是否一致**，不看顺序：

```python
@app.get("/users/{a}/posts/{b}")
def get_post(a: int, b: int):    # a=1, b=2
    ...

# 访问 /users/1/posts/2  → a=1, b=2  ✅
```

### 类型转换是自动的

```python
@app.get("/items/{item_id}")
def get_item(item_id: int):     # ← :int 告诉 FastAPI 要转成整数
    ...

# /items/42   → item_id = 42 (int)  ✅
# /items/abc  → 422 错误           ❌ (abc 不是 int)
```

---

## 4. 查询参数 — 全部规则

### 规则只有一个

> **函数参数中，名字没出现在 URL 路径模板中的，就是查询参数。**

```python
@app.get("/users")                   # 路径模板里没有变量
def list_users(
    active: bool = False,            # 不在路径中 → 查询参数 ?active=true
    page: int = 1,                   # 不在路径中 → 查询参数 ?page=1
):
    ...

# 相当于: GET /users?active=true&page=1
```

### 可选 vs 必填

```python
# 有默认值 → 可选
page: int = 1          # 不传就用 1

# 有默认值 None → 可选，值是 None
keyword: str | None = None   # 不传就是 None

# 没有默认值 → 必填
keyword: str            # 必须传 ?keyword=xxx
```

---

## 5. 参数校验 — `Query()` 和 `Path()`

到目前为止，参数校验只用了类型提示（`:int`、`:str`）。FastAPI 提供了 `Query()` 和 `Path()` 来做更精细的控制：

```python
from fastapi import Query, Path

@app.get("/products")
def list_products(
    # Query() 给查询参数加校验
    page: int = Query(default=1, ge=1, description="页码，从 1 开始"),
    size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    keyword: str | None = Query(default=None, min_length=2, description="搜索关键词"),
):
    ...
```

### 常用校验参数

| 参数 | 含义 | 适用类型 | 例子 |
|------|------|---------|------|
| `ge` | greater or equal (≥) | int, float | `ge=1` → 不能小于 1 |
| `le` | less or equal (≤) | int, float | `le=100` → 不能大于 100 |
| `gt` | greater than (>) | int, float | `gt=0` → 必须大于 0 |
| `lt` | less than (<) | int, float | `lt=1000` → 必须小于 1000 |
| `min_length` | 最小长度 | str | `min_length=2` → 至少 2 个字符 |
| `max_length` | 最大长度 | str | `max_length=50` → 最多 50 个字符 |
| `pattern` | 正则表达式 | str | `pattern=r"^1[3-9]\d{9}$"` → 手机号 |

### Path() 也一样

```python
@app.get("/users/{user_id}")
def get_user(
    user_id: int = Path(..., ge=1, description="用户 ID")
    #                         └─ ... 表示必填（路径参数本来就必填，这里只是语法要求）
):
    ...
```

---

## 6. 枚举参数 — 限定可选值

有些参数只能取几个特定值。用 `Enum`：

```python
from enum import Enum

class Category(str, Enum):
    electronics = "electronics"
    clothing = "clothing"
    books = "books"

@app.get("/products")
def list_products(category: Category | None = None):
    # category 只能是上面的三个值之一，或者是 None
    ...
```

访问 `/products?category=electronics` ✅
访问 `/products?category=toy` ❌ 422 错误

---

## 7. 完整示例：电商商品筛选

把所有知识串起来，写一个真实的商品列表接口：

```python
@app.get("/products")
def list_products(
    # 过滤
    category: Category | None = Query(None),
    keyword: str | None = Query(None, min_length=2),

    # 价格范围
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),

    # 排序
    sort_by: str = Query("newest", pattern="^(price|name|newest)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),

    # 分页
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    ...
```

---

## 8. 常见错误

### ❌ 路径参数名和函数参数名不一致

```python
@app.get("/users/{user_id}")
def get_user(id: int):       # ❌ 函数参数叫 id，URL 里叫 user_id
    ...

# 修复: 保持一致
def get_user(user_id: int):  # ✅
```

### ❌ 查询参数和路径参数搞混

```python
@app.get("/users/{id}")
def get_user(id: int, page: int = 1):
    # id 是路径参数（来自 /users/42）
    # page 是查询参数（来自 ?page=1）

# 访问: /users/42?page=1
# id = 42（路径参数）
# page = 1（查询参数）
```

### ❌ 校验参数写错位置

```python
# ❌ 把 Query 用在路径参数上
def get_user(user_id: int = Query(...)):  # 不对，路径参数用 Path()

# ✅ 路径参数用 Path，查询参数用 Query
def get_user(user_id: int = Path(...), page: int = Query(...)):
```

---

## 9. 自己动手

1. 写一个 `GET /search` 接口，接收 `keyword`（必填）、`page`（可选，默认 1）、`size`（可选，默认 20，最多 100）
2. 加一个枚举参数 `type`，可选值为 `article`、`user`、`tag`
3. 故意传不合法的参数值，看 FastAPI 返回的 422 错误长什么样
4. 在 `/docs` 页面试试各种参数组合 — 注意文档里自动显示了每个参数的描述和限制
