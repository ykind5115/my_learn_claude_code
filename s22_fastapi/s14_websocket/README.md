# s14: 后台任务 & 文件上传 — 慢操作后台跑，用户不用等

s01 → ... → s13 → `s14` → [s15](../s15_testing/) → ... → s17
> *"发邮件要 5 秒 — 你不能让用户盯着转圈。把慢操作扔到后台，立即返回'已收到'。"*
>
> **前提知识**: s13（理解 Depends 依赖链）。

---

## 1. 问题：有些操作很慢

- 发邮件：连接 SMTP 服务器、发出去 → 3-5 秒
- 生成报表：查数据库、计算、生成 PDF → 10-30 秒
- 处理视频：转码 → 几分钟

如果用户要等这些完成才能收到 HTTP 响应，体验极差。

---

## 2. 解决方案：BackgroundTasks

FastAPI 内置了轻量级的后台任务：

```python
from fastapi import BackgroundTasks

def send_email(email: str):
    """这个函数在后台运行"""
    time.sleep(3)  # 实际发邮件
    print(f"发送完成: {email}")

@app.post("/register")
def register(email: str, background_tasks: BackgroundTasks):
    # 用户立即收到响应
    background_tasks.add_task(send_email, email)
    #             ↑ 函数名    ↑ 传给函数的参数
    return {"message": "注册成功！邮件稍后发送"}
```

流程：
1. 接口函数 return → 用户立即收到 201 响应
2. 响应发送后 → `send_email` 在后台执行
3. 两者互不阻塞

---

## 3. BackgroundTasks vs Celery

| | BackgroundTasks | Celery + Redis |
|---|---|---|
| 运行在哪 | 同一个进程 | 独立的 worker 进程 |
| 服务器重启 | 任务丢失 | 任务持久化 |
| 适用场景 | 轻量、可丢失的任务 | 重要、不能丢的任务 |
| 配置 | 零配置 | 需要 Redis/RabbitMQ |

---

## 4. 文件上传

```python
from fastapi import UploadFile, File

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    # file 的几个属性:
    # file.filename   — 原始文件名
    # file.content_type — MIME 类型（如 image/png）
    # await file.read() — 读取文件内容（bytes）

    content = await file.read()
    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(content)

    return {"filename": file.filename, "size": len(content)}
```

> 需要安装：`pip install python-multipart`

---

## 5. 常见错误

### ❌ 在后台任务里用 session

```python
@app.post("/register")
def register(email, background_tasks, session=Depends(get_session)):
    background_tasks.add_task(send_email, email)
    # ❌ send_email 不能接收 session — 请求结束后 session 就关闭了
```

### ❌ 以为后台任务一定成功

后台任务失败时（比如邮件服务器挂了），用户已经收到了"注册成功"。要考虑失败处理。

---

## 6. 自己动手

1. 写一个注册接口，注册后后台"发送"欢迎邮件（用 `print` + `time.sleep` 模拟）
2. 写一个文件上传接口，保存到本地 `uploads/` 目录
3. 上传后后台"处理"文件（用 `time.sleep` 模拟）
