# s06: 数据库入门 — 数据怎么存到硬盘上

s01 → ... → s05 → `s06` → [s07](../s07_dependency_injection/) → ... → s17
> *"目前所有数据都在内存里，服务器重启就没了。这一章让你的数据真正「落地」。"*
>
> **前提知识**: s05（会用 Pydantic Field 做校验）。不需要数据库基础。

---

## 1. 为什么需要数据库？

目前所有数据都存在 Python 列表里：

```python
users_db = []   # 服务器重启 → 数据全部消失 ❌
```

数据库解决三个问题：

| 问题 | 数据库怎么解决 |
|------|--------------|
| 服务器重启数据没了 | 数据存在**硬盘**上，重启不丢 |
| 数据多了查不动 | 数据库有**索引**，百万条数据也能快速查询 |
| 多人同时操作冲突 | 数据库有**事务**，保证数据一致性 |

---

## 2. SQLite 是什么？

**SQLite** 是一个把整个数据库存在**一个文件**里的轻量数据库。它：
- 不需要安装任何服务器软件
- 不需要配置用户名密码
- 你只需要告诉它"数据库文件叫什么名字"

```python
# 这就是全部配置！
engine = create_engine("sqlite:///myapp.db")
# 数据都存在 myapp.db 这个文件里
```

> 学习阶段用 SQLite。生产环境换成 PostgreSQL 或 MySQL 只需要改一行配置。

---

## 3. ORM 是什么？（重要概念）

**ORM = Object-Relational Mapping = 对象关系映射**

不用 ORM（原始 SQL）：
```python
# 你要手写 SQL 字符串
cursor.execute("INSERT INTO users (name, age) VALUES ('张三', 25)")
cursor.execute("SELECT * FROM users WHERE age > 18")
rows = cursor.fetchall()
# rows 是元组列表: [(1, '张三', 25), (2, '李四', 30)]
# 你得手动把元组转成 Python 对象
```

用 ORM（SQLAlchemy）：
```python
# 用 Python 类和对象来操作数据库
user = User(name="张三", age=25)
session.add(user)                    # ← 自动生成 INSERT SQL
session.commit()

users = session.query(User).filter(User.age > 18).all()
# users 是 User 对象列表 — 直接就能用！ users[0].name → "张三"
```

> **ORM 的核心思想**：把数据库表映射成 Python 类，把行映射成对象。你操作对象，ORM 自动生成 SQL。

---

## 4. SQLAlchemy 三步走

### 第 1 步：创建引擎和基类

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

# 创建引擎 — 指定数据库文件路径
engine = create_engine(
    "sqlite:///myapp.db",            # 文件路径（项目根目录下的 myapp.db）
    echo=False,                       # True=打印每条 SQL（调试用）
    connect_args={"check_same_thread": False},  # SQLite 特殊参数，照抄
)

# 创建基类 — 所有 ORM 模型都继承它
class Base(DeclarativeBase):
    pass
```

### 第 2 步：定义 ORM 模型（= 数据库表）

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer

class User(Base):                    # ← 继承 Base
    __tablename__ = "users"          # ← 表名

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[int] = mapped_column(Integer, default=0)
    #               ↑ 数据库列类型           ↑ 列约束
```

这个 Python 类**等价于**这样一张数据库表：

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    age INTEGER DEFAULT 0
);
```

### 第 3 步：建表

```python
# 根据所有 Base 的子类，自动生成 CREATE TABLE 语句并执行
Base.metadata.create_all(bind=engine)
# 如果表已经存在，不会重复创建；如果不存在，创建新表
```

---

## 5. 会话（Session）— 操作数据库的入口

Session 是你和数据库之间的**对话窗口**：

```python
# 开启一个会话
with Session(engine) as session:
    # 在这个 with 块里，所有数据库操作通过 session 完成
    user = User(name="张三", age=25)
    session.add(user)        # 加入待办列表（还没写入数据库）
    session.commit()          # 一次性提交所有待办 → 写入数据库
