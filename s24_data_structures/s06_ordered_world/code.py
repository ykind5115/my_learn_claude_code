#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s06: 有序 vs 无序 — 为什么哈希表不够？

运行: python s24_data_structures/s06_ordered_world/code.py
"""

import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import (
    Color, print_header, print_step, print_note, print_key_point, print_success,
    compare_performance,
)
from s06_ordered_world.ordered_array import OrderedArray, binary_search
from s05_mini_redis.hash_table import HashTable


def demo_problem():
    """展示哈希表的盲区"""
    print_step(1, "哈希表的盲区 — 无法排序、无法范围查询、无法排名")

    ht = HashTable()
    students = [("Alice", 92), ("Bob", 78), ("Charlie", 85), ("Diana", 95), ("Eve", 88)]
    for name, score in students:
        ht.put(name, score)

    print_note("哈希表里的数据:")
    for name, score in students:
        print_note(f"  {name}: {score}")

    print(f"\n  {Color.WARNING}问题 1: 按分数从高到低排列学生？{Color.RESET}")
    print(f"  {Color.DIM}  → 哈希表做不到——key 之间没有顺序关系{Color.RESET}")
    print(f"  {Color.DIM}  → 只能取出所有数据，手动排序: O(n log n){Color.RESET}")

    print(f"\n  {Color.WARNING}问题 2: 分数在 80~90 之间的学生？{Color.RESET}")
    print(f"  {Color.DIM}  → 哈希表做不到——必须遍历所有 5 个学生{Color.RESET}")

    print(f"\n  {Color.WARNING}问题 3: 第一名是谁？{Color.RESET}")
    print(f"  {Color.DIM}  → 哈希表做不到——没有「排名」概念{Color.RESET}")

    print_key_point(
        "O(1) 存取代价: 数据之间的「顺序关系」完全丢失了。\n"
        "    范围查询、排序、排名——这些都是「有序世界」的需求。"
    )


def demo_ordered_array():
    """展示有序数组的优势和劣势"""
    print_step(2, "有序数组 — 解决了排序/范围查询，但插入变成了 O(n)")

    oa = OrderedArray(key_func=lambda x: x[1])  # 按分数排序
    scores = [85, 92, 78, 95, 88]

    print_note("插入数据 (每次插入都要保持有序)...")
    for s in scores:
        oa.insert(("学生", s))

    print_note(f"有序数组: {oa}")
    print_note(f"范围查询 80~90: {oa.range_query(80, 90)}")
    print_note(f"Top 3: {oa.top_n(3)}")

    # 性能对比
    print_step(3, "性能对比: 哈希表 vs 有序数组")

    n = 10000
    # 插入性能
    ht = HashTable()
    start = time.perf_counter()
    for i in range(n):
        ht.put(f"key-{i}", i)
    ht_time = time.perf_counter() - start

    oa2 = OrderedArray()
    start = time.perf_counter()
    for i in range(n):
        oa2.insert(i)
    oa_time = time.perf_counter() - start

    compare_performance("哈希表 insert", ht_time, "有序数组 insert", oa_time)

    print_key_point(
        "哈希表: 插入 O(1) → 快。但不能排序/范围查询。\n"
        "    有序数组: 插入 O(n) → 慢。但能排序/范围查询/排名。\n\n"
        "    有没有「插入快 + 能排序」的数据结构？\n"
        "    → 跳表 (Skip List) —— 下一章！"
    )


def main():
    print_header("s06: 有序 vs 无序 — ★ 过渡章")
    print(f"  {Color.HIGHLIGHT}核心问题: 哈希表 O(1) 很爽，但怎么做范围查询和排序？{Color.RESET}\n")
    demo_problem()
    demo_ordered_array()
    print(f"\n{Color.HIGHLIGHT}下一章 → s07: 跳表 — 插入 O(log n) + 能排序 + 能排名！{Color.RESET}\n")


if __name__ == "__main__":
    main()
