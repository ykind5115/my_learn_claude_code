# s08: 依赖注入 — Depends() 是 FastAPI 最强大的功能

s01 → ... → s07 → `s08` → [s09](../s09_unified_response/) → ... → s17
> *"Depends() 像一个隐形的管道 — 把认证、数据库、配置自动注入到每个接口，你只需要声明'我需要什么'。"*
>
> **前提知识**: s07（用了 Depends 获取 Repository，但没深入理解它）。

---

## 1. 你已经用过 Depends，但可能不知道为什么

s06-s07 一直在用但没解释：

```python
def list_users(repo: UserRepository = Depends(get_user_repo)):
    ...
```

这一行背后发生了三件事：

1. **FastAPI 检测到** `Depends(get_user_repo)` — 知道要先调 `get_user_repo`
2. **FastAPI 分析 get_user_repo** — 发现它自己也有 Depends：`session = Depends(get_session)`
3. **FastAPI 递归解析整个依赖链** — 然后调用你的函数

---

## 2. 依赖链是怎么工作的

```python
def get_session():               # 第 0 层
    with Session(engine) as session:
        yield session

def get_user_repo(session = Depends(get_session)):  # 第 1 层
    return UserRepository(session)

def get_current_user(token = Header(), session = Depends(get_session)):  # 第 2 层
    ...

@app.get("/me")
def me(user = Depends(get_current_user)):  # 你的函数
    ...

# 完整执行顺序:
# 请求进来
# → get_session() 创建 session
# → get_current_user() 用 session 和 Header 解析用户
# → me(user) 你的业务逻辑
# → 请求结束，get_session 的 yield 后代码执行（关闭 session）
```

> **关键理解**：`Depends()` 可以嵌套。FastAPI 会递归解析，就像一个洋葱，从外到内一层层剥开。

---

## 3. Depends 的三种形态

### 形态 1：函数（最常用）

```python
def get_session():
    with Session(engine) as session:
        yield session

session = Depends(get_session)
```

### 形态 2：类（需要参数化）

```python
class Pagination:
    def __init__(self, max_size=100):
        self.max_size = max_size
    
    def __call__(self, page: int = 1, size: int = 20):
        if size > self.max_size:
            size = self.max_size
        return {"page": page, "size": size, "skip": (page-1) * size}

# 使用
@app.get("/items")
def list_items(pag = Depends(Pagination(max_size=50))):
    # pag = {"page": 1, "size": 20, "skip": 0}
    ...
```

> 用类的好处：可以传参数给 `__init__`，创建不同配置的依赖实例。

### 形态 3：yield 依赖（需要清理资源）

```python
def get_db():
    db = connect_to_db()
    try:
        yield db        # 请求处理时用这个
    finally:
        db.close()       # 请求结束后一定执行（即使出错了）
```

---

## 4. 实战：用 Depends 做认证

这是最常见的用法。把认证逻辑抽成独立的依赖函数，然后像乐高一样组装：

```python
# 基础依赖：从 JWT 获取用户
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user = session.get(User, payload["sub"])
    if not user:
        raise HTTPException(401)
    return user

# 叠加上去：要求管理员
def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(403)
    return user

# 接口里只管声明需要什么
@app.get("/admin/dashboard")
def admin_dashboard(admin: User = Depends(require_admin)):
    return {"message": "欢迎管理员"}

@app.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"username": user.name}
```

---

## 5. 和 learn-claude-code 的对应

| learn-claude-code | s08 Depends |
|-------------------|-------------|
| Hook 环绕 Agent Loop | Depends 环绕路由函数 |
| Pre-hook / Post-hook | 依赖函数 / yield 清理 |
| Hook 链式执行 | 依赖链递归解析 |

共同思想：**在核心逻辑前后插入可复用的处理单元。**

---

## 6. 常见错误

### ❌ Depends 函数名写错

```python
def get_user_repo(session=Depends(get_session)): ...

# ❌ 忘记加 Depends
@app.get("/users")
def list_users(repo = get_user_repo):   # 没加 Depends()，不会注入

# ✅
def list_users(repo = Depends(get_user_repo)):
```

### ❌ 循环依赖

```python
def a(b = Depends(c)): ...   # a 依赖 c
def c(a = Depends(a)): ...   # c 依赖 a → 死循环！

# FastAPI 会检测到并报错
```

---

## 7. 自己动手

1. 写一个 `Pagination` 类依赖，用 `__call__` 方法自动提取 page/size
2. 写一个 `get_current_user` 依赖（模拟认证），然后在 `/me` 接口里用
3. 写两个依赖链：`get_session → get_repo`，看路由函数拿到 repo 走了多少步
