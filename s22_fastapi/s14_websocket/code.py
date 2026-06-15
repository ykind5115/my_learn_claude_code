#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s14: 后台任务 & 文件上传

═══════════════════════════════════════════════════════════════
学完本章你应该能回答:
  - BackgroundTasks 怎么让用户不用等慢操作？
  - BackgroundTasks 和 Celery 的区别？
  - UploadFile 怎么接收文件上传？
═══════════════════════════════════════════════════════════════

启动:
    pip install python-multipart
    python s22_fastapi/s14_websocket/code.py
    然后访问 http://localhost:8000/docs
"""

import time
import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form

# 上传目录
UPLOAD_DIR = Path("s14_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="s14 - 后台任务 & 文件上传",
    description="慢操作后台跑，文件直接传",
    version="14.0.0",
)

# ═══════════════════════════════════════════════════════════════
# 后台任务函数
# ═══════════════════════════════════════════════════════════════

def send_welcome_email(email: str, username: str):
    """
    后台发送欢迎邮件（模拟）。

    这个函数会在响应已经返回给用户之后才执行。
    所以即使它需要 3 秒，用户也是立即收到"注册成功"的。
    """
    time.sleep(3)  # 模拟 SMTP 发送耗时
    print(f"✅ [后台] 欢迎邮件已发送至 {email}（用户: {username}）")


def process_image(filename: str, task_id: str):
    """后台处理图片（模拟）"""
    task_store[task_id]["status"] = "处理中"
    time.sleep(5)  # 模拟图片处理
    task_store[task_id]["status"] = "已完成"
    task_store[task_id]["result"] = {
        "thumbnail": f"/thumbnails/{filename}",
        "formats": ["原始", "缩略图", "WebP"],
    }
    print(f"✅ [后台] 图片 {filename} 处理完成")


# 任务状态存储（模拟）
task_store: dict[str, dict] = {}


# ═══════════════════════════════════════════════════════════════
# 接口
# ═══════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {
        "message": "s14 — 后台任务 & 文件上传",
        "试试": [
            "POST /register  → 立即响应，邮件后台发",
            "POST /upload    → 上传文件",
            "POST /upload-image → 上传图片，后台处理",
        ],
        "文档": "/docs",
    }


# ── 场景 1: 注册后后台发邮件 ──────────────────────────────────

@app.post("/register", status_code=201)
def register(
    username: str,
    email: str,
    background_tasks: BackgroundTasks,
):
    """
    注册 — 立即返回响应，邮件在后台发送。

    BackgroundTasks.add_task(函数, 参数1, 参数2...)
    参数会按顺序传给函数。
    """
    # 用户立即收到这个响应
    # 然后 send_welcome_email 在后台开始执行
    background_tasks.add_task(send_welcome_email, email, username)

    return {
        "message": f"注册成功！欢迎邮件将发送至 {email}",
        "note": "你立即收到了这个响应，但后台还在'发邮件'（观察控制台）",
    }


# ── 场景 2: 文件上传 ─────────────────────────────────────────

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    description: str = Form(""),
):
    """
    上传任意文件。

    UploadFile 提供了:
      file.filename    — 原始文件名
      file.content_type — MIME 类型
      await file.read() — 读取内容

    Form() 让 description 从表单字段（而非 JSON）获取。
    文件上传用 multipart/form-data 格式，不是 JSON。
    """
    # 安全: 防止路径穿越攻击（如 ../../etc/passwd）
    safe_name = file.filename.replace("\\", "/").split("/")[-1]
    save_path = UPLOAD_DIR / f"{datetime.now():%Y%m%d_%H%M%S}_{safe_name}"

    content = await file.read()
    save_path.write_bytes(content)

    return {
        "message": "上传成功",
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "saved": str(save_path),
    }


# ── 场景 3: 上传 + 后台处理 ───────────────────────────────────

_task_counter = 0


@app.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
):
    """
    上传图片 + 后台处理（生成缩略图等）。

    用户立即收到"上传成功"，
    然后后台开始处理图片。
    """
    global _task_counter

    # 安全检查
    if not file.content_type or not file.content_type.startswith("image/"):
        from fastapi import HTTPException
        raise HTTPException(400, detail="只允许上传图片")

    _task_counter += 1
    task_id = f"task_{_task_counter}"

    # 保存文件
    content = await file.read()
    safe_name = file.filename.replace("\\", "/").split("/")[-1]
    save_path = UPLOAD_DIR / safe_name
    save_path.write_bytes(content)

    # 记录任务状态
    task_store[task_id] = {
        "task_id": task_id,
        "file": safe_name,
        "status": "等待处理",
        "created_at": datetime.now().isoformat(),
    }

    # 后台处理
    background_tasks.add_task(process_image, safe_name, task_id)

    return {
        "message": "上传成功，后台处理中",
        "task_id": task_id,
        "check": f"GET /tasks/{task_id}",
    }


@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    """查询后台任务的进度"""
    if task_id not in task_store:
        from fastapi import HTTPException
        raise HTTPException(404, detail="任务不存在")
    return task_store[task_id]


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    print("=" * 55)
    print("s14 — 后台任务 & 文件上传")
    print("   访问 http://localhost:8000/docs")
    print("   POST /register → 立即响应，邮件后台发（3秒后看控制台）")
    print("   POST /upload   → 上传文件")
    print("=" * 55)
    uvicorn.run(app, host="0.0.0.0", port=8000)
