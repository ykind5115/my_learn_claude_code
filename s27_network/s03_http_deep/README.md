# s27-03: HTTP 深入

[← 返回概览](../README.md) | [上一章：DNS](../s02_dns/) | [下一章：HTTPS/TLS](../s04_https_tls/)

> *"GET 和 POST 到底发了什么？状态码 200/400/500 怎么理解？请求头和请求体长什么样？"*

---

## 问题 — `client.messages.create(...)` 在网络上到底发了什么？

Anthropic SDK 帮你封装了 HTTP。但理解原始 HTTP 格式才能在 API 报错时看懂日志、在 s11 错误恢复时知道 429 和 500 的区别。

---

## 原理：HTTP 消息格式

```
请求:
POST /v1/messages HTTP/1.1          ← 请求行 (方法 + 路径 + 版本)
Host: api.anthropic.com              ← 请求头 (Key: Value)
Authorization: api-key sk-ant-xxx
Content-Type: application/json
Content-Length: 256
                                     ← 空行分割
{"model":"claude-sonnet-5",...}     ← 请求体 (JSON)

响应:
HTTP/1.1 200 OK                      ← 状态行 (版本 + 状态码 + 描述)
Content-Type: application/json
Content-Length: 1024
                                     ← 空行分割
{"id":"msg_xxx","content":[...]}     ← 响应体 (JSON)
```

---

## 核心概念

### HTTP 方法

| 方法 | 含义 | Agent 中 |
|------|------|---------|
| GET | 查询 | 查模型列表、查用量 |
| POST | 创建 | 发消息给模型 (核心) |
| PUT | 全量更新 | 更新配置 |
| DELETE | 删除 | 删会话 |

### 状态码分类

- **2xx** 成功 (200 OK, 201 Created)
- **3xx** 重定向 (301 永久搬家, 302 临时搬)
- **4xx** 客户端错误 (400 你发错了, 401 没带钥匙, 429 敲门太快)
- **5xx** 服务器错误 (500 服务器崩了, 503 过载)

### 常见请求头

- `Authorization`: 认证信息 (API Key)
- `Content-Type`: 请求体类型 (`application/json`)
- `Accept`: 我想要的响应格式
- `User-Agent`: 我是谁

---

## 试一下

```bash
python s27_network/s03_http_deep/code.py
```

---

## 小结

```
请求 = 方法 + 路径 + Header + Body
响应 = 状态码 + Header + Body
2xx=成功 4xx=你的错 5xx=服务器的错
```
