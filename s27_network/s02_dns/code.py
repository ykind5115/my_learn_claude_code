#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s27-02: DNS — 域名解析

运行: python s27_network/s02_dns/code.py
"""

import os, sys, socket
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, run_cmd, print_step, print_key_point, print_note, print_section


def demo_1_gethostbyname():
    print_step(1, "Python 解析域名")
    domains = ["api.anthropic.com", "google.com", "localhost"]
    for d in domains:
        try:
            ip = socket.gethostbyname(d)
            print(f"  {Color.BOLD}{d:25s}{Color.RESET} → {Color.SUCCESS}{ip}{Color.RESET}")
        except socket.gaierror as e:
            print(f"  {d:25s} → {Color.ERROR}解析失败: {e}{Color.RESET}")


def demo_2_getaddrinfo():
    print_step(2, "getaddrinfo — 完整解析")
    try:
        results = socket.getaddrinfo("httpbin.org", 443, proto=socket.IPPROTO_TCP)
        print(f"  httpbin.org:443 的解析结果:")
        seen = set()
        for family, kind, proto, canonname, addr in results:
            ip, port = addr
            if ip not in seen:
                seen.add(ip)
                family_name = "IPv4" if family == socket.AF_INET else "IPv6"
                print(f"    {family_name}: {Color.SUCCESS}{ip}{Color.RESET} (端口 {port})")
    except socket.gaierror as e:
        print_note(f"解析失败: {e} (可能无网络)")


def demo_3_nslookup():
    print_step(3, "nslookup — 命令行 DNS 查询")
    ret, out, err = run_cmd("nslookup httpbin.org", timeout=5)
    if ret == 0 and out:
        for line in out.strip().split("\n"):
            if line.strip():
                print(f"  {Color.DIM}{line.strip()}{Color.RESET}")
    else:
        print_note("nslookup 不可用，用 Python 代替:")
        try:
            ip = socket.gethostbyname("httpbin.org")
            print(f"  httpbin.org → {ip}")
        except Exception:
            pass


def demo_4_dns_cache():
    print_step(4, "DNS 缓存")
    print(f"  第一次查询: 走完整的递归链 (~100ms)")
    print(f"  第二次查询: 从缓存返回 (~1ms)")
    print_key_point("Agent 高频调用 API → DNS 缓存避免每次都查")

    # 验证：连续查询同一个域名
    import time
    domain = "httpbin.org"
    times = []
    for i in range(3):
        start = time.time()
        try:
            socket.gethostbyname(domain)
        except Exception:
            pass
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
    print(f"  连续 3 次查询 {domain}: {[f'{t:.1f}ms' for t in times]}")
    print_note("第一次明显慢(走网络)，后续快(缓存)")


if __name__ == "__main__":
    print_section("s27-02: DNS — 互联网的电话簿")
    demo_1_gethostbyname()
    demo_2_getaddrinfo()
    demo_3_nslookup()
    demo_4_dns_cache()
    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("DNS = 域名→IP 的电话簿")
    print_key_point("gethostbyname() 查 A 记录, getaddrinfo() 全面解析")
    print_key_point("DNS 有缓存 — 高频 API 调用不需要每次都查")
