# s00: HTTP 与后端基础 — 建立心智模型

s00 → [s01](../s01_hello_fastapi/) → s02 → ... → s17
> *"在写代码之前，先理解：当你在浏览器输入一个网址，背后发生了什么。"*
>
> 这一章**不写代码**。目的是帮你建立一张"地图"——后面每一章都是这张地图上的一个点。

---

## 1. 前端 vs 后端：两个世界

互联网应用分为两部分：

```
┌─────────────────────────┐      ┌─────────────────────────┐
│        前端              │      │         后端             │
│  (Frontend)             │      │  (Backend)              │
│                         │      │                         │
│  运行在你的浏览器里       │ HTTP │  运行在远程服务器上       │
│  负责界面：按钮、表单、样式 │ ←──→ │  负责数据：存取、计算、逻辑 │
│  技术: HTML/CSS/JS       │      │  技术: Python/Java/Go等  │
│                         │      │                         │
│  你看到的                │      │  你看不到的              │
└─────────────────────────┘      └─────────────────────────┘
```

举个例子：你在淘宝搜索"机械键盘"

- **前端**做的事：显示搜索框、把"机械键盘"四个字发给后端、把返回的商品列表渲染成页面
- **后端**做的事：收到"机械键盘"四个字、去数据库里查、过滤排序、返回结果

> **后端 = 你看不到的那个"服务生"**。你在桌上（浏览器）点菜（发请求），服务生去后厨（数据库）取菜，端回来给你。

---

## 2. HTTP：前后端之间的语言

HTTP（HyperText Transfer Protocol）就是前端和后端之间**约定的通信格式**。

### 一个完整的 HTTP 请求长这样：

```
POST /api/login HTTP/1.1               ← 请求行：方法 + 路径 + 协议版本
Host: example.com                       ← 请求头（Headers）：附加信息
Content-Type: application/json         ← 告诉服务器"我发的是 JSON"
Authorization: Bearer xxxxxxxx         ← 身份凭证

{"username": "zhangsan", "password": "123456"}  ← 请求体（Body）：实际数据
```

### 服务器收到后返回：

```
HTTP/1.1 200 OK                         ← 状态行：协议版本 + 状态码 + 描述
Content-Type: application/json          ← 响应头：告诉客户端"我回的是 JSON"

{"code": 200, "message": "success", "token": "xxx"}  ← 响应体：实际数据
```

### 拆解 HTTP 的四个部分：

| 部分 | 是什么 | 类比 |
|------|--------|------|
| **方法 (Method)** | 你要做什么 | 动词：GET=查询, POST=创建, PUT=更新, DELETE=删除 |
| **路径 (Path)** | 你要操作什么资源 | `/users`、`/orders/123` |
| **头部 (Headers)** | 附加信息 | 身份凭证、数据格式说明、缓存指令 |
| **体 (Body)** | 实际传输的数据 | JSON 格式的用户信息、订单信息等 |

---

## 3. HTTP 方法：四个动词

就像说话有"请给我"、"请拿走"、"请修改"、"请删除"——

| 方法 | 含义 | 什么时候用 | 有 Body 吗？ |
|------|------|-----------|-------------|
| **GET** | 查询（读取） | 看用户列表、搜商品、看一篇文章 | ❌ 没有 |
| **POST** | 创建（新增） | 注册、登录、下单 | ✅ 有 |
| **PUT** | 更新（全量替换） | 修改整条用户信息 | ✅ 有 |
| **PATCH** | 更新（部分修改） | 只改昵称 | ✅ 有 |
| **DELETE** | 删除 | 删用户、删订单 | ❌ 通常没有 |

> **一个重要的区别**：
> - GET 请求把参数放在 URL 里：`/search?keyword=机械键盘&page=1`
> - POST 请求把参数放在 Body 里：一大段 JSON

---

## 4. HTTP 状态码：服务器在说什么

每次服务器返回，都会带一个三位数字，告诉前端"结果怎么样了"：

| 状态码范围 | 含义 | 常见例子 |
|-----------|------|---------|
| **2xx** | 成功 | `200 OK`（成功）、`201 Created`（创建成功）、`204 No Content`（删除成功，没东西返回） |
| **3xx** | 重定向 | `301 Moved Permanently`（永久搬家了）、`302 Found`（临时去别处） |
| **4xx** | 客户端错误（你搞错了） | `400 Bad Request`（请求格式不对）、`401 Unauthorized`（没登录）、`403 Forbidden`（没权限）、`404 Not Found`（不存在） |
| **5xx** | 服务器错误（我挂了） | `500 Internal Server Error`（服务器崩了）、`502 Bad Gateway`（网关错误） |

> **记法**：4 开头 = 你的问题，5 开头 = 服务器的问题。

---

## 5. JSON：数据的通用格式

JSON（JavaScript Object Notation）是前后端之间**传数据的标准格式**。它只有几种类型：

```json
{
    "name": "张三",              // 字符串
    "age": 25,                   // 数字
    "is_active": true,           // 布尔
    "hobbies": ["编程", "篮球"],  // 数组
    "address": {                 // 嵌套对象
        "city": "北京",
        "street": "长安街 100 号"
    },
    "phone": null                // 空值
}
```

> **为什么用 JSON？**
> 因为它是纯文本 — 任何语言都能读。Python 的 `json.dumps()` 和 `json.loads()` 天生支持它。

---

## 6. URL 的结构

一个完整的 URL 长这样：

