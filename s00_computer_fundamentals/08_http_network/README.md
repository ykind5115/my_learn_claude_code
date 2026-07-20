# s00-08: HTTP 和网络基础

[← 返回概览](../README.md) | [上一章：Shell/JSON](../07_shell_json/) | [下一章：Git/DAG/Cron](../09_git_dag_cron/)

> *HTTP 是 Agent 跟外部世界通信的协议。每个 LLM API 调用都是一次 HTTP POST。TCP/端口/DNS 是 HTTP 的底层基础。*

---

## 问题 — `client.messages.create()` 到底发生了什么？

```python
response = client.messages.create(model=MODEL, messages=messages, tools=TOOLS)
```

这行代码背后是一次**HTTP POST 请求**。SDK 帮你藏了细节，但理解底层协议才能在出问题时排查：

1. 客户端把 `messages` 序列化成 JSON
2. 加上 `Authorization: api-key` 头部
3. POST 到 `https://api.anthropic.com/v1/messages`
4. 服务器返回 JSON 响应

---

## 核心概念

### 1. HTTP — 对讲机模型

```
客户端 (你)                      服务器 (API)
    │                                │
    │── POST /v1/messages ───→       │  请求: 方法 + 路径 + Header + Body
    │                                │
    │←── 200 OK + JSON ───────      │  响应: 状态码 + Header + Body
```

**一问一答**。客户端发起，服务器回应。服务器不能主动推送（除非用 WebSocket/SSE）。

### 2. 状态码 — 一看就懂

| 状态码 | 含义 | Agent 怎么做 |
|--------|------|-------------|
| 200 | 成功 | 处理响应 |
| 400 | 请求不对 | 检查参数 |
| 401 | 没带钥匙 | 检查 API Key |
| 429 | 敲门太快 | 等一会重试（s11） |
| 500 | 对面崩了 | 换策略或重试（s11） |

### 3. 网络底层

- **TCP**：可靠的连接型协议。"你先发，我确认收到"。像打电话
- **端口**：一台机器 65535 个端口，不同服务用不同端口。HTTP 默认 80，HTTPS 443
- **localhost**：`127.0.0.1`，指向自己的电脑
- **DNS**：把 `api.anthropic.com` 翻译成 IP 地址（像电话簿）

### 4. MCP 的三种传输方式

s19 MCP 插件支持三种通信方式：
- **stdio**：通过进程的 stdin/stdout 管道通信（最快，但只限本机）
- **HTTP/SSE**：通过 HTTP 请求/响应 + 服务器推送事件
- **WebSocket**：全双工通道，服务器可以随时推送

---

## 跟 Agent 的关系

| 章节 | 通信方式 |
|------|---------|
| **s01-s20** | 所有 API 调用都是 HTTP POST |
| **s15-s17** | Agent 团队通过 TCP/端口互相通信 |
| **s19** | MCP 的 stdio/HTTP/WebSocket 传输 |

---

## 试一下

```bash
python 08_http_network/code.py
```

---

## 小结

```
HTTP: 一问一答，状态码表示结果
  ├── POST /v1/messages  → 发消息给模型
  ├── 200 OK             → 成功
  ├── 401 Unauthorized   → 没带 API Key
  └── 429 Too Many       → 等一会重试

底层:
  TCP: 可靠连接（电话）
  DNS: 域名 → IP（电话簿）
  端口: 不同的服务频道
```
