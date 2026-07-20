#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s00-08: HTTP 和网络基础 — HTTP 请求/响应, TCP, 端口, DNS

学习目标:
  - 发起 HTTP 请求并检查响应
  - 理解状态码
  - 理解 TCP/端口/DNS

运行: python 08_http_network/code.py
"""

import json
import socket
import sys


# ═══════════════════════════════════════════════════════════
# Demo 1: HTTP 请求 (用 urllib)
# ═══════════════════════════════════════════════════════════
def demo_1_http_request():
    print("── Demo 1: HTTP 请求 ──")

    try:
        from urllib.request import Request, urlopen
        from urllib.error import HTTPError, URLError

        # 一个公开的测试 API
        url = "https://httpbin.org/json"

        print(f"  发送 GET 请求: {url}")
        req = Request(url, headers={"Accept": "application/json"})
        resp = urlopen(req, timeout=5)

        print(f"  状态码: {resp.status} ({'成功' if resp.status == 200 else '失败'})")
        print(f"  Content-Type: {resp.headers.get('Content-Type')}")
        data = json.loads(resp.read())
        print(f"  响应 JSON (截断): {json.dumps(data, ensure_ascii=False)[:200]}...")

    except (HTTPError, URLError) as e:
        print(f"  网络请求失败: {e}")
        print(f"  (断网环境，展示模拟数据)")
        print(f"  模拟: GET /v1/messages → 200 OK")
        print(f"  响应: {{\"id\": \"msg_xxx\", \"content\": [...]}}")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 2: 状态码模拟
# ═══════════════════════════════════════════════════════════
def demo_2_status_codes():
    print("── Demo 2: HTTP 状态码 ──")

    codes = [
        (200, "OK — 成功，拿到数据 ✓"),
        (400, "Bad Request — 你发给服务器的数据格式不对"),
        (401, "Unauthorized — 没带 API Key 或 Key 无效"),
        (429, "Too Many Requests — 请求太快，等一会"),
        (500, "Internal Server Error — 服务器出 bug 了"),
    ]

    for code, meaning in codes:
        emoji = "✓" if code == 200 else "⚠" if code == 429 else "✗"
        print(f"  {emoji} {code}: {meaning}")

    print()
    print("  在 Agent 里:")
    print("    200 → 继续循环")
    print("    401 → 检查 .env 里的 API Key")
    print("    429 → sleep 后重试 (s11 错误恢复)")
    print("    500 → 换备用模型或重试")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 3: Socket — TCP 连接的基础
# ═══════════════════════════════════════════════════════════
def demo_3_tcp_socket():
    print("── Demo 3: TCP Socket 基础 ──")

    # 解析 DNS
    host = "httpbin.org"
    try:
        ip = socket.gethostbyname(host)
        print(f"  DNS 解析: {host} → {ip}")
        print(f"    → DNS 把域名翻译成 IP 地址")
    except socket.gaierror:
        print(f"  DNS 解析失败: {host} (可能无网络)")
        print(f"    模拟: api.anthropic.com → 1.2.3.4")

    # 查看端口
    print()
    common_ports = [
        (80, "HTTP"),
        (443, "HTTPS"),
        (22, "SSH"),
        (5432, "PostgreSQL"),
        (6379, "Redis"),
    ]
    print("  常见端口:")
    for port, service in common_ports:
        print(f"    {port:5d} → {service}")

    print()
    print("  Python 连接 google.com:80 的例子:")
    print("    sock = socket.socket()")
    print("    sock.connect(('google.com', 80))  # DNS + TCP 连接")
    print("    sock.send(b'GET / HTTP/1.0\\r\\n\\r\\n')")
    print("    data = sock.recv(1024)")
    print("    → 这就是 HTTP 的底层实现")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 4: 模拟 Anthropic API 调用流程
# ═══════════════════════════════════════════════════════════
def demo_4_anthropic_api_flow():
    print("── Demo 4: 模拟一次 Anthropic API 调用 ──")

    print("  你写的代码:")
    print("    response = client.messages.create(")
    print("        model='claude-sonnet-5',")
    print("        messages=[{'role': 'user', 'content': 'Hello'}],")
    print("        max_tokens=1024,")
    print("    )")
    print()
    print("  底层发生的事情:")
    print("    1. SDK 把 messages 序列化成 JSON")
    print("       → {\"model\":\"claude-sonnet-5\",\"messages\":[...],\"max_tokens\":1024}")
    print("    2. 添加 HTTP 请求头")
    print("       → POST /v1/messages HTTP/1.1")
    print("       → Host: api.anthropic.com")
    print("       → Authorization: api-key sk-ant-xxx")
    print("       → Content-Type: application/json")
    print("    3. DNS 解析 api.anthropic.com → IP 地址")
    print("    4. TCP 连接到 IP:443 (HTTPS)")
    print("    5. TLS 握手 (加密)")
    print("    6. 发送请求体")
    print("    7. 等待响应...")
    print("    8. 收到 JSON 响应")
    print("       → {\"id\":\"msg_xxx\",\"content\":[{\"type\":\"text\",\"text\":\"Hi!\"}]}")
    print("    9. SDK 解析 JSON，返回 Python 对象")
    print()
    print("  → 你的代码只需要 1 行，但底层做了 9 步")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 5: 简单的 TCP Echo 客户端
# ═══════════════════════════════════════════════════════════
def demo_5_tcp_echo():
    print("── Demo 5: TCP Echo 演示 ──")

    try:
        # 连接到 httpbin 的 80 端口
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect(("httpbin.org", 80))

        # 发送一个简单的 HTTP 请求
        request = (
            "GET /get?hello=world HTTP/1.1\r\n"
            "Host: httpbin.org\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        sock.send(request.encode())

        # 读取响应
        response = b""
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            except socket.timeout:
                break
        sock.close()

        # 只显示第一行 + 空行后的 JSON
        text = response.decode()
        header_end = text.find("\r\n\r\n")
        if header_end > 0:
            first_line = text.split("\r\n")[0]
            body = text[header_end + 4:]
            print(f"  状态行: {first_line}")
            print(f"  响应体 (截断): {body[:200]}...")
            print(f"  → 这就是原始 HTTP 响应的样子")
    except Exception as e:
        print(f"  TCP 连接失败: {e}")
        print(f"  (不影响理解——核心概念不变)")
    print()


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("s00-08: HTTP 和网络基础")
    print("=" * 60)
    print()

    demo_1_http_request()
    demo_2_status_codes()
    demo_3_tcp_socket()
    demo_4_anthropic_api_flow()
    demo_5_tcp_echo()

    print("─" * 60)
    print("小结:")
    print("  HTTP: 就是你问我答，状态码告诉你结果")
    print("  DNS: 域名 → IP 地址 (电话簿)")
    print("  TCP: 可靠传输 (电话)")
    print("  端口: 一台机器的不同服务频道")
    print("  client.messages.create() = POST JSON → HTTPS → 拿到响应")
