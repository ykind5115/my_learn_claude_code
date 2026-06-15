# s11: 异常与中间件 — 错误统一处理，请求自动拦截

s01 → ... → s10 → `s11` → [s12](../s12_rbac_permission/) → ... → s17
> *"异常处理器是最后一道防线 — 任何未捕获的错误都变成体面的 JSON。中间件是请求的第一道门 — 日志、CORS、限流在这里做。"*
>
> **前提知识**: s10（有了统一响应格式）。

---

## 1. 异常处理器：把崩溃变成 500

没有异常处理器的后果：一个不小心出了 bug → 服务器返回丑陋的 HTML/空白页 → 前端报错也不知道原因。

FastAPI 的 `@app.exception_handler()` 让你**定义每种异常的处理方式**：

```python
@app.exception_handler(HTTPException)
async def http_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": 40000, "message": exc.detail},
    )

@app.exception_handler(Exception)
async def global_handler(request, exc):
    # 任何未预料的异常都会到这 → 返回统一的 500 错误
    return JSONResponse(
        status_code=500,
        content={"code": 50000, "message": "服务器内部错误"},
    )
```

---

## 2. 异常处理的三层金字塔

```
┌──────────────────────────────────┐
│ 第 1 层: HTTPException 处理器     │  ← 最高优先级
│ (404, 401, 403, 422...)          │
├──────────────────────────────────┤
│ 第 2 层: 自定义异常处理器          │
│ (AppException — 业务异常)        │
├──────────────────────────────────┤
│ 第 3 层: Exception 兜底处理器     │  ← 最低优先级
│ (任何未预料的异常)                │
└──────────────────────────────────┘
```

FastAPI 按优先级匹配：先看有没有具体的，没有再找通用的。

---

## 3. 中间件是什么？

中间件是一个在**每个请求**前后自动执行的函数：

```python
@app.middleware("http")
async def my_middleware(request: Request, call_next):
    # ===== 请求进来时（路由执行前）=====
    start = time.time()
    
    response = await call_next(request)  # ← 执行后续中间件和路由函数
    
    # ===== 响应出去时（路由执行后）=====
    duration = time.time() - start
    response.headers["X-Process-Time"] = f"{duration:.3f}s"
    return response
```

---

## 4. CORS 中间件 — 解决跨域问题

前端在 `localhost:3000`，后端在 `localhost:8000` — 浏览器默认阻止这种跨域请求。CORS 中间件一行配置解决：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许哪些前端来源
    allow_credentials=True,
    allow_methods=["*"],                       # 允许的 HTTP 方法
    allow_headers=["*"],                       # 允许的请求头
)
```

> 学习阶段用 `allow_origins=["*"]`（允许所有来源）。生产环境要限制为具体域名。

---

## 5. 常见的中间件场景

| 中间件 | 做什么 | 在哪个阶段 |
|--------|--------|-----------|
| CORS | 加跨域头 | 请求前 + 响应后 |
| 请求日志 | 记录方法、路径、耗时 | 请求前 + 响应后 |
| 限流 | 限制每个 IP 的请求频率 | 请求前 |
| 安全头 | 加 X-Frame-Options 等 | 响应后 |
| GZip | 压缩响应体 | 响应后 |

---

## 6. 中间件 vs 异常处理器 vs Depends

| 机制 | 作用范围 | 执行时机 | 典型用途 |
|------|---------|---------|---------|
| **中间件** | 所有请求 | 最外层 | CORS、日志、限流 |
| **异常处理器** | 所有请求 | 出错时 | 统一错误格式 |
| **Depends** | 指定路由 | 路由函数前 | 认证、分页、数据库会话 |

---

## 7. 常见错误

### ❌ 中间件吃掉了异常

```python
# ❌ 中间件里用了 try-except 吞掉了异常
async def bad_middleware(request, call_next):
    try:
        return await call_next(request)
    except Exception:
        pass  # 异常消失了！异常处理器收不到它
```

### ❌ 异常处理器里又抛异常

```python
# ❌ 异常处理器里又抛异常 → FastAPI 不知道怎么处理
@app.exception_handler(Exception)
async def handler(request, exc):
    raise HTTPException(500, "error")  # 异常套异常
```

---

## 8. 自己动手

1. 给 s10 的 code.py 加一个全局异常处理器，把未捕获的错误转为 ApiResponse
2. 加一个请求日志中间件，打印每个请求的方法、路径和耗时
3. 加 CORS 中间件
4. 写一个会故意抛 RuntimeError 的接口 `/crash`，看异常处理器有没有工作
