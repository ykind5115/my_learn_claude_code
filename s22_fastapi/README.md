# s22: FastAPI 后端开发 — 从零到生产级 API

[中文](README.md)

> *"一个路由 + 一个 Schema = 一个 API。剩下的一切都是工程化。"*
>
> 本课程面向**后端零基础**的学习者。不假设你用过任何后端框架。
> 每一章只比上一章多一个概念，每一步都讲清楚「为什么」。
> 最终目标是：学完能独立写出一个带认证、有数据库、结构清晰的生产级 API。

---

## 开始之前：你需要什么基础？

- Python 基础：会写函数、会用 `pip install`、理解 `dict` / `list` / `str` / `int`
- 会用终端（命令行）
- 会用 VS Code 或任何编辑器

> ❓ **完全零基础？** 从 [s00](s00_http_basics/) 开始 — 纯概念，不写代码，帮你建立心智模型。
> 如果你已经知道 HTTP、JSON、前后端分离是什么，可以直接从 s01 开始。

---

## 学习路线图

```
s00  HTTP 与后端基础  ← 纯概念，建立心智模型
 │
s01  第一个接口       ← 从这里开始写代码
s02  返回数据         ← dict → JSON、状态码、/docs
s03  接收参数         ← 路径参数、查询参数
s04  接收请求体       ← POST、JSON body、Pydantic
 │
s05  校验数据         ← Field()、自动 422
s06  连接数据库       ← SQLite、SQLAlchemy 入门
 │
s07  CRUD 完整实现     ← 增删改查、Repository 模式
s08  依赖注入         ← Depends() 原理、认证/DB 注入
 │
s09  路由拆分         ← APIRouter、大型项目结构
s10  统一响应封装      ← {code, message, data} 工厂
s11  异常与中间件      ← 全局错误处理、CORS、日志
 │
s12  JWT 认证         ← 登录/注册、Token、OAuth2
s13  权限控制         ← RBAC、角色-权限模型
 │
s14  后台任务         ← BackgroundTasks、文件上传
s15  WebSocket        ← 实时双向通信
s16  测试             ← TestClient、pytest
s17  部署             ← Docker、gunicorn、生产检查清单
```

---

## 模块总览

### 🧭 第 0 章：认知基础

| # | 模块 | 要解决的问题 | 不写代码 |
|---|------|-------------|---------|
| s00 | [HTTP 与后端基础](s00_http_basics/) | "后端到底是什么？浏览器输入网址后发生了什么？" | ✅ |

### 🔰 第 1 章：写出第一个接口

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s01 | [第一个接口](s01_hello_fastapi/) | "怎么让后端跑起来，浏览器能访问到？" | FastAPI()、@app.get()、uvicorn |
| s02 | [返回数据](s02_pydantic_models/) | "怎么返回不同类型的数据？怎么知道接口对不对？" | JSON、状态码、/docs 文档 |
| s03 | [接收参数](s03_path_query_params/) | "怎么接收前端传来的参数？" | 路径参数 {id}、查询参数 ?key=value |

### 📦 第 2 章：接收和校验数据

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s04 | [请求体](s04_request_body/) | "前端发来一大段 JSON 怎么收？" | POST、@app.post()、Pydantic BaseModel |
| s05 | [数据校验](s05_sqlalchemy/) | "怎么保证数据是合法的？必填项没传怎么办？" | Field()、自动 422、枚举限制 |
| s06 | [数据库入门](s06_crud_repository/) | "数据怎么存到硬盘上，重启不丢失？" | SQLite、SQLAlchemy、建表、CRUD |

### 🏗️ 第 3 章：架构与工程化（接口封装核心）

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s07 | [CRUD 完整实现](s07_dependency_injection/) | "增删改查的标准套路是什么？" | Repository 模式、Session 管理 |
| s08 | [依赖注入](s08_router_structure/) | "认证/数据库会话/配置怎么在接口间共享？" | Depends()、yield 依赖、依赖链 |
| s09 | [路由拆分](s09_unified_response/) | "50 个接口写一个文件不乱吗？" | APIRouter、模块化项目结构 |
| s10 | [统一响应](s10_exception_middleware/) | "怎么让所有接口返回同一个格式？" | code/message/data、工厂模式 |
| s11 | [异常与中间件](s11_jwt_auth/) | "出错了怎么给前端有用的信息？跨域怎么配？" | exception_handler、CORS、日志 |

### 🔐 第 4 章：认证与安全

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s12 | [JWT 认证](s12_rbac_permission/) | "怎么区分登录用户和游客？" | JWT、OAuth2PasswordBearer、bcrypt |
| s13 | [权限控制](s13_background_tasks/) | "管理员和普通用户能做的事情怎么区分？" | RBAC、角色、权限点 |

### 🚀 第 5 章：进阶主题

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s14 | [后台任务](s14_websocket/) | "发邮件要 5 秒，用户要等吗？" | BackgroundTasks、UploadFile |
| s15 | [WebSocket](s15_testing/) | "怎么让服务器主动推送消息给前端？" | WebSocket 协议、连接管理、广播 |
| s16 | [测试](s16_deployment/) | "改了代码怎么确保没弄坏别的地方？" | TestClient、pytest、fixture |
| s17 | [部署](s00_http_basics/) | "写完了怎么让别人也能用？" | Docker、gunicorn、环境变量 |

---

## 如何使用本课程

### 学习节奏

每个模块按这个顺序：

1. **读 README 的「为什么」部分** — 理解这个模块要解决什么问题
2. **读 README 的「怎么做」部分** — 理解核心原理，不要跳
3. **运行 code.py** — 每个文件都是独立可运行的
4. **打开 /docs** — 在 Swagger UI 里亲自动手试接口
5. **做「自己动手」练习** — 每个模块末尾有练习，一定要做
6. **再读一遍 README** — 此时有些概念你会理解得更深

### 不要跳章

每个模块的代码都依赖前一个模块的概念。跳着学 = 浪费时间。

### 遇到不懂的先记下来

有些概念（比如"异步"、"ORM"）第一次听到不懂很正常。先记下来，继续往后学，回头再看往往豁然开朗。

---

## 快速开始

```bash
# 1. 安装依赖
pip install -r s22_fastapi/requirements.txt

# 2. 从概念章开始（纯阅读，不写代码）
# 打开 s22_fastapi/s00_http_basics/README.md

# 3. 第一个接口
cd s22_fastapi/s01_hello_fastapi
python code.py
# 浏览器打开 http://localhost:8000
```

---

## 和 learn-claude-code 项目的关系

本课程是 learn-claude-code 仓库中的 s22，和主项目遵循同样的学习理念：

| learn-claude-code | s22_fastapi |
|-------------------|-------------|
| Agent Loop = 一切的基础 | 路由 + Schema = 一切的基础 |
| 渐进式添加工具 | 渐进式添加功能 |
| 每章一个可运行的 Agent | 每章一个可运行的 API |
| Harness 层的概念 | 接口层的概念 |
| 从简单到复杂，不跳步 | 从简单到复杂，不跳步 |
