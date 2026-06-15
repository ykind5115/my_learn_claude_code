# s01: 第一个接口 — 让后端跑起来

s00 → `s01` → [s02](../s02_pydantic_models/) → s03 → ... → s17
> *"三行代码，让浏览器访问到你的 Python 函数。"*
>
> **前提知识**: 看过 s00（知道 HTTP、JSON、URL 是什么）。会打开终端，会 `pip install`。

---

## 1. 为什么需要 FastAPI？

回顾 s00 那张图：

```
浏览器  →  服务器  →  你的 Python 函数  →  服务器  →  浏览器
         (Uvicorn)     (你写的代码)        (Uvicorn)
```

**问题是**：如果不用框架，你得自己写代码来：
- 监听 8000 端口（接收 TCP 连接）
- 解析 HTTP 请求文本（把那一大段原始文本拆成方法、路径、头、Body）
- 把 URL 匹配到对应的 Python 函数
- 把函数的返回值转成 HTTP 响应文本
- 加上正确的 Content-Type 头

自己写要几百行。FastAPI 帮你做了**除了"你的业务逻辑"之外的所有事**。

---

## 2. 最小可运行的后端 — 逐行解释

```python
from fastapi import FastAPI          # 第 1 行

app = FastAPI()                      # 第 2 行

@app.get("/")                        # 第 3 行
def root():                          # 第 4 行
    return {"message": "Hello!"}     # 第 5 行
```

### 逐行解释：

**第 1 行** `from fastapi import FastAPI`
- 从安装的 `fastapi` 包里，导入 `FastAPI` 这个类。
- FastAPI 是一个**类**（class），你创建一个实例，就创建了一个"应用"。

**第 2 行** `app = FastAPI()`
- 创建应用实例。这个 `app` 变量是你整个后端的**入口**。
- 后面所有的路由、中间件、异常处理都注册在这个 `app` 上。
- 你可以理解为：`app` = 你的整个 API 服务。

**第 3 行** `@app.get("/")`
- 这是一个**装饰器**（decorator）。它的作用是：**把下面这个函数注册为处理 `GET /` 请求的处理器**。
- `"/"` 是根路径。浏览器访问 `http://localhost:8000/` 时，FastAPI 就调用这个函数。
- `@app.get` 是 FastAPI 提供的方法，`get` 对应 HTTP 的 GET 方法。

> **什么是装饰器？**
> `@app.get("/")` 等价于 `root = app.get("/")(root)`。
> 它把 `root` 函数"包装"了一下，让 FastAPI 知道：
> "当有人用 GET 方法访问 `/` 路径时，就调用 root 函数"

**第 4 行** `def root():`
- 一个普通的 Python 函数。名字可以随便取，叫 `root`、`hello`、`index` 都行。
- **函数名不会出现在 URL 里**。决定 URL 的是 `@app.get("/")` 里的字符串。

**第 5 行** `return {"message": "Hello!"}`
- 返回一个 Python 字典。FastAPI **自动把它转成 JSON**：`{"message": "Hello!"}`
- 同时自动设置 HTTP 状态码为 200（成功）。
- 同时自动设置 `Content-Type: application/json` 响应头。

> **FastAPI 帮你做的三件事**：
> 1. 把 `dict` → JSON 字符串
> 2. 设置 HTTP 200 状态码
> 3. 设置 `Content-Type: application/json`

---

## 3. 启动服务器

写到这，你的代码还不能被浏览器访问。你需要一个**服务器程序**来接收 HTTP 请求，交给 FastAPI 处理。

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 逐行解释：

**`if __name__ == "__main__":`**
- 表示"只有直接执行这个文件时才运行下面的代码"。
- 如果别的文件 import 了这个文件，下面的代码不会执行。

**`import uvicorn`**
- uvicorn 是一个 **ASGI 服务器**。它负责：
  - 监听端口（port 8000）
  - 接收 HTTP 连接
  - 把请求解析后交给 FastAPI
  - 把 FastAPI 的响应发回浏览器
- 没有 uvicorn，FastAPI 就是一堆没通电的代码。

**`uvicorn.run(app, host="0.0.0.0", port=8000)`**
- `app`：要运行哪个 FastAPI 应用
- `host="0.0.0.0"`：监听所有网络接口（局域网内其他设备也能访问）
  - 如果只想本机访问，改成 `"127.0.0.1"`
- `port=8000`：监听 8000 端口
  - 端口号可以是 8000-9000 之间的任意值，只要不冲突

**启动后你应该看到**：
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 4. 在浏览器里验证

