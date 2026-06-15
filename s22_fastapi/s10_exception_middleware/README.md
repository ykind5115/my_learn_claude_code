# s10: 统一响应封装 — 所有接口返回 `{code, message, data}`

s01 → ... → s09 → `s10` → [s11](../s11_jwt_auth/) → ... → s17
> *"前端不关心你内部怎么处理 — 它只想用一个统一的格式解析所有接口的返回。"*
>
> **前提知识**: s09（知道怎么拆分路由模块）。

---

## 1. 问题：每个接口返回格式都不一样

目前你的接口返回格式五花八门：

```python
@app.get("/users")       # → [{...}, {...}]    列表
@app.get("/users/{id}")  # → {...}             对象
@app.post("/users")      # → {...}             对象
@app.delete("/users/{id}") # → (空)            204
```

前端要针对每个接口写不同的解析逻辑。更糟的是，出错了怎么办？
- 有的错误是 FastAPI 自动生成的 `{"detail": "..."}`
- 有的错误是自定义的 `{"error": "..."}`
- 前端根本不知道从哪里取错误信息

---

## 2. 解决方案：约定一个统一格式

定义一个规范，所有接口（成功和失败）都遵守：

```json
// 成功
{
    "code": 20000,
    "message": "success",
    "data": { ... }
}

// 失败
{
    "code": 40400,
    "message": "用户不存在",
    "data": null
}
```

- **code**：业务状态码（`20000` = 成功，`4xxxx` = 客户端错误，`5xxxx` = 服务器错误）
- **message**：给人看的提示文字
- **data**：实际数据，失败时为 null

> **注意**：`code` 是**业务状态码**，和 HTTP 状态码是两回事。HTTP 200 可以携带 `code: 40001`（请求参数错误）。

---

## 3. 怎么实现

### 第 1 步：定义统一响应类

```python
from pydantic import BaseModel

class ApiResponse(BaseModel):
    code: int = 20000
    message: str = "success"
    data: Any = None

    @classmethod
    def success(cls, data=None, message="success"):
        """工厂方法：创建成功响应"""
        return cls(code=20000, message=message, data=data)

    @classmethod
    def error(cls, code: int, message: str):
        """工厂方法：创建错误响应"""
        return cls(code=code, message=message, data=None)
```

### 第 2 步：在接口里用

```python
@app.get("/users/{id}")
def get_user(id: int) -> ApiResponse:
    user = find_user(id)
    if user:
        return ApiResponse.success(data=user)
    else:
        return ApiResponse.error(code=40400, message="用户不存在")
```

---

## 4. 定义业务状态码枚举

```python
from enum import IntEnum

class StatusCode(IntEnum):
    SUCCESS = 20000
    BAD_REQUEST = 40000
    UNAUTHORIZED = 40100
    FORBIDDEN = 40300
    NOT_FOUND = 40400
    CONFLICT = 40900
    VALIDATION_ERROR = 42200
    INTERNAL_ERROR = 50000

# 使用
raise AppException(StatusCode.NOT_FOUND, "用户不存在")
```

---

## 5. 进阶：用异常处理器自动包装

不手动调 `ApiResponse.success()`，而是让异常处理器自动把所有响应包进统一格式。这样接口函数可以返回原始数据，中间件负责包装。

s11 会详细讲异常处理器。

---

## 6. 常见错误

### ❌ 业务状态码和 HTTP 状态码混淆

```python
# HTTP 200 但内容表示"错误" — 这在某些 API 设计中是故意的
# 因为有些客户端/CDN 会吞掉非 200 的响应体

return JSONResponse(
    status_code=200,   # HTTP 层面是 200
    content={"code": 40001, "message": "参数错误"}  # 业务层面是错误
)
```

### ❌ 不定义枚举，用魔法数字

```python
# ❌ 不好的做法
if error_type == "not_found":
    return {"code": 40400, ...}   # 散布在各处的数字

# ✅ 好的做法
from status_codes import StatusCode
return ApiResponse.error(StatusCode.NOT_FOUND, "用户不存在")
```

---

## 7. 自己动手

1. 实现一个 `ApiResponse` 类，有 `success()` 和 `error()` 两个工厂方法
2. 定义至少 5 个业务状态码（成功、参数错、未登录、无权限、不存在）
3. 改造一个 s08 的路由，让它返回统一格式
