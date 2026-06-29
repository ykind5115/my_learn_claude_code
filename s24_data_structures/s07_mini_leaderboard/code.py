#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s07: Mini Leaderboard — 跳表

运行: python s24_data_structures/s07_mini_leaderboard/code.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import (
    Color, print_header, print_step, print_note, print_key_point, print_success,
)
from s07_mini_leaderboard.skip_list import SkipList
from s07_mini_leaderboard.mini_leaderboard import DemoLeaderboard


def demo_skip_list():
    print_step(1, "跳表 — 多层索引的有序链表")
    sl = SkipList()
    for score, name in [(85, "Alice"), (92, "Bob"), (78, "Charlie"), (95, "Diana"), (88, "Eve")]:
        sl.insert(score, name)
    sl.print_structure()

    print_note(f"search(88) = '{sl.search(88)}'")
    print_note(f"rank(88)  = 第 {sl.get_rank(88)} 名")
    print_note(f"Top 3    = {sl.top_n(3)}")

    print_key_point(
        "跳表 = 给链表加了「高速公路」。\n"
        "    高层索引让你快速跳过大量元素，接近目标时下降到低层。\n"
        "    插入和查找都是期望 O(log n)。"
    )


def demo_leaderboard():
    print_step(2, "Mini Leaderboard — 跳表应用")
    lb = DemoLeaderboard()
    players = [("Alice", 1500), ("Bob", 2200), ("Charlie", 1800),
               ("Diana", 2500), ("Eve", 1200), ("Frank", 1900)]
    for name, score in players:
        lb.update_score(name, score)

    print_note("排行榜:")
    for i, (score, name) in enumerate(reversed(lb.get_top_n(10)), 1):
        print_note(f"  #{i} {name}: {score}")

    print_note(f"Alice 的排名: #{lb.get_rank('Alice')}")
    lb.update_score("Eve", 2600)
    print_note("Eve 分数更新为 2600 后:")
    print_note(f"Eve 的排名: #{lb.get_rank('Eve')}")
    print_note(f"新的 #1: {lb.get_top_n(1)}")


def main():
    print_header("s07: Mini Leaderboard — 跳表")
    print(f"  {Color.HIGHLIGHT}数据结构: 跳表 (Skip List) — O(log n) 插入 + 排名{Color.RESET}\n")
    demo_skip_list()
    demo_leaderboard()
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"\n{Color.SUCCESS}✅ 跳表解决了「插入快 + 能排名」的矛盾。Redis sorted set 就是用跳表。{Color.RESET}")
    print(f"{Color.HIGHLIGHT}下一步: 打开 mini_leaderboard.py，实现 TODO 方法！{Color.RESET}\n")


if __name__ == "__main__":
    main()