打开浏览器，访问：
- `http://localhost:8000` — 看到 `{"message":"Hello!"}` ✅
- `http://localhost:8000/docs` — 看到自动生成的 API 文档页面 ✅
- `http://localhost:8000/openapi.json` — 看到原始的 OpenAPI 描述文件

### Swagger UI（`/docs`）是什么？

```
┌─────────────────────────────────────────────┐
│  Swagger UI — FastAPI 自动生成的交互式文档    │
│                                             │
│  GET /                           [Try it out] │ ← 点 "Try it out" 可以实际调用接口
│  ────────────────                            │
│  Response:                                   │
│    { "message": "Hello!" }                   │
└─────────────────────────────────────────────┘
```

FastAPI 根据你写的代码**自动生成**了这个文档：
- 路径从 `@app.get("/")` 来
- 请求/响应格式从函数参数和返回值推断
- 不需要写任何额外的文档代码

---

## 5. 加更多路由

一个后端不可能只有一个接口。加一个路由只需要再加一个函数：

```python
@app.get("/hello")         # 访问 http://localhost:8000/hello
def say_hello():
    return {"message": "你好，世界！"}

@app.get("/status")        # 访问 http://localhost:8000/status
def server_status():
    return {"status": "running", "version": "1.0"}
```

每个路由 = 一个 `@app.xxx(path)` + 一个函数。函数之间完全独立。

---

## 6. 路径参数：URL 里的变量

很多时候，URL 里包含一个 ID：

```
/users/42    ← 查看 42 号用户
/users/99    ← 查看 99 号用户
```

不可能为每个 ID 写一个路由。用 `{变量名}` 来匹配：

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):         # ← 参数名和 URL 里的 {user_id} 对应
    return {"user_id": user_id}
```

**注意** `user_id: int` — FastAPI 会：
1. 从 URL 里提取 `"42"`
2. 发现它是一个字符串
3. 看到你的类型提示是 `int`
4. 自动把 `"42"` 转成整数 `42`
5. 如果 URL 里是 `"abc"`，直接返回 422 错误（"abc" 不是 int）

> **如果你写 `user_id: str`**（不写 int），FastAPI 就不会做转换，`user_id` 就是一个字符串 `"42"`。

---

## 7. 常见错误（新手必读）

### ❌ 错误 1：改了代码但浏览器没变化

```bash
# 原因：服务器没有重启。Ctrl+C 停止，重新运行 python code.py
```

> 进阶技巧：启动时加 `reload=True`，代码变更会自动重启：
> `uvicorn.run(app, reload=True)`

### ❌ 错误 2：`Port 8000 already in use`

```bash
# 原因：上次的进程没关掉，端口被占用了
# 解决：找到并杀掉占用进程
# Windows: netstat -ano | findstr :8000  → 拿到 PID → taskkill /PID xxx /F
# Mac/Linux: lsof -i :8000 → kill -9 xxx
```

### ❌ 错误 3：浏览器访问 localhost 连不上

```
# 检查:
1. 服务器启动了吗？（终端里有没有 "Uvicorn running on..."）
2. 端口号对不对？（浏览器和代码里的 port=8000 一致吗）
3. 防火墙有没有拦截？
```

### ❌ 错误 4：`@app.get("/users/{user_id}")` 但函数参数名不一致

```python
@app.get("/users/{user_id}")   # URL 里叫 user_id
def get_user(id: int):         # ❌ 函数参数叫 id，不匹配！
    ...

# 修复：URL 里的变量名和函数参数名必须一致
def get_user(user_id: int):    # ✅
```

---

## 8. 你学到了什么（对照 s00 的概念）

| s00 概念 | s01 对应的代码 |
|----------|---------------|
| HTTP GET 请求 | `@app.get(...)` |
| URL 路径 | 装饰器里的字符串 `"/"` `"/hello"` `"/users/{id}"` |
| 状态码 200 | FastAPI 自动设置（函数正常 return 就是 200） |
| JSON 响应 | `return {"key": "value"}` 自动变成 JSON |
| 服务器 | `uvicorn.run(app)` |

---

## 9. 自己动手

1. **基础练习**：在 `code.py` 里加一个新路由 `GET /ping`，返回 `{"pong": true}`
2. **路径参数**：加一个路由 `GET /greet/{name}`，访问 `/greet/张三` 返回 `{"hello": "张三"}`
3. **观察**：访问 `http://localhost:8000/docs`，看看新加的路由是不是自动出现在文档里了
4. **故意犯错**：访问 `/greet/`（不传 name），看看 FastAPI 返回什么错误
5. **修改端口**：把 `port=8000` 改成 `port=9000`，重启后用 `localhost:9000` 访问
