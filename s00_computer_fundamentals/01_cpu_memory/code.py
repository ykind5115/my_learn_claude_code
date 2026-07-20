#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s00-01: CPU、内存、缓存 — 存储金字塔，局部性原理

学习目标:
  - 感受 CPU vs I/O 的速度差距
  - 理解内存地址和对象引用
  - 体验缓存的加速效果

运行: python 01_cpu_memory/code.py
"""

import time
import sys
from functools import lru_cache


# ═══════════════════════════════════════════════════════════
# Demo 1: CPU 密集 vs I/O 密集 — 速度天壤之别
# ═══════════════════════════════════════════════════════════
def demo_1_cpu_vs_io():
    print("── Demo 1: CPU 密集 vs I/O 密集 ──")

    # CPU 密集：纯计算
    start = time.time()
    total = 0
    for i in range(10_000_000):
        total += i
    cpu_time = time.time() - start
    print(f"  CPU 密集 (1000 万次加法): {cpu_time:.4f}s")
    print(f"    每秒执行约 {10 / cpu_time:.0f} 百万次加法")

    # I/O 密集：写文件
    start = time.time()
    with open("/tmp/s00_demo.txt", "w") as f:
        for i in range(10000):
            f.write(f"line {i}\n")
    io_time = time.time() - start
    print(f"  I/O 密集 (写 10000 行到文件): {io_time:.4f}s")

    # 内存访问
    start = time.time()
    data = list(range(10_000_000))
    _ = sum(data)
    mem_time = time.time() - start
    print(f"  内存访问 (求和 1000 万元素): {mem_time:.4f}s")

    print(f"  → CPU 计算比 I/O 快 1000-100000 倍")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 2: 内存地址 — id() 看对象在哪
# ═══════════════════════════════════════════════════════════
def demo_2_memory_address():
    print("── Demo 2: 内存地址 ──")

    # 可变对象：列表
    a = [1, 2, 3]
    b = a          # b 指向同一个列表
    c = [1, 2, 3]  # c 是新建的列表，值相同但地址不同

    print(f"  a = [1, 2, 3]")
    print(f"  b = a")
    print(f"  c = [1, 2, 3]")
    print(f"  id(a) = {id(a)}")
    print(f"  id(b) = {id(b)}  (和 a 相同 → 同一个对象)")
    print(f"  id(c) = {id(c)}  (不同于 a → 新创建的对象)")
    print(f"  a is b → {a is b}")
    print(f"  a is c → {a is c} (值相同但不是同一个对象)")

    # 小整数的驻留
    print()
    x = 256
    y = 256
    print(f"  x=256, y=256: x is y → {x is y} (小整数被 Python 驻留)")
    x = 257
    y = 257
    print(f"  x=257, y=257: x is y → {x is y} (超出驻留范围)")

    # 对象大小
    print()
    print(f"  sys.getsizeof(42): {sys.getsizeof(42)} bytes")
    print(f"  sys.getsizeof('hello'): {sys.getsizeof('hello')} bytes")
    print(f"  sys.getsizeof([1,2,3]): {sys.getsizeof([1, 2, 3])} bytes")
    print(f"  sys.getsizeof([1,2,3]*1000): {sys.getsizeof([1, 2, 3] * 1000)} bytes")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 3: LRU Cache — 缓存加速
# ═══════════════════════════════════════════════════════════
def demo_3_lru_cache():
    print("── Demo 3: LRU Cache 缓存加速 ──")

    # 模拟一个"昂贵"的计算
    def expensive_calculation(n):
        """没有缓存——每次都要算"""
        time.sleep(0.1)  # 模拟耗时操作
        return n * n

    @lru_cache(maxsize=128)
    def cached_calculation(n):
        """有缓存——算过的直接返回"""
        time.sleep(0.1)
        return n * n

    # 无缓存
    print("  无缓存 (调用 5 次，3 次重复):")
    start = time.time()
    for _ in range(5):
        expensive_calculation(42)  # 每次都重新算
    print(f"    耗时: {time.time() - start:.3f}s")

    # 有缓存
    print("  有 LRU Cache (同样调用 5 次):")
    start = time.time()
    for _ in range(5):
        cached_calculation(42)  # 第一次算，后面 4 次读缓存
    print(f"    耗时: {time.time() - start:.3f}s")
    print(f"  → 缓存后实际计算 1 次，命中 4 次")

    # 查看缓存信息
    info = cached_calculation.cache_info()
    print(f"  cache_info: hits={info.hits}, misses={info.misses}")
    print(f"  → 这和 Anthropic Prompt Caching 的原理一模一样")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 4: 空间局部性 — 顺序 vs 随机访问
# ═══════════════════════════════════════════════════════════
def demo_4_spatial_locality():
    print("── Demo 4: 空间局部性 — 顺序 vs 随机访问 ──")

    import random
    SIZE = 5_000_000
    arr = list(range(SIZE))

    # 顺序访问 — CPU 预取友好
    start = time.time()
    total = 0
    for i in range(SIZE):
        total += arr[i]  # 相邻地址，缓存命中率高
    seq_time = time.time() - start
    print(f"  顺序访问 (0→{SIZE}): {seq_time:.4f}s")

    # 随机访问 — 缓存大量失效
    indices = list(range(SIZE))
    random.shuffle(indices)
    start = time.time()
    total = 0
    for i in indices:
        total += arr[i]  # 到处跳，缓存频繁失效
    rand_time = time.time() - start
    print(f"  随机访问 (打乱顺序): {rand_time:.4f}s")

    if rand_time > seq_time:
        print(f"  顺序比随机快: {rand_time / seq_time:.1f}x")
        print(f"  → 这就是空间局部性：访问相邻地址时缓存有效")
    print()


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("s00-01: CPU、内存、缓存 — 存储金字塔")
    print("=" * 60)
    print()

    demo_1_cpu_vs_io()
    demo_2_memory_address()
    demo_3_lru_cache()
    demo_4_spatial_locality()

    print("─" * 60)
    print("小结:")
    print("  CPU 计算: 纳秒级，I/O: 毫秒级 → 相差百万倍")
    print("  内存地址: id() 看对象在哪，小整数被驻留")
    print("  缓存原理: 记住结果，下次直接用 (LRU Cache → Prompt Caching)")
    print("  局部性: 顺序访问比随机访问快很多")
