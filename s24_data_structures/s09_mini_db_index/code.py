#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s09: Mini DB Index — B+ 树

运行: python s24_data_structures/s09_mini_db_index/code.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import (
    Color, print_header, print_step, print_note, print_key_point, print_success,
)
from s09_mini_db_index.bplus_tree import BPlusTree
from s09_mini_db_index.mini_db_index import DemoDBIndex


def demo_bplus_tree():
    print_step(1, "B+ 树的结构 — 宽而浅")
    tree = BPlusTree(order=5)
    for i in [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45, 55, 65, 75, 90]:
        tree.insert(i, f"data-{i}")
    tree.print_structure()
    print_note(f"search(60) = '{tree.search(60)}'")
    print_note(f"range_query[30, 60] = {tree.range_query(30, 60)}")

    print_key_point(
        "B+ 树的核心优势:\n"
        "    1. 树矮 (order=5, 3 层能存 ~125 条; order=500, 3 层能存 1.25 亿条)\n"
        "    2. 叶子链表 → 范围查询不需要回溯内部节点\n"
        "    3. 节点大 → 每次 IO 读取的 key 多 → 利用率高"
    )


def demo_db_index():
    print_step(2, "Mini DB Index — B+ 树做数据库索引")
    idx = DemoDBIndex("age_idx")
    # 模拟 users 表: (id, name, age)
    users = [(1, "Alice", 25), (2, "Bob", 30), (3, "Charlie", 25),
             (4, "Diana", 35), (5, "Eve", 28)]
    for uid, name, age in users:
        idx.insert(age, uid)
    print_note("索引已建立: age → user_id")
    print_note(f"age=25 的用户: user_id={idx.search(25)}")
    print_note(f"age 在 [25,30]: {idx.range_query(25, 30)}")

    print_key_point("没有索引 = 全表扫描 O(n)。有 B+ 树索引 = O(log n)。")


def main():
    print_header("s09: Mini DB Index — B+ 树")
    print(f"  {Color.HIGHLIGHT}数据结构: B+ 树 — 磁盘友好的多路搜索树{Color.RESET}\n")
    demo_bplus_tree()
    demo_db_index()
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"\n{Color.SUCCESS}✅ B+ 树 = 数据库索引的标准答案。宽节点 + 矮树 = 少 IO。{Color.RESET}")
    print(f"{Color.HIGHLIGHT}下一步: 打开 mini_db_index.py，实现 TODO 方法！{Color.RESET}\n")


if __name__ == "__main__":
    main()
