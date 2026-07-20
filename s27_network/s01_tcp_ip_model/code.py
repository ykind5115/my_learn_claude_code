#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s27-01: TCP/IP 四层模型

运行: python s27_network/s01_tcp_ip_model/code.py
"""

import os, sys, socket
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_key_point, print_note, print_section


def demo_1_layers():
    print_step(1, "四层模型速览")
    layers = [
        ("应用层", "HTTP, DNS, WebSocket, SSH", "信封里的内容格式"),
        ("传输层", "TCP, UDP", "挂号信(TCP)还是平信(UDP)"),
        ("网络层", "IP, ICMP", "收件地址和路线"),
        ("链路层", "Ethernet, WiFi", "网线/无线信号怎么传"),
    ]
    for name, protos, desc in layers:
        print(f"  {Color.BOLD}{name:8s}{Color.RESET} {Color.DIM}[{protos}]{Color.RESET}")
        print(f"            {desc}")


def demo_2_encapsulation():
    print_step(2, "封装：数据包的套娃过程")
    print(f"  你的 HTTP 数据: POST /v1/messages {{...}}")
    print(f"    ↓ 应用层: [HTTP Header]")
    print(f"    ↓ 传输层: [TCP Header: port 443]  ← TCP 包裹")
    print(f"    ↓ 网络层: [IP Header: 1.1.1.1→2.2.2.2] ← IP 包裹")
    print(f"    ↓ 链路层: [MAC Header + CRC]  ← 网卡发出")
    print_key_point("每一层只关心自己的事：TCP 不管路由，IP 不管丢包重传")


def demo_3_tcp_vs_udp():
    print_step(3, "TCP vs UDP — 挂号信 vs 平信")
    print(f"  {Color.BOLD}TCP (挂号信){Color.RESET}")
    print(f"    三次握手 → 传输数据 → 确认收到 → 四次挥手")
    print(f"    保证: 不丢、不重、不乱序")
    print(f"  {Color.BOLD}UDP (平信){Color.RESET}")
    print(f"    直接发，不确认，丢了不管")
    print(f"    适用: 视频直播、DNS 查询、游戏(快比可靠更重要)")
    print_note("Agent API 调用全部走 TCP — 模型回答一个字都不能丢")


def demo_4_common_ports():
    print_step(4, "端口 — 公司里的具体部门")
    ports = [(80, "HTTP"), (443, "HTTPS"), (22, "SSH"), (53, "DNS"), (5432, "PostgreSQL"), (6379, "Redis")]
    for port, svc in ports:
        print(f"  {Color.BOLD}{port:5d}{Color.RESET} → {svc}")


if __name__ == "__main__":
    print_section("s27-01: TCP/IP 四层模型")
    demo_1_layers()
    demo_2_encapsulation()
    demo_3_tcp_vs_udp()
    demo_4_common_ports()
    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("四层: 应用层→传输层→网络层→链路层")
    print_key_point("TCP=挂号信(可靠) UDP=平信(快)")
