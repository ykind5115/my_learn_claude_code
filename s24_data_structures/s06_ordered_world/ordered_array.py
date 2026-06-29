#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
有序数组 + 二分查找

哈希表给了我们 O(1) 存取，但它有一个致命的盲区:
  key 之间没有顺序关系！你无法做:
    - 范围查询 (80~90 分的学生)
    - 排名 (第 10 名是谁？)
    - 顺序遍历 (按字母顺序列出用户)

有序数组解决了这些问题，但带来了新的代价:
    - 插入: O(n) (保持有序需要移动元素)
    - 查找: O(log n) (二分查找)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import Color


def binary_search(arr, target, key=lambda x: x):
    """
    二分查找 — O(log n)

    每次排除一半的搜索空间。
    前提: 数组必须有序。
    """
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        mid_val = key(arr[mid])
        if mid_val == target:
            return mid
        elif mid_val < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1  # 未找到


class OrderedArray:
    """
    有序数组 — 插入时保持有序

    操作:
      insert(item)   — O(n) 保持有序
      search(key)    — O(log n) 二分查找
      range_query(lo, hi) — O(log n + k) k=结果数量
      top_n(n)       — O(1) 取前 n 个 (数组天然有序)
    """

    def __init__(self, key_func=lambda x: x):
        self._data = []
        self.key_func = key_func  # 提取排序键的函数

    def insert(self, item):
        """插入并保持有序 — O(n) (需要移动元素)"""
        key = self.key_func(item)
        # 找到插入位置
        left, right = 0, len(self._data)
        while left < right:
            mid = (left + right) // 2
            if self.key_func(self._data[mid]) < key:
                left = mid + 1
            else:
                right = mid
        self._data.insert(left, item)

    def search(self, key):
        """二分查找 — O(log n)"""
        idx = binary_search(self._data, key, self.key_func)
        return self._data[idx] if idx >= 0 else None

    def range_query(self, lo, hi):
        """
        范围查询 — O(log n + k)
        返回所有 key 在 [lo, hi] 范围内的元素。
        这是哈希表做不到的。
        """
        # 找到起始位置 (lower_bound)
        left, right = 0, len(self._data)
        while left < right:
            mid = (left + right) // 2
            if self.key_func(self._data[mid]) < lo:
                left = mid + 1
            else:
                right = mid

        result = []
        i = left
        while i < len(self._data) and self.key_func(self._data[i]) <= hi:
            result.append(self._data[i])
            i += 1
        return result

    def top_n(self, n):
        """取最大的 n 个元素 — O(1) (数组天然有序)"""
        return self._data[-n:] if n <= len(self._data) else self._data[:]

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"OrderedArray({self._data})"


# ═══════════════════════════════════════════════════════════════
# 演示
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    from utils import print_step, print_key_point, print_note

    print(f"\n{Color.HEADER}  有序数组 + 二分查找{Color.RESET}\n")

    oa = OrderedArray(key_func=lambda x: x["score"])

    print_step("1", "插入 — O(n) 但保持有序")
    for score in [85, 92, 78, 95, 88, 76, 90]:
        oa.insert({"name": f"学生{score}", "score": score})
    print_note(f"数据: {oa}")

    print_step("2", "二分查找 — O(log n)")
    found = oa.search(88)
    print_note(f"search(88) = {found}")

    print_step("3", "范围查询 — O(log n + k)，哈希表做不到！")
    results = oa.range_query(80, 90)
    print_note(f"分数 80~90: {results}")

    print_step("4", "Top 3 — O(1)，哈希表做不到！")
    print_note(f"Top 3: {oa.top_n(3)}")

    print_key_point(
        "有序数组 = 查询快(O(log n)), 插入慢(O(n))\n"
        "    哈希表 = 查询快(O(1)),   插入快(O(1)), 但不能排序和范围查询\n\n"
        "    问题: 有没有「插入快 + 查询快 + 能排序」的数据结构？\n"
        "    → 跳表 (Skip List) — 下一章见"
    )
