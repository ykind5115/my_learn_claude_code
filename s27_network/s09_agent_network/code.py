#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s27-09: Agent 网络实践 — DNS→TCP→TLS→HTTP 全链路

运行: python s27_network/s09_agent_network/code.py
"""

import os, sys, socket, ssl, time, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_key_point, print_note, print_section


def demo_full_trace():
    host = "httpbin.org"
    port = 443
    path = "/post"

    # Step 1: DNS
    print_step(1, f"DNS 解析: {host}")
    start = time.time()
    ip = socket.gethostbyname(host)
    dns_time = (time.time() - start) * 1000
    print(f"  {host} → {Color.SUCCESS}{ip}{Color.RESET} ({dns_time:.1f}ms)")

    # Step 2: TCP
    print_step(2, "TCP 连接")
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((ip, port))
    tcp_time = (time.time() - start) * 1000
    print(f"  TCP 三次握手完成 → {tcp_time:.1f}ms")

    # Step 3: TLS
    print_step(3, "TLS 握手")
    start = time.time()
    ctx = ssl.create_default_context()
    ssock = ctx.wrap_socket(sock, server_hostname=host)
    tls_time = (time.time() - start) * 1000
    print(f"  TLS {ssock.version()} — 证书: {dict(ssock.getpeercert().get('subject', []))}")
    print(f"  TLS 握手完成 → {tls_time:.1f}ms")

    # Step 4: HTTP
    print_step(4, "HTTP POST 请求")
    body = json.dumps({"message": "hello from s27 demo", "agent": "claude-code"})
    request = (
        f"POST {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
        f"{body}"
    )
    start = time.time()
    ssock.sendall(request.encode())
    http_time = (time.time() - start) * 1000
    print(f"  发送 {len(request)} 字节 → {http_time:.1f}ms")

    # Step 5: 接收响应
    print_step(5, "接收 HTTP 响应")
    start = time.time()
    response = b""
    while True:
        try:
            chunk = ssock.recv(4096)
            if not chunk:
                break
            response += chunk
        except socket.timeout:
            break
    resp_time = (time.time() - start) * 1000
    ssock.close()

    text = response.decode(errors="replace")
    header_end = text.find("\r\n\r\n")
    status_line = text.split("\r\n")[0] if text else "N/A"
    body_text = text[header_end+4:] if header_end > 0 else ""

    print(f"  状态行: {Color.SUCCESS}{status_line}{Color.RESET}")
    print(f"  响应大小: {len(response)} bytes → {resp_time:.1f}ms")

    # 总结
    total = dns_time + tcp_time + tls_time + http_time + resp_time
    print(f"\n  {Color.HIGHLIGHT}全链路耗时:{Color.RESET}")
    print(f"    DNS:  {dns_time:.1f}ms")
    print(f"    TCP:  {tcp_time:.1f}ms")
    print(f"    TLS:  {tls_time:.1f}ms")
    print(f"    HTTP请求: {http_time:.1f}ms")
    print(f"    HTTP响应: {resp_time:.1f}ms")
    print(f"    {Color.BOLD}总计: {total:.0f}ms{Color.RESET}")


if __name__ == "__main__":
    print_section("s27-09: Agent 网络实践 — 全链路跟踪")
    try:
        demo_full_trace()
    except Exception as e:
        print_note(f"全链路演示失败: {e}")
        print_note("(无网络时展示概念流程，不影响理解)")
        # 展示概念流程
        print_step(1, "DNS → IP")
        print_step(2, "TCP → 三次握手")
        print_step(3, "TLS → 证书验证 + 密钥交换")
        print_step(4, "HTTP → POST JSON 请求")
        print_step(5, "等待 → 收到 200 OK + 模型响应")

    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("Agent API调用 = DNS→TCP→TLS→HTTP→等待→响应")
    print_key_point("每一步都可以独立诊断: ping(DNS+TCP) curl(HTTP) openssl(TLS)")
