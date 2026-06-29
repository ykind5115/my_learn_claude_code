#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s08: 内存 vs 磁盘 — ★ 过渡章

运行: python s24_data_structures/s08_memory_vs_disk/code.py
"""

import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import (
    Color, print_header, print_step, print_note, print_key_point, print_warning,
    compare_performance,
)
from s08_memory_vs_disk.disk_sim import DiskSimulator, MemorySimulator


def demo_the_gap():
    print_step(1, "理解性能鸿沟 — 100,000x 的差距")

    disk = DiskSimulator(io_delay=0.005, name="Disk")  # 5ms for demo
    mem = MemorySimulator()

    n = 50  # 减少数量以免演示太长

    # 磁盘版
    start = time.perf_counter()
    for i in range(n):
        disk.write(f"key-{i}", i)
    for i in range(n):
        disk.read(f"key-{i}")
    disk_time = time.perf_counter() - start

    # 内存版
    start = time.perf_counter()
    for i in range(n):
        mem.write(f"key-{i}", i)
    for i in range(n):
        mem.read(f"key-{i}")
    mem_time = time.perf_counter() - start

    compare_performance("内存 (Memory)", mem_time, "磁盘 (Disk)", disk_time)
    print_warning(f"现实中的差距不是 {disk_time/mem_time:.0f}x，而是 ~100,000x！")
    print_note("(本演示缩小了延迟，否则你会等太久)")


def demo_why_btree():
    print_step(2, "为什么需要 B+ 树？— IO 次数决定性能")

    print_note("假设有 1,000,000 条记录:")
    print_note("")
    print_note("  二叉搜索树 (BST):")
    print_note("    深度 ≈ log₂(1,000,000) ≈ 20 层")
    print_note("    每次查找 = 20 次节点访问")
    print_note("    如果在磁盘上: 20 次 IO × 10ms = 200ms")
    print_note("")
    print_note("  B+ 树 (500 个 key/节点):")
    print_note("    深度 ≈ log₅₀₀(1,000,000) ≈ 3 层")
    print_note("    每次查找 = 3 次节点访问")
    print_note("    在磁盘上: 3 次 IO × 10ms = 30ms")
    print_note("")
    print_note("  差距: 200ms vs 30ms —— 快了 6.7x！")

    print_key_point(
        "B+ 树的设计核心: 让每个节点存更多 key → 树更矮 → 更少 IO。\n"
        "    为什么不在内存里也用 B+ 树？因为内存不需要——\n"
        "    二叉树 20 次内存访问 ≈ 2 微秒，已经足够快了。\n"
        "    数据结构的「好坏」取决于它运行的环境。"
    )


def main():
    print_header("s08: 内存 vs 磁盘 — ★ 过渡章")
    print(f"  {Color.HIGHLIGHT}核心问题: 数据大到内存装不下时，数据结构的设计会怎么变？{Color.RESET}\n")
    demo_the_gap()
    demo_why_btree()
    print(f"\n{Color.HIGHLIGHT}下一章 → s09: B+ 树 — 数据库索引的核心数据结构{Color.RESET}\n")


if __name__ == "__main__":
    main()
