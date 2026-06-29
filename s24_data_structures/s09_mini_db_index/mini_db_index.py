#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini DB Index — 基于 B+ 树的数据库索引

═══════════════════════════════════════════════════════════════
数据库索引的作用: 不用扫描全表就能找到数据。

例如:
  SELECT * FROM users WHERE age = 25;
  没有索引: 扫描所有 100 万行 → O(n)
  有索引:   B+ 树查找 age=25 → O(log n)

你的任务: 实现 DBIndex 类中标记为 TODO 的方法。
"""

import sys
from pathlib import Path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from s09_mini_db_index.bplus_tree import BPlusTree


class DBIndex:
    """迷你数据库索引"""

    def __init__(self, name="idx"):
        self.name = name
        self.tree = BPlusTree(order=50)  # 大 order 模拟真实场景

    def insert(self, key, row_id):
        """
        插入索引条目 — key 是要索引的列的值，row_id 是行标识。

        提示: self.tree.insert(key, row_id)
        """
        # TODO: 实现 insert
        raise NotImplementedError("TODO: 实现 insert")

    def search(self, key):
        """
        精确查找 — 返回匹配的 row_id 列表。

        提示: val = self.tree.search(key); return [val] if val else []
        """
        # TODO: 实现 search
        raise NotImplementedError("TODO: 实现 search")

    def range_query(self, lo, hi):
        """
        范围查询 — 返回 key 在 [lo, hi] 范围内的所有 row_id。

        提示: 返回 self.tree.range_query(lo, hi)
        """
        # TODO: 实现 range_query
        raise NotImplementedError("TODO: 实现 range_query")

    def delete(self, key):
        """删除索引条目"""
        pass  # B+ 树删除较复杂，本章跳过


class DemoDBIndex(DBIndex):
    def insert(self, key, row_id):
        self.tree.insert(key, row_id)

    def search(self, key):
        val = self.tree.search(key)
        return [val] if val is not None else []

    def range_query(self, lo, hi):
        return self.tree.range_query(lo, hi)
