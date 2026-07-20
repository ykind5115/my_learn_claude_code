#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s27-06: WebSocket/SSE — 实时推送

运行: python s27_network/s06_websocket_sse/code.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_key_point, print_note, print_section


def demo_1_polling_problem():
    print_step(1, "HTTP 轮询的痛点")
    print(f"  客户端: '有新消息吗?' → 服务器: '没有'")
    print(f"  客户端: '有新消息吗?' → 服务器: '没有'")
    print(f"  客户端: '有新消息吗?' → 服务器: '没有'")
    print(f"  ... 99% 的请求是浪费")
    print_key_point("HTTP = 一问一答，服务器不能主动推")


def demo_2_websocket():
    print_step(2, "WebSocket — 全双工热线")
    print(f"  升级握手:")
    print(f"    GET /chat HTTP/1.1")
    print(f"    Upgrade: websocket")
    print(f"    Connection: Upgrade")
    print(f"    101 Switching Protocols")
    print(f"  通信方式:")
    print(f"    → 服务器: '任务完成了!' (主动推送)")
    print(f"    → 客户端: '收到, 继续下一个' (主动发)")
    print(f"    → 双方随时可以发消息")
    print_key_point("s19 MCP 的 WebSocket 传输 = 这个原理")


def demo_3_sse():
    print_step(3, "SSE — 服务器单向推送")
    print(f"  客户端:")
    print(f"    GET /events HTTP/1.1")
    print(f"    Accept: text/event-stream")
    print(f"  服务器响应:")
    print(f"    Content-Type: text/event-stream")
    print(f"    ")
    print(f'    data: {{"event":"progress","pct":50}}')
    print(f"    ")
    print(f'    data: {{"event":"progress","pct":100}}')
    print(f"    ")
    print_key_point("SSE = 服务器→客户端 单向推送，HTTP 原生支持")


def demo_4_compare():
    print_step(4, "HTTP vs WebSocket vs SSE 对比")
    print(f"  HTTP:      一问一答，服务器不能主动发")
    print(f"  WebSocket: 全双工，双方随时发 (需要升级握手)")
    print(f"  SSE:       服务器→客户端单向推送 (HTTP 原生)")
    print()
    print_key_point("Agent 场景: API调用用HTTP, 实时通知用WebSocket, 进度推送用SSE")


if __name__ == "__main__":
    print_section("s27-06: WebSocket/SSE — 实时推送")
    demo_1_polling_problem()
    demo_2_websocket()
    demo_3_sse()
    demo_4_compare()
    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("HTTP=对讲机 WebSocket=热线 SSE=新闻推送")