# with 块结束，session 自动关闭
```

Session 的三个关键方法：

| 方法 | 做什么 | 什么时候用 |
|------|--------|-----------|
| `session.add(obj)` | 把对象加入"待插入"队列 | 创建新记录时 |
| `session.commit()` | 把所有待办操作写入数据库 | 确认修改时 |
| `session.refresh(obj)` | 从数据库重新读取这个对象 | 需要获取数据库生成的 id 等值时 |

---

## 6. CRUD 核心操作

### Create（创建）

```python
with Session(engine) as session:
    user = User(name="张三", age=25)   # 1. 创建 Python 对象
    session.add(user)                  # 2. 加入待办
    session.commit()                   # 3. 写入数据库
    session.refresh(user)              # 4. 刷新（获取数据库生成的 id）
    print(user.id)                     # 5. 现在有 id 了
```

### Read（查询）

```python
with Session(engine) as session:
    # 查单个（按主键）
    user = session.get(User, 1)        # SELECT * FROM users WHERE id = 1

    # 查全部
    all_users = session.query(User).all()

    # 条件过滤
    adults = session.query(User).filter(User.age >= 18).all()

    # 排序 + 限制
    top3 = session.query(User).order_by(User.age.desc()).limit(3).all()
```

### Update（更新）

```python
with Session(engine) as session:
    user = session.get(User, 1)
    if user:
        user.name = "张三丰"           # 直接修改属性
        session.commit()               # 提交 → UPDATE SQL 自动生成
```

### Delete（删除）

```python
with Session(engine) as session:
    user = session.get(User, 1)
    if user:
        session.delete(user)           # 标记删除
        session.commit()               # 提交 → DELETE SQL 自动生成
```

---

## 7. 和 FastAPI 对接

把数据库和 FastAPI 连起来的关键是：**在接口函数里获取 Session**。

```python
def get_session():
    """FastAPI 依赖 — 每个请求一个数据库会话"""
    with Session(engine) as session:
        yield session
        # yield 之后，请求处理完自动关闭 session

@app.post("/users", status_code=201)
def create_user(user: UserCreate, session=Depends(get_session)):
    db_user = User(name=user.name, age=user.age)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
```

---

## 8. Pydantic 模型 vs ORM 模型

> 这是初学者最容易混淆的概念，专门拿出来说。

| | Pydantic 模型 | SQLAlchemy ORM 模型 |
|---|---|---|
| **用途** | 校验 HTTP 请求/响应的数据 | 定义数据库表结构 |
| **继承** | `BaseModel` | `Base`（DeclarativeBase） |
| **定义的是** | 数据的"形状"（Shape） | 数据库的"表"（Table） |
| **在哪里用** | 接口函数的参数和返回值 | Session 操作 |
| **变数据库表？** | ❌ 不变 | ✅ `Base.metadata.create_all()` 会建表 |

它们经常**同名**但**不同类**：

```python
# Pydantic 模型 — API 层
class UserCreate(BaseModel):
    name: str
    age: int

# ORM 模型 — 数据库层
class User(Base):             # ← 不同的父类！
    __tablename__ = "users"
    id: Mapped[int] = ...
    name: Mapped[str] = ...
```

---

## 9. 常见错误

### ❌ 忘记 commit

```python
session.add(user)
# 忘记 session.commit()   ← 数据没写入数据库！
```

### ❌ 忘记 refresh 就拿 id

```python
user = User(name="张三")
session.add(user)
session.commit()
print(user.id)   # ❌ 可能是 None！
session.refresh(user)
print(user.id)   # ✅ 现在有值了
```

### ❌ 在 session 之外访问 ORM 对象

```python
with Session(engine) as session:
    user = session.get(User, 1)
# with 块结束，session 关闭了

print(user.name)   # ❌ 可能报错（session 已关闭）
```

---

## 10. 自己动手

1. 运行 code.py，用 `/docs` 创建几个用户
2. 关闭服务器，再重新启动 → 数据还在！（因为存在了 .db 文件里）
3. 在项目目录找到 `s06_app.db` 文件，这就是你的数据库
4. 用 `/docs` 试试：创建 → 查列表 → 更新 → 删除
5. 注意观察终端里的 SQL 日志（code.py 里 `echo=True` 会打印每条 SQL）
