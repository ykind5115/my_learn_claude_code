#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跳表 (Skip List) — 概率平衡的有序数据结构

跳表 = 多层索引的有序链表。

核心思想: 给链表加「快速通道」。
  第 0 层: 完整的有序链表 (包含所有元素)
  第 1 层: 每 2 个元素取 1 个作为索引
  第 2 层: 每 4 个元素取 1 个
  ...

查找时从最高层开始，找到目标区间后「下降」一层继续。
这就像在高速公路上开车: 先走高速(高层)，接近出口时换到普通道路(低层)。

复杂度 (期望):
  insert:  O(log n)
  search:  O(log n)
  delete:  O(log n)
  rank:   O(log n) (需要维护 span)

为什么不用平衡树？跳表实现更简单，性能相当，Redis 就用跳表做排行榜。
"""

import random
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import Color


class SkipNode:
    """跳表节点"""

    def __init__(self, key, value, level):
        self.key = key
        self.value = value
        # forward[i] = 第 i 层指向的下一个节点
        self.forward = [None] * (level + 1)
        # span[i] = 第 i 层到下一个节点跨越了多少个第 0 层节点 (用于排名)
        self.span = [0] * (level + 1)

    def __repr__(self):
        return f"SkipNode({self.key}:{self.value}, Lv={len(self.forward)-1})"


class SkipList:
    """
    跳表 — 支持插入、查找、删除、排名、Top N

    最大层数: 16 (支持 2^16 ≈ 65000 个元素)
    """

    MAX_LEVEL = 16

    def __init__(self):
        # 头节点 (哨兵)，key 为 None，所有层都指向 None
        self.head = SkipNode(None, None, self.MAX_LEVEL)
        self.level = 0   # 当前最高层
        self._size = 0

    def _random_level(self):
        """
        随机生成新节点的层数。
        每层有 50% 概率再升一层 (概率递减)。
        """
        level = 0
        while random.random() < 0.5 and level < self.MAX_LEVEL:
            level += 1
        return level

    def insert(self, key, value):
        """
        插入键值对 — 期望 O(log n)

        1. 从最高层开始，找到每一层的插入位置
        2. 随机生成新节点的层数
        3. 在各层插入新节点
        """
        update = [None] * (self.MAX_LEVEL + 1)  # 每层的前驱节点
        rank = [0] * (self.MAX_LEVEL + 1)        # 每层的排名偏移
        current = self.head

        # 从最高层往下找插入位置
        for i in range(self.level, -1, -1):
            if i == self.level:
                rank[i] = 0
            else:
                rank[i] = rank[i + 1]
            while current.forward[i] and current.forward[i].key < key:
                rank[i] += current.span[i]
                current = current.forward[i]
            update[i] = current

        # 随机生成新节点层数
        new_level = self._random_level()
        if new_level > self.level:
            for i in range(self.level + 1, new_level + 1):
                update[i] = self.head
            self.level = new_level

        # 创建新节点并插入各层
        new_node = SkipNode(key, value, new_level)
        for i in range(new_level + 1):
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node
            # 更新 span
            new_node.span[i] = update[i].span[i] - (rank[0] - rank[i]) if update[i].forward[i] else 0
            update[i].span[i] = (rank[0] - rank[i]) + 1

        self._size += 1
        return True

    def search(self, key):
        """
        查找 — 期望 O(log n)
        返回 value 或 None。
        """
        current = self.head
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
        current = current.forward[0]
        if current and current.key == key:
            return current.value
        return None

    def delete(self, key):
        """删除 — 期望 O(log n)"""
        update = [None] * (self.MAX_LEVEL + 1)
        current = self.head
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current

        target = current.forward[0]
        if target and target.key == key:
            for i in range(self.level + 1):
                if update[i].forward[i] != target:
                    break
                update[i].forward[i] = target.forward[i]
            while self.level > 0 and self.head.forward[self.level] is None:
                self.level -= 1
            self._size -= 1
            return True
        return False

    def get_rank(self, key):
        """
        获取排名 — 期望 O(log n)

        返回: 1-based 排名 (第 1 名最小)，如果 key 不存在返回 -1。
        这是哈希表和有序数组都做不到的 (哈希表做不到，有序数组 O(n))。
        """
        current = self.head
        rank = 0
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key <= key:
                rank += current.span[i]
                current = current.forward[i]
        if current and current.key == key:
            return rank
        return -1

    def top_n(self, n):
        """
        取最大的 n 个 — O(n) (需要遍历第 0 层尾部)
        返回 [(key, value), ...] 从大到小排列
        """
        # 走到第 0 层的最后一个节点
        current = self.head
        for i in range(self.level, -1, -1):
            while current.forward[i]:
                current = current.forward[i]

        # 从尾部往回找 top n (跳表只有单向，这里简化遍历前 size-n 个元素)
        result = []
        current = self.head.forward[0]
        skip = max(0, self._size - n)
        for _ in range(skip):
            current = current.forward[0]
        while current:
            result.append((current.key, current.value))
            current = current.forward[0]
        return result

    def __len__(self):
        return self._size

    def print_structure(self, max_items=8):
        """打印跳表结构"""
        print(f"\n  {Color.HIGHLIGHT}跳表结构 (层数={self.level+1}, 元素={self._size}):{Color.RESET}")
        for i in range(self.level, -1, -1):
            nodes = []
            current = self.head.forward[i]
            count = 0
            while current and count < max_items:
                nodes.append(f"{current.key}:{current.value}")
                current = current.forward[i]
                count += 1
            if current:
                nodes.append("...")
            print(f"  Lv{i}: {' → '.join(nodes) if nodes else '(空)'}")
        print()


# ═══════════════════════════════════════════════════════════════
# 演示
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    from utils import print_step, print_key_point, print_note

    print(f"\n{Color.HEADER}  跳表 — 概率平衡的快速有序结构{Color.RESET}\n")

    sl = SkipList()

    print_step("1", "插入数据")
    for score, name in [(85, "Alice"), (92, "Bob"), (78, "Charlie"), (95, "Diana"), (88, "Eve")]:
        sl.insert(score, name)
        print_note(f"insert({score}, '{name}')")
    sl.print_structure()

    print_step("2", "查找 + 排名")
    print_note(f"search(88) = {sl.search(88)!r}")
    print_note(f"rank(88) = 第 {sl.get_rank(88)} 名")
    print_note(f"rank(95) = 第 {sl.get_rank(95)} 名 (最高分)")

    print_step("3", "Top 3")
    print_note(f"top_3 = {sl.top_n(3)}")

    print_key_point(
        "跳表 = 多层索引的链表。查找/插入/删除期望 O(log n)。\n"
        "    比平衡树简单，性能相当。Redis 用它做排行榜。\n"
        "    代价: 额外空间 (多层索引)，概率性 (最坏可能退化)。"
    )
