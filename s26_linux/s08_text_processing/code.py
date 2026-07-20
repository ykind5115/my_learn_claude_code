#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s26-08: 文本处理 — grep, sed, awk 三剑客

学习目标:
  - 用 grep 搜索文本
  - 用 sed 替换和删除
  - 用 awk 处理列
  - 三剑客组合使用

运行: python s26_linux/s08_text_processing/code.py
"""

import os
import sys
import subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, print_step, print_note,
                   print_key_point, print_section, create_demo_dir, cleanup_demo_dir)


# ═══════════════════════════════════════════════════════════
# 模拟日志数据
SAMPLE_LOG = """2024-01-15 10:00:01 INFO  Server started on port 8080
2024-01-15 10:00:05 DEBUG Loading configuration from /etc/app.yaml
2024-01-15 10:00:10 INFO  User alice logged in from 192.168.1.100
2024-01-15 10:00:12 ERROR Database connection timeout (retry 1/3)
2024-01-15 10:00:15 WARN  Retry attempt 2/3 for database
2024-01-15 10:00:20 ERROR Database connection timeout (retry 2/3)
2024-01-15 10:00:25 INFO  User bob logged in from 10.0.0.55
2024-01-15 10:00:30 ERROR Database connection timeout (retry 3/3) - GIVING UP
2024-01-15 10:00:35 INFO  User alice logged out
2024-01-15 10:00:40 INFO  Server shutting down
"""


# ═══════════════════════════════════════════════════════════
def demo_1_grep():
    print_step(1, "grep — 搜索文本")
    demo = create_demo_dir()
    log = demo / "app.log"
    log.write_text(SAMPLE_LOG)

    # 基本搜索
    r = subprocess.run(["grep", "ERROR", str(log)], capture_output=True, text=True)
    print(f"  grep ERROR → {len(r.stdout.strip().split(chr(10)))} 行")
    for line in r.stdout.strip().split("\n")[:3]:
        print(f"    {Color.RED}{line}{Color.RESET}")

    # 忽略大小写
    r = subprocess.run(["grep", "-i", "error", str(log)], capture_output=True, text=True)
    print(f"  grep -i error → {len(r.stdout.strip().split(chr(10)))} 行 (含 ERROR)")

    # 排除
    r = subprocess.run(["grep", "-v", "DEBUG|INFO", str(log)], capture_output=True, text=True)
    lines = [l for l in r.stdout.strip().split("\n") if l]
    print(f"  grep -v 'DEBUG|INFO' → {len(lines)} 行 (排除普通日志)")

    # 计数
    r = subprocess.run(["grep", "-c", "ERROR", str(log)], capture_output=True, text=True)
    print(f"  grep -c ERROR → {r.stdout.strip()} 条 ERROR")
    print_note("grep = Agent 排查日志的第一工具")

    cleanup_demo_dir(demo)


def demo_2_sed():
    print_step(2, "sed — 流编辑器")
    demo = create_demo_dir()
    data = demo / "data.txt"
    data.write_text("hello world\nhello linux\nhello python\n")

    # 替换
    r = subprocess.run(
        ["sed", "s/hello/hi/g", str(data)],
        capture_output=True, text=True,
    )
    print(f"  sed 's/hello/hi/g':")
    for line in r.stdout.strip().split("\n"):
        print(f"    {line}")

    # 删除行
    r = subprocess.run(
        ["sed", "/linux/d", str(data)],
        capture_output=True, text=True,
    )
    print(f"  sed '/linux/d' (删除含 linux 的行):")
    for line in r.stdout.strip().split("\n"):
        print(f"    {line}")

    cleanup_demo_dir(demo)


def demo_3_awk():
    print_step(3, "awk — 列处理器")
    demo = create_demo_dir()
    log = demo / "app.log"
    log.write_text(SAMPLE_LOG)

    # 提取第一列 (日期)
    r = subprocess.run(
        ["awk", "{print $1, $2, $3, $4, $5}", str(log)],
        capture_output=True, text=True,
    )
    print(f"  awk '{{print $1,$2,$3}}' (提取列):")
    for line in r.stdout.strip().split("\n")[:3]:
        print(f"    {line}")
    print(f"    ...")

    # 条件过滤：第三列 == "ERROR"
    r = subprocess.run(
        ['awk', '$3 == "ERROR" {print $1, $2, $4, $5, $6, $7, $8, $9}', str(log)],
        capture_output=True, text=True,
    )
    print(f"\n  awk '$3 == \"ERROR\"' (条件过滤):")
    for line in r.stdout.strip().split("\n"):
        print(f"    {Color.RED}{line}{Color.RESET}")

    cleanup_demo_dir(demo)


def demo_4_pipeline():
    print_step(4, "三剑客组合 — 管道串联")
    demo = create_demo_dir()
    log = demo / "app.log"
    log.write_text(SAMPLE_LOG)

    # 组合: 找 ERROR → 提取时间 → 排序去重
    print(f"  任务: 统计每个时间段各有多少条 ERROR")
    print(f"  命令: grep ERROR | awk '{{print $1,$2}}' | sort | uniq -c")

    r1 = subprocess.run(["grep", "ERROR", str(log)], capture_output=True, text=True)
    r2 = subprocess.run(
        ["awk", "{print $1, $2}"],
        input=r1.stdout, capture_output=True, text=True,
    )
    r3 = subprocess.run(
        ["sort"],
        input=r2.stdout, capture_output=True, text=True,
    )
    r4 = subprocess.run(
        ["uniq", "-c"],
        input=r3.stdout, capture_output=True, text=True,
    )
    print(f"  结果:")
    for line in r4.stdout.strip().split("\n"):
        print(f"    {line}")
    print_note("grep → awk → sort → uniq 管道链 = Linux 最强大的组合")

    cleanup_demo_dir(demo)


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print_section("s26-08: 文本处理 — 三剑客")

    demo_1_grep()
    demo_2_sed()
    demo_3_awk()
    demo_4_pipeline()

    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("小结:")
    print_key_point("  grep: 搜索/筛选行  (-i 忽略大小写, -v 排除, -c 计数)")
    print_key_point("  sed: 流编辑 (s/old/new/g 替换, /pattern/d 删除)")
    print_key_point("  awk: 列处理 ({print $1} 提取, $3>100 条件)")
    print_key_point("  | 管道串联: grep → awk → sort → uniq")