```
https://www.example.com:443/api/users/42?active=true&page=1#section
└─┬─┘ └──────┬──────┘ └┬┘ └─────┬──────┘ └───────┬───────┘ └──┬──┘
 scheme    host       port   path            query string    fragment
 协议      主机       端口   路径             查询参数         锚点
```

我们主要关心的部分：

| 部分 | 含义 | 例子 |
|------|------|------|
| **host** | 服务器地址 | `www.baidu.com` |
| **port** | 哪个门（默认 80/443 可省略） | `:8000` |
| **path** | 你要访问服务器上的哪个资源 | `/api/users/42` |
| **query string** | 附加的过滤条件 | `?page=1&size=20` |

> 在 FastAPI 中：
> - `{user_id}` 这种是**路径参数** — 定位"哪一个"资源
> - `?page=1` 这种是**查询参数** — 过滤/分页/排序

---

## 7. API 是什么？

API（Application Programming Interface）= **应用程序编程接口**。

通俗说：API 就是后端**开放给前端调用的功能列表**。

```
前端: "后端，我要查用户 42 的信息"
后端: "好的，调用 GET /api/users/42，这是约定好的接口"
```

REST API 是目前最流行的 API 风格。它的核心思想：

1. **用 URL 路径表示资源**：`/users` = 用户集合，`/users/42` = 42 号用户
2. **用 HTTP 方法表示操作**：GET = 查，POST = 增，PUT/PATCH = 改，DELETE = 删
3. **无状态**：每个请求独立，服务器不记住上次你做了什么（要靠 token/session）

FastAPI 就是用来**快速构建 REST API** 的 Python 框架。

---

## 8. FastAPI 在这张地图上的位置

```
浏览器（前端）
    │
    │  HTTP 请求（GET /users?active=true）
    ▼
┌──────────────────┐
│  Nginx（反向代理） │  ← 可选，负责 SSL、负载均衡
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Uvicorn（服务器） │  ← 接收 HTTP 请求，转给 FastAPI
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    FastAPI       │  ← ★ 这就是我们写的代码 ★
│                  │     处理请求、校验参数、调用数据库、返回响应
│  你的函数:        │
│  def list_users() │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    数据库         │  ← SQLite / PostgreSQL / MySQL
└──────────────────┘
```

> FastAPI 的角色：**请求 → 你的函数 → 响应** 这个过程中的框架。它帮你做参数校验、JSON 转换、文档生成，你的函数只需要关心业务逻辑。

---

## 9. 一个请求的完整旅程

以"在浏览器里打开 `http://localhost:8000/users/42?include_orders=true`"为例：

```
Step 1: 你在浏览器地址栏输入 URL，回车
        ↓
Step 2: 浏览器构造一个 HTTP GET 请求，发给 localhost:8000
        ↓
Step 3: Uvicorn 收到请求，转给 FastAPI
        ↓
Step 4: FastAPI 看 URL: /users/42 → 匹配到 @app.get("/users/{user_id}")
        ↓
Step 5: FastAPI 提取参数: user_id=42, include_orders=True
        ↓
Step 6: FastAPI 调用你的函数: get_user(user_id=42, include_orders=True)
        ↓
Step 7: 你的函数查数据库，返回 {"id": 42, "name": "张三"}
        ↓
Step 8: FastAPI 把 dict 自动转成 JSON 字符串
        ↓
Step 9: 加上 HTTP 状态码 200、Content-Type: application/json
        ↓
Step 10: Uvicorn 把响应发回浏览器
        ↓
Step 11: 浏览器收到 JSON，显示在页面上
```

> 后续每一章就是在这个流程的**某个环节**上做文章：
> - s01：写第 6 步的函数
> - s03：搞懂第 5 步的参数提取
> - s04：处理 POST 请求的 Body
> - s06：打通第 7 步的数据库
> - s12：在第 5 步之前加身份验证
> - ...

---

## 10. 动手之前：安装准备

确认你已经装好这些：

```bash
# 1. 确认 Python 版本 >= 3.10
python --version

# 2. 安装 FastAPI 全家桶
pip install fastapi uvicorn[standard]

# 3. 验证安装
python -c "import fastapi; print(fastapi.__version__)"
python -c "import uvicorn; print('uvicorn OK')"
```

如果都 OK，进入 [s01](../s01_hello_fastapi/) 开始写你人生中第一个后端接口！

---

## 本章要点总结

| 概念 | 一句话 |
|------|--------|
| 前端 vs 后端 | 前端管界面，后端管数据 |
| HTTP | 前后端通信的协议：方法 + 路径 + 头 + 体 |
| GET/POST/PUT/DELETE | 查询 / 创建 / 更新 / 删除 |
| 状态码 | 2xx=成功，4xx=你的错，5xx=服务器的错 |
| JSON | `{"key": "value"}` — 前后端传数据的通用格式 |
| URL | `协议://主机:端口/路径?查询参数` |
| API | 后端提供给前端调用的功能列表 |
| REST API | 用 URL 表示资源 + 用 HTTP 方法表示操作 |
| FastAPI | Python 写 REST API 的框架 |

---

## 自己动手

1. 打开浏览器，按 F12 → Network（网络）标签
2. 访问 `https://jsonplaceholder.typicode.com/users/1`
3. 观察 Network 面板：请求方法是什么？状态码是多少？响应体是什么格式？
4. 再访问 `https://jsonplaceholder.typicode.com/users` — 这次返回了什么区别？
5. 试试 `https://jsonplaceholder.typicode.com/posts?userId=1` — `?userId=1` 起了什么作用？

> 这个 `jsonplaceholder` 是一个免费假 API，你可以随便调。玩玩看，后面的章节就是教你做出这样的东西。
