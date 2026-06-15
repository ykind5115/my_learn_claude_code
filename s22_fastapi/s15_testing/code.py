#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s15: WebSocket — 实时双向通信

═══════════════════════════════════════════════════════════════
学完本章你应该能回答:
  - HTTP 和 WebSocket 的根本区别是什么？
  - 怎么在 FastAPI 里写 WebSocket 端点？
  - ConnectionManager 怎么管理多个连接和广播？
═══════════════════════════════════════════════════════════════

启动:
    python s22_fastapi/s15_testing/code.py
    浏览器打开 http://localhost:8000/static/chat.html — 聊天室！
    打开多个窗口试试实时聊天。
"""

import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

# ═══════════════════════════════════════════════════════════════
# 连接管理器 — 追踪所有 WebSocket 连接
# ═══════════════════════════════════════════════════════════════

class ConnectionManager:
    """管理所有 WebSocket 连接 — 支持广播和个人消息"""

    def __init__(self):
        # {websocket对象: 用户名}
        self.active: dict[WebSocket, str] = {}

    async def connect(self, ws: WebSocket, username: str):
        """接受新连接并广播"加入"消息"""
        await ws.accept()
        self.active[ws] = username
        await self.broadcast({
            "type": "system",
            "message": f"{username} 加入了聊天室",
            "online": len(self.active),
        })

    def disconnect(self, ws: WebSocket):
        """移除连接"""
        username = self.active.pop(ws, "未知")
        return username

    async def broadcast(self, data: dict):
        """广播消息给所有在线用户"""
        text = json.dumps(data, ensure_ascii=False)
        for ws in list(self.active.keys()):
            try:
                await ws.send_text(text)
            except Exception:
                pass  # 发送失败就跳过

    async def send_personal(self, data: dict, ws: WebSocket):
        """发给指定用户"""
        await ws.send_text(json.dumps(data, ensure_ascii=False))


manager = ConnectionManager()


# ═══════════════════════════════════════════════════════════════
# FastAPI App
# ═══════════════════════════════════════════════════════════════

app = FastAPI(
    title="s15 - WebSocket",
    description="HTTP 是问答，WebSocket 是打电话",
    version="15.0.0",
)


# ═══════════════════════════════════════════════════════════════
# WebSocket 端点
# ═══════════════════════════════════════════════════════════════

@app.websocket("/ws/{username}")
async def chat_endpoint(websocket: WebSocket, username: str):
    """
    WebSocket 聊天端点。

    连接: ws://localhost:8000/ws/你的名字

    发送的消息格式（JSON）:
      {"type": "message", "text": "大家好！"}
      {"type": "ping"}

    收到的消息格式:
      {"type": "message", "username": "张三", "text": "...", "timestamp": "..."}
      {"type": "system", "message": "...", "online": 3}
      {"type": "pong"}
    """
    await manager.connect(websocket, username)

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = {"type": "message", "text": raw}

            if data.get("type") == "message":
                await manager.broadcast({
                    "type": "message",
                    "username": username,
                    "text": data.get("text", ""),
                    "timestamp": datetime.now().isoformat(),
                })
            elif data.get("type") == "ping":
                await manager.send_personal({"type": "pong"}, websocket)

    except WebSocketDisconnect:
        name = manager.disconnect(websocket)
        await manager.broadcast({
            "type": "system",
            "message": f"{name} 离开了聊天室",
            "online": len(manager.active),
        })


# ═══════════════════════════════════════════════════════════════
# 聊天室 HTML 页面
# ═══════════════════════════════════════════════════════════════

STATIC_DIR = Path("s15_static")
STATIC_DIR.mkdir(exist_ok=True)

CHAT_PAGE = """<!DOCTYPE html><html lang="zh">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>WebSocket 聊天室 — s15</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:#0f172a;color:#e2e8f0;display:flex;justify-content:center;align-items:center;height:100vh}
#app{width:100%;max-width:600px;background:#1e293b;border-radius:12px;display:flex;flex-direction:column;height:90vh;box-shadow:0 20px 60px rgba(0,0,0,.5)}
#h{padding:16px 20px;background:#334155;border-radius:12px 12px 0 0;display:flex;justify-content:space-between;align-items:center}
#h h2{font-size:16px}#online{font-size:12px;color:#94a3b8}
#msgs{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:8px}
.msg{padding:8px 14px;border-radius:10px;max-width:80%;word-break:break-word;line-height:1.4}
.msg.system{align-self:center;background:#334155;color:#94a3b8;font-size:12px;text-align:center}
.msg.mine{align-self:flex-end;background:#2563eb}
.msg.other{align-self:flex-start;background:#374151}
.msg .user{font-size:11px;color:#93c5fd;margin-bottom:2px}
.msg .time{font-size:10px;color:#94a3b8;margin-top:4px}
#inp{padding:12px;display:flex;gap:8px;border-top:1px solid #334155}
#inp input{flex:1;padding:10px 14px;border-radius:8px;border:1px solid #475569;background:#0f172a;color:#e2e8f0;font-size:14px;outline:none}
#inp button{padding:10px 20px;background:#2563eb;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:14px}
#setup{display:flex;flex-direction:column;align-items:center;justify-content:center;flex:1;gap:16px}
#setup input{padding:10px 14px;border-radius:8px;border:1px solid #475569;background:#0f172a;color:#e2e8f0;font-size:14px;outline:none;width:200px}
#setup button{padding:10px 30px;background:#2563eb;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:14px}
</style></head><body>
<div id="app">
<div id="h"><h2>💬 WebSocket 聊天室</h2><span id="online">在线: 0</span></div>
<div id="setup"><input id="ni" placeholder="输入昵称" maxlength="20" autofocus><button onclick="c()">加入</button></div>
<div id="msgs" style="display:none"></div>
<div id="inp" style="display:none"><input id="mi" placeholder="输入消息..." maxlength="500"><button onclick="s()">发送</button></div>
</div>
<script>
let w,n;
function c(){n=document.getElementById('ni').value.trim();if(!n)return;w=new WebSocket(`ws://${location.host}/ws/${encodeURIComponent(n)}`);
w.onopen=()=>{document.getElementById('setup').style.display='none';document.getElementById('msgs').style.display='flex';document.getElementById('inp').style.display='flex';document.getElementById('mi').focus()};
w.onmessage=(e)=>{const d=JSON.parse(e.data),m=document.getElementById('msgs'),el=document.createElement('div');
if(d.type==='system'){el.className='msg system';el.textContent=d.message;document.getElementById('online').textContent='在线: '+d.online}
else{el.className=d.username===n?'msg mine':'msg other';el.innerHTML=`<div class="user">${d.username}</div>${d.text}<div class="time">${new Date(d.timestamp).toLocaleTimeString()}</div>`}
m.appendChild(el);m.scrollTop=m.scrollHeight};
w.onclose=()=>location.reload()}
function s(){const i=document.getElementById('mi'),t=i.value.trim();if(!t||!w)return;w.send(JSON.stringify({type:'message',text:t}));i.value=''}
document.getElementById('mi').addEventListener('keydown',(e)=>{if(e.key==='Enter')s()})
document.getElementById('ni').addEventListener('keydown',(e)=>{if(e.key==='Enter')c()})
</script></body></html>"""

(STATIC_DIR / "chat.html").write_text(CHAT_PAGE, encoding="utf-8")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def root():
    return {
        "message": "s15 — WebSocket",
        "聊天室": "http://localhost:8000/static/chat.html",
        "API": "/docs",
    }


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    print("=" * 55)
    print("s15 — WebSocket 实时通信")
    print("   聊天室: http://localhost:8000/static/chat.html")
    print("   打开多个窗口试试实时聊天！")
    print("=" * 55)
    uvicorn.run(app, host="0.0.0.0", port=8000)
