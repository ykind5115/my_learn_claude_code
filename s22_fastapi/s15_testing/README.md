# s15: WebSocket — 实时双向通信

s01 → ... → s14 → `s15` → [s16](../s16_deployment/) → s17
> *"HTTP 是你问我答，WebSocket 是打电话 — 服务器可以主动推送消息了。"*
>
> **前提知识**: s14（理解异步 async/await 基础）。

---

## 1. HTTP 的局限

HTTP 是**请求-响应**模式：

```
客户端: "有新消息吗？"  →  服务器: "没有"
客户端: "有新消息吗？"  →  服务器: "没有"    ← 浪费
客户端: "有新消息吗？"  →  服务器: "有！"    ← 终于有了
```

这叫**轮询（Polling）** — 大部分请求都是浪费。而且服务器**不能主动**发消息给客户端。

---

## 2. WebSocket：持久双向连接

```
客户端 ───────── 建立连接 ───────── 服务器
   │                                  │
   │  ←──── 服务器主动推送消息 ──────  │
   │  ────── 客户端发消息 ──────────→  │
   │  ←──── 服务器主动推送消息 ──────  │
   │                                  │
   └──── 连接保持，直到某一方断开 ────┘
```

---

## 3. FastAPI 中的 WebSocket

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()     # 1. 接受连接（必须第一步做）

    try:
        while True:
            data = await websocket.receive_text()    # 2. 等消息
            await websocket.send_text(f"Echo: {data}")  # 3. 回复
    except WebSocketDisconnect:
        print(f"{client_id} 断开了连接")
```

---

## 4. 连接管理 — 广播消息

真实应用中需要一个管理器来跟踪所有连接：

```python
class ConnectionManager:
    def __init__(self):
        self.active: dict[WebSocket, str] = {}  # {连接: 用户名}

    async def connect(self, ws: WebSocket, name: str):
        await ws.accept()
        self.active[ws] = name

    def disconnect(self, ws: WebSocket):
        self.active.pop(ws, None)

    async def broadcast(self, message: str):
        """发给所有在线用户"""
        for ws in self.active:
            await ws.send_text(message)
```

---

## 5. 什么时候用 WebSocket vs 轮询 vs SSE？

| | 轮询 | WebSocket | SSE |
|---|---|---|---|
| 方向 | 客户端→服务器 | 双向 | 服务器→客户端 |
| 复杂度 | 简单 | 中等 | 简单 |
| 适用 | 不要求实时 | 聊天、游戏、协作 | 通知、股票行情 |

---

## 6. 自己动手

1. 运行 code.py，在浏览器打开聊天室页面
2. 打开两个窗口 → 在一个窗口发消息 → 另一个窗口立即收到
3. 观察 Network 面板（F12 → WS 标签），看 WebSocket 的消息帧
