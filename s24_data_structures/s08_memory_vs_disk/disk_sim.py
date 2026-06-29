#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
磁盘模拟器 — 理解内存和磁盘的性能鸿沟

核心数字:
  内存访问: ~100 纳秒 (0.0001 毫秒)
  磁盘 IO:   ~10 毫秒
  差距:      约 100,000 倍

这意味着: 一个在内存里跑得很欢的数据结构，放到磁盘上可能慢 10 万倍。
这就是为什么数据库需要 B+ 树——它把几百个 key 塞进一个节点，
把 IO 次数从 O(log₂ n) 降到 O(log₅₀₀ n)。
"""

import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import Color


class DiskSimulator:
    """
    磁盘模拟器。

    模拟磁盘的关键特性: 每次随机访问有固定延迟。
    - IO_DELAY: 每次读/写的模拟延迟 (默认 0.01s = 10ms)
    - 统计 IO 次数
    """

    def __init__(self, io_delay=0.01, name="disk"):
        self.io_delay = io_delay
        self.name = name
        self.io_count = 0
        self._blocks = {}  # block_id → data

    def read(self, block_id):
        """模拟磁盘读取 — 一次 IO"""
        self.io_count += 1
        if self.io_delay > 0:
            time.sleep(self.io_delay)
        return self._blocks.get(block_id)

    def write(self, block_id, data):
        """模拟磁盘写入 — 一次 IO"""
        self.io_count += 1
        if self.io_delay > 0:
            time.sleep(self.io_delay)
        self._blocks[block_id] = data

    def reset_stats(self):
        self.io_count = 0

    def stats(self):
        return f"{self.name}: {self.io_count} 次 IO, 约 {self.io_count * self.io_delay:.3f}s"


class MemorySimulator:
    """内存模拟器 — 无延迟 (基准对比)"""

    def __init__(self):
        self._data = {}
        self.access_count = 0

    def read(self, addr):
        self.access_count += 1
        return self._data.get(addr)

    def write(self, addr, data):
        self.access_count += 1
        self._data[addr] = data

    def stats(self):
        return f"memory: {self.access_count} 次访问, ~0s"


# ═══════════════════════════════════════════════════════════════
# 演示
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    from utils import print_step, print_key_point, print_note, print_warning

    print(f"\n{Color.HEADER}  磁盘模拟器 — 理解 IO 瓶颈{Color.RESET}\n")

    disk = DiskSimulator(io_delay=0.001, name="HDD")  # 1ms 用于演示
    mem = MemorySimulator()

    print_step("1", "对比: 在内存和磁盘上做 100 次查找")

    # 内存版本
    start = time.perf_counter()
    for i in range(100):
        mem.write(f"key-{i}", f"value-{i}")
    for i in range(100):
        mem.read(f"key-{i}")
    mem_time = time.perf_counter() - start

    # 磁盘版本 (有延迟)
    start = time.perf_counter()
    for i in range(100):
        disk.write(f"key-{i}", f"value-{i}")
    for i in range(100):
        disk.read(f"key-{i}")
    disk_time = time.perf_counter() - start

    print_note(f"内存版: {mem_time:.3f}s ({mem.stats()})")
    print_note(f"磁盘版: {disk_time:.3f}s ({disk.stats()})")
    print_warning(f"慢了多少倍？{disk_time/mem_time:.0f}x！")

    print_key_point(
        "内存和磁盘的根本差异:\n"
        "    内存访问 ≈ 100ns, 磁盘 IO ≈ 10ms → 差 100,000 倍\n\n"
        "    这意味着: 跳表在磁盘上查 20 个节点 = 20 次 IO = 200ms\n"
        "    B+ 树查 3 个节点 = 3 次 IO = 30ms\n\n"
        "    数据结构的设计必须考虑「数据在哪」——内存还是磁盘。"
    )
