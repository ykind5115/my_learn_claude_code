# s05: 数据校验 — 用 Field() 给数据加上约束

s01 → ... → s04 → `s05` → [s06](../s06_crud_repository/) → ... → s17
> *"Pydantic 不只是声明类型。Field() 让你精确控制每个字段的约束 — 长度、范围、格式，全自动校验。"*
>
> **前提知识**: s04（会用 Pydantic BaseModel 接收 POST 数据）。

---

## 1. 为什么 s04 的校验不够？

s04 的模型只做了类型校验：

```python
class UserCreate(BaseModel):
    name: str      # 只要求是字符串 — 但空字符串 "" 也能通过
    age: int       # 只要求是整数 — 但 -999 也能通过
    email: str     # 只要求是字符串 — 但 "not-an-email" 也能通过
```

真实项目需要更严格的校验：
- `name` 不能为空，最长 50 个字符
- `age` 必须在 0-150 之间
- `email` 必须符合邮箱格式
- `password` 至少 6 位

---

## 2. `Field()` — 给字段加约束

```python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    name: str = Field(
        ...,                          # ... 表示必填
        min_length=1,                 # 最少 1 个字符
        max_length=50,                # 最多 50 个字符
        description="用户名",          # 出现在 /docs 里
    )
    age: int = Field(
        ...,
        ge=0,                         # greater or equal — >= 0
        le=150,                       # less or equal — <= 150
    )
    email: str = Field(
        ...,
        min_length=5,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        # pattern: 正则表达式校验 — 拒绝明显不是邮箱的字符串
    )
```

### `Field()` 常用参数一览

| 参数 | 含义 | 适用类型 | 例子 |
|------|------|---------|------|
| `...` | 必填（和没有默认值等价） | 全部 | `Field(...)` |
| `default` | 默认值 | 全部 | `Field(default=0)` |
| `ge` / `le` | ≥ 和 ≤ | int, float | `Field(ge=0, le=100)` |
| `gt` / `lt` | > 和 < | int, float | `Field(gt=0)` |
| `min_length` / `max_length` | 字符串长度范围 | str | `Field(min_length=1)` |
| `pattern` | 正则表达式 | str | `Field(pattern=r"^\d+$")` |
| `description` | 字段描述（显示在 /docs） | 全部 | `Field(description="用户名")` |
| `examples` | 示例值（显示在 /docs） | 全部 | `Field(examples=["zhangsan"])` |

---

## 3. 校验失败时发生了什么？

当你传了不合法的数据，FastAPI 返回 **422 Unprocessable Entity**：

```json
// 请求: POST /users   Body: {"name": "", "age": 200}
// 响应: 422

{
    "detail": [
        {
            "type": "string_too_short",
            "loc": ["body", "name"],
            "msg": "String should have at least 1 character",
            "input": ""
        },
        {
            "type": "less_than_equal",
            "loc": ["body", "age"],
            "msg": "Input should be less than or equal to 150",
            "input": 200
        }
    ]
}
```

注意 `detail` 是一个**数组** — 它列出了**所有**不合法的字段，而不仅仅是第一个。这样前端就能一次显示所有错误。

---

## 4. 枚举字段 — 限定可选值

有些字段只能取特定的几个值：

```python
from enum import Enum

class OrderStatus(str, Enum):
    pending = "pending"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class OrderCreate(BaseModel):
    status: OrderStatus = OrderStatus.pending   # 默认是 pending
```

传 `"shipped"` ✅ | 传 `"unknown"` ❌ 422

---

## 5. 嵌套模型的校验

s04 学了嵌套模型。校验同样递归进行：

```python
class Address(BaseModel):
    province: str = Field(..., min_length=2)
    city: str = Field(..., min_length=2)
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")  # 手机号

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    address: Address     # ← 嵌套 — Address 的校验规则也会执行
```

如果 `address.phone` 格式不对，同样返回 422，并且错误信息会指出是 `body → address → phone` 的问题。

---

## 6. `model_validator` — 跨字段校验

有时候校验不是针对单个字段，而是**多个字段之间的关系**。比如"结束日期不能早于开始日期"：

```python
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start_date: str
    end_date: str

    @model_validator(mode="after")
    def check_dates(self):
        """在所有字段校验完成后，再检查它们之间的关系"""
        if self.start_date > self.end_date:
            raise ValueError("end_date 不能早于 start_date")
        return self
```

`model_validator` 在单字段校验**之后**运行。你可以在这里做任意复杂的逻辑判断。

---

## 7. 常见错误

### ❌ 以为有默认值就一定有校验

```python
age: int = 0   # 默认值是 0，但客户端传 -999 也能通过！
age: int = Field(default=0, ge=0)   # ✅ 加了 ge=0，负数会被拒绝
```

### ❌ pattern 写错导致所有合法值都被拒绝

```python
# 正则表达式写错了会拒绝所有输入
email: str = Field(..., pattern=r"^.+@.+$")  # 简单的邮箱正则
# 注意: FastAPI/Pydantic 用的是 Python re 模块的语法
```

### ❌ 把 Pydantic Field 和 SQLAlchemy Column 搞混

这两个是完全不同的东西 — 虽然名称相似：
- Pydantic `Field()` → API 层的数据校验（s04-s05）
- SQLAlchemy `Column()` → 数据库层的列定义（s06）

---

## 8. 自己动手

1. 给 s04 的 UserCreate 模型加上 Field() 校验：name 1-50 字符、age 0-150、email 的 pattern
2. 故意传越界数据，观察 422 错误 — 注意它同时列出所有不合规的字段
3. 写一个 `model_validator`，校验"确认密码"和"密码"是否一致
4. 用一个枚举字段定义用户角色（admin/editor/user），限制只能选这三个
