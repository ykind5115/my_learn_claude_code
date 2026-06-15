# s09: 路由拆分 — 50 个接口不乱，靠 APIRouter

s01 → ... → s08 → `s09` → [s10](../s10_exception_middleware/) → ... → s17
> *"当一个文件几千行，Git 冲突无数 — 你就知道为什么要拆分了。APIRouter 让你按业务领域组织代码。"*
>
> **前提知识**: s08（理解了 Depends 依赖链）。

---

## 1. 问题：一个文件能装多少？

s01-s08 的所有代码都在一个文件里。想象一个真实项目：
- 50 个接口
- 10 张数据库表
- 认证、权限、日志、配置...

全放一个文件 → 几千行代码，找路由像大海捞针。多人协作 → 每次 Git 合并都冲突。

---

## 2. 解决方案：APIRouter

FastAPI 提供了 `APIRouter`，它和 `FastAPI()` 用法几乎一样，但可以**拆分到不同文件**。

```python
# routers/users.py — 用户相关路由（一个文件）
from fastapi import APIRouter

router = APIRouter(
    prefix="/users",       # ← 所有路由自动加前缀
    tags=["用户管理"],      # ← 在 /docs 里分组显示
)

@router.get("/")           # 实际路径: GET /users/
def list_users(): ...

@router.get("/{id}")       # 实际路径: GET /users/{id}
def get_user(id: int): ...

@router.post("/")          # 实际路径: POST /users/
def create_user(): ...
```

然后在主应用里像乐高一样**组装**：

```python
# main.py — 入口文件（几十行）
from fastapi import FastAPI
from routers import users, posts, auth, admin

app = FastAPI()

app.include_router(users.router)    # 插上用户模块
app.include_router(posts.router)    # 插上文章模块
app.include_router(auth.router)     # 插上认证模块
app.include_router(admin.router)    # 插上管理模块
# 不需要某个模块？注释掉一行就关掉了
```

---

## 3. 推荐的项目结构

```
project/
  main.py                    ← 入口：创建 app + include_router
  config.py                  ← 配置（SECRET_KEY、DATABASE_URL...）
  database.py                ← engine、Base、get_session
  dependencies.py            ← 公共依赖（get_current_user、分页...）

  models/                    ← ORM 模型
    __init__.py
    user.py
    post.py

  schemas/                   ← Pydantic Schema
    __init__.py
    user.py
    post.py

  routers/                   ← 路由模块 ★
    __init__.py
    auth.py                  ← /auth/*
    users.py                 ← /users/*
    posts.py                 ← /posts/*
    admin.py                 ← /admin/*
```

每个目录有自己的 `__init__.py`，让别的文件可以 `from models import User` 而不是 `from models.user import User`。

---

## 4. APIRouter 的关键参数

| 参数 | 作用 | 例子 |
|------|------|------|
| `prefix` | 自动加在所有路由前面 | `prefix="/users"` → `/users/`、`/users/{id}` |
| `tags` | 在 /docs 里分组显示 | `tags=["用户管理"]` |
| `dependencies` | 整个模块的公共依赖 | `dependencies=[Depends(get_current_user)]` |
| `responses` | 公共响应描述 | 整个模块都返回 401/403 的话写在这 |

---

## 5. 常见错误

### ❌ 在主应用和 Router 里都加了 prefix

```python
# main.py
app.include_router(users.router, prefix="/api/v1")

# users.py
router = APIRouter(prefix="/users")

# 实际路径: /api/v1/users/ ✅ （两者叠加）
# 如果不想叠加，只在一个地方写 prefix
```

### ❌ 忘记 `__init__.py`

```python
# 想写 from routers import users
# 但 routers 目录下没有 __init__.py → 会报错

# 解决: touch routers/__init__.py（可以是空文件）
```

---

## 6. 自己动手

1. 把 s08 的 `main.py` 拆成：`routers/auth.py`（登录）、`routers/posts.py`（文章）、`routers/admin.py`（管理员）
2. 提取公共依赖到 `dependencies.py`
3. 打开 `/docs`，看 tags 分组效果
