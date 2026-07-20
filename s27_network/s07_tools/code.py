#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s27-07: 网络排障工具 — ping, curl, nslookup, traceroute

运行: python s27_network/s07_tools/code.py
"""

import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, run_cmd, print_step, print_key_point, print_note, print_section


def demo_1_ping():
    print_step(1, "ping — 连通性测试")
    target = "httpbin.org"
    if sys.platform == "win32":
        ret, out, _ = run_cmd(f"ping -n 2 {target}", timeout=8)
    else:
        ret, out, _ = run_cmd(f"ping -c 2 {target}", timeout=8)
    if ret == 0:
        for line in out.strip().split("\n"):
            if any(k in line.lower() for k in ["ttl", "time", "packet", "statistics", "avg", "minimum"]):
                print(f"  {Color.DIM}{line.strip()}{Color.RESET}")
    else:
        print_note("ping 不可用或目标不可达")


def demo_2_curl():
    print_step(2, "curl — HTTP 诊断")
    ret, out, _ = run_cmd("curl -s -o /dev/null -w 'http_code=%{http_code} time_total=%{time_total}s' https://httpbin.org/get", timeout=10)
    if ret == 0 and out:
        print(f"  httpbin.org: {Color.SUCCESS}{out.strip()}{Color.RESET}")
    else:
        # Python fallback
        from urllib.request import urlopen
        start = time.time()
        try:
            resp = urlopen("https://httpbin.org/get", timeout=5)
            elapsed = time.time() - start
            print(f"  httpbin.org: {Color.SUCCESS}http_code={resp.status} time_total={elapsed:.3f}s{Color.RESET}")
        except Exception as e:
            print_note(f"不可达: {e}")


def demo_3_nslookup():
    print_step(3, "nslookup — DNS 诊断")
    ret, out, _ = run_cmd("nslookup httpbin.org", timeout=5)
    if ret == 0 and out:
        for line in out.strip().split("\n"):
            if "Address" in line or "Name" in line:
                print(f"  {Color.DIM}{line.strip()}{Color.RESET}")
    else:
        print_note("nslookup 不可用")


def demo_4_diagnostic_flow():
    print_step(4, "Agent 排障流程")
    print(f"  1. {Color.BOLD}ping{Color.RESET} api.anthropic.com → 网络通不通？")
    print(f"     ↓ 通")
    print(f"  2. {Color.BOLD}nslookup{Color.RESET} api.anthropic.com → DNS 解析对吗？")
    print(f"     ↓ 正确")
    print(f"  3. {Color.BOLD}curl -v{Color.RESET} POST /v1/messages → HTTP 通不通？状态码？")
    print(f"     ↓ 200 OK")
    print(f"  4. 问题可能在代码层 → 检查 API Key, 请求格式")
    print_key_point("排障顺序: 网络→DNS→HTTP→代码")


if __name__ == "__main__":
    print_section("s27-07: 网络排障工具")
    demo_1_ping()
    demo_2_curl()
    demo_3_nslookup()
    demo_4_diagnostic_flow()
    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("ping=连通性 nslookup=DNS curl=HTTP traceroute=路由")
