# s07: Repository 模式 — 增删改查的标准套路

s01 → ... → s06 → `s07` → [s08](../s08_router_structure/) → ... → s17
> *"把数据库操作从路由函数里抽出来，封装成可复用的 Repository 类。"*
>
> **前提知识**: s06（会用 SQLAlchemy 做基本 CRUD）。

---

## 1. 问题：s06 的代码在重复

s06 的每个接口都直接写数据库操作：

```python
@app.get("/users")
def list_users(session=Depends(get_session)):
    return session.query(User).all()           # ← 重复

@app.get("/products")
def list_products(session=Depends(get_session)):
    return session.query(Product).all()         # ← 同样的模式
```

当有 30 个接口时，同样的分页逻辑写 30 遍。更麻烦的是：
- 要改排序方式？30 个地方全要改
- 要加分页？每个接口单独加
- 要换数据库？所有 SQL 都得检查

---

## 2. 解决方案：Repository 模式

**把数据访问逻辑封装到一个独立的类里**：

```
之前: 路由函数 → 直接写 SQL（混在一起）
之后: 路由函数 → Repository → SQL（职责分离）
```

```python
class UserRepository:
    """所有和 User 表相关的数据库操作都在这里"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)
    
    def list_all(self, skip=0, limit=100) -> list[User]:
        return self.session.query(User).offset(skip).limit(limit).all()
    
    def create(self, name: str, email: str) -> User:
        user = User(name=name, email=email)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
```

路由函数变得极其干净：

```python
@app.get("/users")
def list_users(repo: UserRepository = Depends(get_user_repo)):
    return repo.list_all()   # ← 一行，没有 SQL
```

---

## 3. 三层结构

```
┌──────────────────────────────────┐
│  路由层 (Route)                   │  ← 只负责 HTTP 协议
│  提取参数、调用 Repository、       │     (参数提取、状态码、响应格式)
│  返回响应                         │
└────────────┬─────────────────────┘
             │ 调用
┌────────────▼─────────────────────┐
│  仓库层 (Repository)              │  ← 只负责数据访问
│  查询、过滤、排序、分页、事务       │     (Session 操作)
└────────────┬─────────────────────┘
             │ 使用
┌────────────▼─────────────────────┐
│  模型层 (ORM Model)               │  ← 只负责表结构映射
│  User / Product / Order ...      │
└────────────┬─────────────────────┘
             │
┌────────────▼─────────────────────┐
│  数据库 (SQLite / PostgreSQL)      │
└──────────────────────────────────┘
```

每层只管自己的事。换数据库 → 只改 Repository。改接口格式 → 只改路由函数。

---

## 4. Repository 的核心方法

```python
class UserRepository:
    
    def get(self, id: int) -> User | None:        # 查单个
        ...
    
    def get_or_404(self, id: int) -> User:         # 查单个，不存在抛 404
        ...
    
    def list(self, skip=0, limit=100) -> list[User]:  # 查列表
        ...
    
    def create(self, **kwargs) -> User:             # 创建
        ...
    
    def update(self, id: int, **kwargs) -> User:    # 部分更新
        ...
    
    def delete(self, id: int) -> User:              # 删除
        ...
```

有了这些方法，所有用户相关的接口都不用重复写数据库操作。

---

## 5. 常见错误

### ❌ 在路由函数里还直接操作 session

```python
@app.get("/users")
def list_users(
    repo: UserRepository = Depends(get_user_repo),
    session: Session = Depends(get_session),   # ❌ 有了 repo 就不要直接拿 session
):
    return session.query(User).filter(...)      # ❌ 绕过 repo 了
```

### ❌ Repository 里写业务逻辑

```python
class UserRepository:
    def send_welcome_email(self, user):  # ❌ 这不是数据访问
        ...
    def calculate_age(self, birth):      # ❌ 这应该放 Service 层
        ...
```

Repository **只负责数据访问**。业务逻辑放在 Service 层（不在这门课的范围，但要知道这个原则）。

---

## 6. 自己动手

1. 仿照 UserRepository，自己写一个 ProductRepository 类
2. 给 ProductRepository 加一个 `find_by_price_range(min_price, max_price)` 方法
3. 把 s06 的路由函数改成使用 Repository
4. 对比改写前后的代码行数 — 感受一下封装的好处
