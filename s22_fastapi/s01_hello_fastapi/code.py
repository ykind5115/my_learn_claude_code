#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s01: 第一个接口 — 让后端跑起来

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - FastAPI() 做了什么？
  - @app.get("/") 这行是什么意思？
  - uvicorn 是干嘛的？
  - 浏览器怎么访问到你的 Python 函数的？
═══════════════════════════════════════════════════════════════

启动方式:
    python s22_fastapi/s01_hello_fastapi/code.py

然后打开浏览器访问:
    http://localhost:8000          ← 你的第一个接口！
    http://localhost:8000/docs     ← 自动生成的 API 文档
"""

# ═══════════════════════════════════════════════════════════════
# 第 1 步: 导入 FastAPI
# ═══════════════════════════════════════════════════════════════
# FastAPI 是一个 Python 类。从 fastapi 包里导入它。
# 注意: 你需要在终端里先运行: pip install fastapi
from fastapi import FastAPI

# ═══════════════════════════════════════════════════════════════
# 第 2 步: 创建应用实例
# ═══════════════════════════════════════════════════════════════
# 这一行创建了你的整个 API 应用。
# 变量名 "app" 是约定俗成的名字 — uvicorn 启动时要用它。
#
# 类比: FastAPI() = 创建一个空白画布，后面往上贴路由。
#
# 参数 title, description, version 是可选的 —
# 它们会出现在 /docs 文档页面的顶部。
app = FastAPI(
    title="s01 - 我的第一个 API",
    description="从零开始：学习如何让后端跑起来",
    version="1.0.0",
)

# ═══════════════════════════════════════════════════════════════
# 第 3 步: 定义路由（接口）
# ═══════════════════════════════════════════════════════════════
#
# 核心语法:
#   @app.http方法("URL路径")
#   def 函数名():
#       return 字典
#
# @app.get("/") 的意思是:
#   "当有人用 GET 方法访问根路径 / 时，调用下面这个函数"
#
# 函数返回的 dict 会被 FastAPI 自动转为 JSON。


# ── 路由 1: 根路径 ─────────────────────────────────────────────
@app.get("/")
def root():
    """
    访问 http://localhost:8000/ 时调用这个函数。

    这是你的第一个接口！返回一个欢迎消息。
    """
    # FastAPI 会自动把这个 dict 变成 JSON: {"message": "欢迎..."}
    return {
        "message": "🎉 恭喜！你的第一个后端接口跑起来了！",
        "下一步": "试试访问 /hello 和 /docs",
    }


# ── 路由 2: /hello ─────────────────────────────────────────────
@app.get("/hello")
def say_hello():
    """
    访问 http://localhost:8000/hello

    这是最简单的接口: 不接收任何参数，只返回固定的数据。
    """
    # 你可以返回任何 dict，FastAPI 都会转成 JSON
    return {
        "message": "你好，世界！Hello, World!",
        "status": "ok",
    }


# ── 路由 3: /status — 模拟健康检查 ──────────────────────────────
@app.get("/status")
def server_status():
    """
    访问 http://localhost:8000/status

    真实项目中这种接口叫"健康检查"（health check）。
    监控系统定期访问它来判断服务是否活着。
    """
    return {
        "status": "运行中",
        "framework": "FastAPI",
        "version": "1.0.0",
    }


# ═══════════════════════════════════════════════════════════════
# 第 4 步: 路径参数 — URL 里的动态内容
# ═══════════════════════════════════════════════════════════════
#
# {变量名} 表示"这里可以是任意值，把它作为参数传给函数"。
# 函数参数名必须和 URL 里的变量名一致。
# 类型提示 (如 :int) 告诉 FastAPI 自动把字符串转成对应类型。

@app.get("/users/{user_id}")
def get_user(user_id: int):
    """
    路径参数示例 — 访问 /users/42 返回 {"user_id": 42}

    参数说明:
      {user_id} — URL 里的变量
      user_id: int — 函数参数，FastAPI 自动把 "42" 转成整数 42

    试试:
      /users/42     → 正常返回
      /users/hello  → 422 错误（hello 不是 int）
    """
    # user_id 已经是 int 类型了，不是字符串
    # FastAPI 在调用你的函数之前就做好了类型转换
    return {
        "user_id": user_id,
        "user_id的类型": str(type(user_id).__name__),  # 你会发现是 int
    }


@app.get("/greet/{name}")
def greet(name: str):
    """
    路径参数 — 字符串类型。

    访问 /greet/张三 返回 {"message": "你好, 张三!"}

    注意: name: str — 路径参数默认就是字符串，
    写 :str 和不写效果一样（但写了更清晰）。
    """
    return {"message": f"你好, {name}!"}


# ── 两个路径参数 ─────────────────────────────────────────────────
@app.get("/users/{user_id}/posts/{post_id}")
def get_user_post(user_id: int, post_id: int):
    """
    一个 URL 里可以有多个路径参数。

    访问 /users/1/posts/42：
      user_id = 1
      post_id = 42

    这种嵌套结构很常见: /资源A/{idA}/资源B/{idB}
    """
    return {
        "user_id": user_id,
        "post_id": post_id,
        "含义": f"用户 {user_id} 的第 {post_id} 篇文章",
    }


# ═══════════════════════════════════════════════════════════════
# 第 5 步: 启动服务器
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # 只有在直接运行这个文件时才执行下面的代码
    # 如果是被其他文件 import，下面的代码不执行

    import uvicorn

    # uvicorn 是 ASGI 服务器 — 它负责:
    #   1. 监听 8000 端口，等 HTTP 请求进来
    #   2. 解析 HTTP 请求（方法、路径、头、Body）
    #   3. 交给上面的 app（FastAPI 实例）处理
    #   4. 把 FastAPI 返回的响应发回浏览器

    print("=" * 55)
    print("🚀 服务器启动中...")
    print("")
    print("   在浏览器里打开:")
    print("   http://localhost:8000        ← 根路径")
    print("   http://localhost:8000/hello  ← 问好")
    print("   http://localhost:8000/docs   ← 自动文档（可以试接口！）")
    print("   http://localhost:8000/users/42  ← 路径参数")
    print("   http://localhost:8000/greet/张三 ← 中文路径参数")
    print("")
    print("   按 Ctrl+C 停止服务器")
    print("=" * 55)

    # host="0.0.0.0": 接受所有网络连接（局域网也能访问）
    # port=8000:      监听 8000 端口
    # 如果 8000 被占用，改成 8001 或 9000
    uvicorn.run(app, host="0.0.0.0", port=8000)
