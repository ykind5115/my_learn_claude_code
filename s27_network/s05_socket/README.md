# s27-05: Socket 编程 — 亲手写 TCP 通信

[← 返回概览](../README.md) | [上一章：HTTPS/TLS](../s04_https_tls/) | [下一章：WebSocket/SSE](../s06_websocket_sse/)

> *"扔掉框架，用最原始的 socket 写一个能通信的程序。理解 bind/listen/accept/connect/send/recv。"*

---

## 问题 — 两个 Python 程序怎么通过网络互相通信？

你用 HTTP 库发请求，底层到底发生了什么？socket 是所有网络通信的起点——HTTP、WebSocket、SSH 都建立在 socket 之上。

---

## 原理：TCP 通信模型

```
  服务端                        客户端
    │                             │
    │  socket()                   │  socket()
    │  bind(port)                 │
    │  listen()                   │
    │     ↓                        │
    │  accept() ←────────────── connect()
    │     ↓                        │
    │  recv()  ←─────────────── send("hello")
    │  send()  ────────────────→ recv()
    │  close()                    │  close()
```

- **服务端**：绑定端口，等着别人连进来
- **客户端**：主动连接服务器的端口
- `accept()` 返回一个新的 socket，专门用于和这个客户端通信

---

## 核心概念

### send/recv 的边界问题

TCP 是**字节流**——你 `send("hello")` 两次，对方可能一次 `recv` 就收到 `"hellohello"`，也可能分三次收到。TCP 不保证消息边界。这就是为什么 HTTP 用 `Content-Length` 头来告诉对方"我这封信用多长"。

---

## 试一下

```bash
python s27_network/s05_socket/code.py
```

---

## 小结

```python
服务端: socket → bind → listen → accept → recv/send → close
客户端: socket → connect → send/recv → close
TCP 是字节流，不保证消息边界
```
