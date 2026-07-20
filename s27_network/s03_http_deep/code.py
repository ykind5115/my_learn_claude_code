#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s27-03: HTTP 深入 — 请求/响应格式

运行: python s27_network/s03_http_deep/code.py
"""

import os, sys, json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_key_point, print_note, print_section


def demo_1_http_get():
    print_step(1, "HTTP GET — 查看原始响应")
    url = "https://httpbin.org/get?name=agent&version=1.0"
    try:
        req = Request(url, headers={"Accept": "application/json"})
        resp = urlopen(req, timeout=10)
        print(f"  状态行: {Color.SUCCESS}HTTP/1.1 {resp.status} {resp.reason}{Color.RESET}")
        print(f"  响应头:")
        for key, val in list(resp.headers.items())[:5]:
            print(f"    {key}: {val}")
        body = json.loads(resp.read())
        print(f"  响应体 (JSON):")
        for k, v in body.items():
            val_str = str(v)[:60]
            print(f"    {k}: {val_str}")
    except (HTTPError, URLError) as e:
        print_note(f"网络请求失败: {e}")


def demo_2_http_post():
    print_step(2, "HTTP POST — 模拟 Agent API 调用")
    print(f"  模拟 Anthropic API 调用:")
    print(f"    POST /v1/messages HTTP/1.1")
    print(f"    Host: api.anthropic.com")
    print(f"    Authorization: api-key sk-ant-xxx")
    print(f"    Content-Type: application/json")
    print(f"    ")
    print(f'    {{"model":"claude-sonnet-5","max_tokens":1024,"messages":[...]}}')
    print_key_point("这个 POST 就是 Agent 每一轮 loop 的实际网络操作")


def demo_3_status_codes():
    print_step(3, "状态码分类")
    codes = [
        ("2xx", "200 OK", Color.SUCCESS, "成功 — 你要的在这"),
        ("3xx", "301 Moved", Color.INFO, "搬家了 — 去新地址找"),
        ("4xx", "401 Unauthorized", Color.WARNING, "没带钥匙 — 检查 API Key"),
        ("4xx", "429 Rate Limited", Color.WARNING, "敲门太快 — 等一会再试(s11)"),
        ("5xx", "500 Internal", Color.ERROR, "服务器崩了 — 换策略或重试(s11)"),
    ]
    for cls, code, col, meaning in codes:
        print(f"  {col}{code:20s}{Color.RESET} {cls:4s} {meaning}")


def demo_4_headers():
    print_step(4, "关键 HTTP 请求头")
    headers = [
        ("Authorization", "Bearer sk-ant-xxx", "认证 — 证明你是谁"),
        ("Content-Type", "application/json", "告诉服务器: 我发的是 JSON"),
        ("Accept", "application/json", "告诉服务器: 我想要 JSON"),
        ("User-Agent", "Anthropic/Python 1.0", "我是谁、什么版本"),
    ]
    for name, val, desc in headers:
        print(f"  {Color.BOLD}{name:20s}{Color.RESET} {Color.DIM}{val:30s}{Color.RESET} {desc}")


if __name__ == "__main__":
    print_section("s27-03: HTTP 深入")
    demo_1_http_get()
    demo_2_http_post()
    demo_3_status_codes()
    demo_4_headers()
    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("HTTP请求 = 方法+路径+Header+Body")
    print_key_point("2xx=成功 4xx=你错了 5xx=服务器错了")
