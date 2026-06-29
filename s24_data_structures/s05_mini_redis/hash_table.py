#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
哈希表 (Hash Table) — O(1) 键值存取

哈希表是现代软件中最常用的数据结构之一。Python 的 dict、Redis、
数据库索引都依赖它。

核心思想: 用一个「哈希函数」把 key 映射为数组索引。

    key ──→ [哈希函数] ──→ index ──→ 数组[index] = value

冲突处理: 两个不同的 key 可能映射到同一个 index。
  解决方案: 链地址法 (每个 slot 是一个链表)

动态扩容: 当负载因子 (size/capacity) 过高时，扩容并 rehash。

关键操作:
  put(key, value)  — 平均 O(1), 最坏 O(n)
  get(key)         — 平均 O(1), 最坏 O(n)
  delete(key)      — 平均 O(1), 最坏 O(n)

工程应用:
  - Python dict / set
  - Redis (整个数据库就是一个大哈希表)
  - 数据库索引 (Hash Index)
  - 缓存 (LRU Cache)
  - DNS 解析缓存
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import Color


class HashTable:
    """
    哈希表 — 链地址法实现

    空间复杂度: O(n)
    负载因子阈值: 0.75 (超过则扩容)
    """

    def __init__(self, initial_capacity=8):
        self._capacity = initial_capacity
        self._size = 0
        # 每个 slot 是一个 list (链表，存储 (key, value) 元组)
        self._buckets = [[] for _ in range(initial_capacity)]

    # ── 哈希函数 ─────────────────────────────────────────

    def _hash(self, key):
        """
        计算 key 的哈希值并映射到 bucket 索引。

        Python 内置 hash() 对相同对象保证相同哈希值。
        取模运算保证索引在 [0, capacity) 范围内。
        """
        h = hash(key)
        # Python 的 hash 可能是负数，取绝对值
        return abs(h) % self._capacity

    @property
    def load_factor(self):
        """负载因子 = 存储元素数 / 桶数量"""
        return self._size / self._capacity

    # ── 核心操作 ─────────────────────────────────────────

    def put(self, key, value):
        """
        插入或更新键值对 — 平均 O(1)

        1. 计算 key 的哈希 → 找到 bucket
        2. 遍历 bucket，如果 key 已存在 → 更新 value
        3. 否则追加到 bucket 尾部
        4. 检查是否需要扩容
        """
        idx = self._hash(key)
        bucket = self._buckets[idx]

        # 检查 key 是否已存在
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return

        # 新 key，追加
        bucket.append((key, value))
        self._size += 1

        # 扩容检查
        if self.load_factor > 0.75:
            self._resize(self._capacity * 2)

    def get(self, key, default=None):
        """
        获取 key 对应的值 — 平均 O(1)

        如果 key 不存在，返回 default。
        """
        idx = self._hash(key)
        for k, v in self._buckets[idx]:
            if k == key:
                return v
        return default

    def delete(self, key):
        """
        删除键值对 — 平均 O(1)
        返回: True (已删除) 或 False (key 不存在)
        """
        idx = self._hash(key)
        bucket = self._buckets[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self._size -= 1
                return True
        return False

    def __contains__(self, key):
        return self.get(key) is not None

    # ── 扩容 ────────────────────────────────────────────

    def _resize(self, new_capacity):
        """
        扩容并重新哈希所有元素 — O(n)

        为什么需要扩容？
          负载因子过高 → bucket 链表变长 → 查找退化到 O(n)
          扩容 + rehash → 保持 O(1)
        """
        old_buckets = self._buckets
        self._capacity = new_capacity
        self._buckets = [[] for _ in range(new_capacity)]
        self._size = 0  # put() 会重新计数

        for bucket in old_buckets:
            for key, value in bucket:
                self.put(key, value)  # 重新计算索引并插入

    # ── 信息方法 ─────────────────────────────────────────

    def keys(self):
        """返回所有 key"""
        result = []
        for bucket in self._buckets:
            for k, v in bucket:
                result.append(k)
        return result

    def __len__(self):
        return self._size

    def __repr__(self):
        items = []
        for bucket in self._buckets:
            for k, v in bucket:
                items.append(f"{k!r}: {v!r}")
        return f"HashTable({{{', '.join(items)}}})"

    def print_structure(self):
        """打印哈希表内部结构 (可视化冲突)"""
        print(f"\n  {Color.HIGHLIGHT}哈希表内部结构 (容量={self._capacity}, 元素={self._size}):{Color.RESET}")
        for i, bucket in enumerate(self._buckets):
            if bucket:
                chain = " → ".join(f"({k!r}:{v!r})" for k, v in bucket)
                print(f"  [{i:2d}] {chain}")
            else:
                print(f"  [{i:2d}] {Color.DIM}(空){Color.RESET}")


# ═══════════════════════════════════════════════════════════════
# 演示
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    from utils import print_step, print_key_point, print_note

    print(f"\n{Color.HEADER}  哈希表 — O(1) 键值存取{Color.RESET}\n")

    ht = HashTable(4)  # 故意用小容量来观察扩容

    print_step("1", "插入 + 观察冲突和扩容")
    for i in range(8):
        ht.put(f"key-{i}", f"value-{i}")
    ht.print_structure()

    print_step("2", "查找 — O(1)")
    print_note(f"get('key-3') = {ht.get('key-3')!r}")
    print_note(f"get('nonexistent') = {ht.get('nonexistent', 'N/A')!r}")

    print_step("3", "删除")
    ht.delete("key-3")
    print_note(f"删除 'key-3' 后, get = {ht.get('key-3', 'N/A')!r}")

    print_key_point(
        "哈希表的威力: put/get/delete 平均 O(1)\n"
        "    代价: 无序 (key 之间没有顺序关系)\n"
        "    代价: 空间 (需要预留空桶)\n"
        "    代价: 最坏 O(n) (所有 key 碰撞到同一个 bucket)"
    )
