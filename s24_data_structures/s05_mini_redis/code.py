#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s05: Mini Redis — 哈希表

运行: python s24_data_structures/s05_mini_redis/code.py
"""

import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import (
    Color, print_header, print_step, print_note, print_key_point, print_success,
)
from s05_mini_redis.hash_table import HashTable
from s05_mini_redis.mini_redis import DemoMiniRedis


def demo_hash_table():
    print_step(1, "哈希表基础 — put / get / delete O(1)")
    ht = HashTable()
    ht.put("name", "Alice")
    ht.put("age", 30)
    ht.put("city", "Beijing")
    print_note(f"get('name') = {ht.get('name')!r}")
    print_note(f"get('age')  = {ht.get('age')!r}")
    print_note(f"'email' in ht? {'email' in ht}")
    ht.print_structure()

    print_key_point(
        "哈希表的核心: 用哈希函数把 key 变成数组索引。\n"
        "    好哈希函数 = 均匀分布 → O(1)\n"
        "    坏哈希函数 = 所有 key 碰撞 → O(n)"
    )


def demo_collision_and_resize():
    print_step(2, "冲突处理 + 动态扩容")
    ht = HashTable(4)
    print_note("初始容量=4，负载因子阈值=0.75")
    for i in range(8):
        ht.put(f"key-{i}", i)
        print_note(f"put('key-{i}') → 容量={ht._capacity}, 负载={ht.load_factor:.2f}")
    print_note("注意: 超过 0.75 阈值后自动扩容了！")


def demo_mini_redis():
    print_step(3, "Mini Redis — 带 TTL 的哈希表")
    r = DemoMiniRedis()
    r.set("user:1", {"name": "Alice", "age": 30})
    r.set("user:2", {"name": "Bob", "age": 25})
    r.set("temp:token", "abc123", ttl=1)
    print_note(f"get('user:1') = {r.get('user:1')!r}")
    print_note(f"keys() = {r.keys()}")
    print_note("等待 2 秒让 temp:token 过期...")
    time.sleep(2)
    print_note(f"get('temp:token') = {r.get('temp:token', 'EXPIRED')!r}")
    print_note(f"ttl('user:1') = {r.ttl('user:1')} (永不过期)")

    print_key_point("Redis = 哈希表 + TTL + 持久化 + 网络协议。核心就是哈希表。")


def main():
    print_header("s05: Mini Redis — 哈希表")
    print(f"  {Color.HIGHLIGHT}数据结构: 哈希表 (Hash Table) — O(1) 键值存取{Color.RESET}\n")

    demo_hash_table()
    demo_collision_and_resize()
    demo_mini_redis()

    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"\n{Color.SUCCESS}✅ 哈希表 = O(1) 存取的魔法。代价是无法做范围查询和排序。{Color.RESET}")
    print(f"{Color.HIGHLIGHT}下一步: 打开 mini_redis.py，实现 TODO 方法！{Color.RESET}\n")


if __name__ == "__main__":
    main()
