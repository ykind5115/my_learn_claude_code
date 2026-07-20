#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s27-08: 代理/VPN/NAT — 中间人转发

运行: python s27_network/s08_proxy_vpn/code.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_key_point, print_note, print_section


def demo_1_nat():
    print_step(1, "NAT — 内网上外网")
    print(f"  你的内网设备:")
    print(f"    192.168.1.100 (你的电脑)")
    print(f"    192.168.1.101 (手机)")
    print(f"    192.168.1.1   (路由器/网关)")
    print(f"  NAT 过程:")
    print(f"    你发请求: 192.168.1.100:54321 → api.anthropic.com:443")
    print(f"    路由器改写: 公网IP:12345 → api.anthropic.com:443")
    print(f"    服务器看到的是路由器的公网 IP，不知道你的内网地址")
    print_key_point("几十台设备共享一个公网 IP → NAT 的关键作用")


def demo_2_http_proxy():
    print_step(2, "HTTP 代理")
    print(f"  Agent 配代理:")
    print(f"    export HTTP_PROXY=http://proxy.company.com:8080")
    print(f"    export HTTPS_PROXY=http://proxy.company.com:8080")
    print(f"  Python 代码里:")
    print(f"    os.environ['HTTP_PROXY'] = 'http://proxy:8080'")
    print_key_point("公司网络通常需要配代理才能访问外网 API")


def demo_3_vpn():
    print_step(3, "VPN — 加密隧道")
    print(f"  你的电脑 ══加密隧道══ VPN 服务器 ══ 目标网站")
    print(f"  → 你的所有流量通过加密隧道到 VPN 服务器")
    print(f"  → 目标网站看到的是 VPN 服务器的 IP，不是你的真实 IP")
    print(f"  → 同时加密了所有通信（包括非 HTTPS 的流量）")


def demo_4_agent_config():
    print_step(4, "Agent 网络配置检查")
    proxy_vars = ["HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "http_proxy", "https_proxy"]
    for var in proxy_vars:
        val = os.environ.get(var, "")
        if val:
            print(f"  {var} = {val[:60]}...")
        else:
            print(f"  {var} = (未设置)")
    if not any(os.environ.get(v) for v in proxy_vars):
        print_note("当前无代理配置 → 直接连接")


if __name__ == "__main__":
    print_section("s27-08: 代理/VPN/NAT")
    demo_1_nat()
    demo_2_http_proxy()
    demo_3_vpn()
    demo_4_agent_config()
    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("NAT=内网→公网 代理=代发HTTP VPN=加密隧道")
