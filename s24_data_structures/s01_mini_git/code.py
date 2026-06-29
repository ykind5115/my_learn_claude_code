#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s01: Mini Git — 链表 + 哈希 + DAG

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - 链表和数组的本质区别是什么？什么时候用链表？
  - Git 的 commit chain 为什么是单向链表而不是双向？
  - DAG 和树的区别是什么？为什么 Git 的 commit 历史是 DAG？
  - 哈希表在 Git 中起什么作用？
═══════════════════════════════════════════════════════════════

运行:
    python s24_data_structures/s01_mini_git/code.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import (
    Color, print_header, print_step, print_note, print_key_point,
    print_success, print_warning, print_linked_list,
)

# 导入本章的数据结构实现
from s01_mini_git.linked_list import LinkedList, Node
from s01_mini_git.commit_chain import CommitChain
from s01_mini_git.dag import DAG


def demo_linked_list():
    """演示链表的基本操作，建立直觉"""
    print_step(1, "链表基础 — 和数组的区别")

    linked = LinkedList()

    # 模拟 Git 的 commit 过程
    print_note("模拟 git commit 的过程...")
    linked.append("init: 项目启动")
    linked.append("feat: 添加 main.py")
    linked.append("fix: 修复登录 bug")
    linked.append("feat: 添加测试")

    print_linked_list(linked.head, lambda n: n.next, lambda n: n.value)

    print_key_point(
        "链表 = 每个节点知道「下一个是谁」\n"
        "    数组 = 所有元素排排坐，用索引直接访问\n\n"
        "    Git 的 commit 链 = 单向链表。\n"
        "    为什么是「单向」？因为现实世界中你只知道过去(我来自哪里)，\n"
        "    不知道未来(谁会在我后面)。"
    )

    # 演示查找
    print_step(2, "链表查找 — O(n)，必须从头遍历")
    target = linked.find("fix: 修复登录 bug")
    if target:
        print_note(f"找到: {target.value}")
        print_note(f"它在链表的第 {linked.to_list().index(target.value)} 个位置")
        print_note("要找到它，必须从 HEAD 开始一个个往下走——这就是 O(n)")


def demo_commit_chain():
    """演示 Commit Chain"""
    print_step(3, "Commit Chain — 链表的 Git 特化")

    chain = CommitChain()
    print_note("模拟 git init + git commit × 4...")
    chain.commit("第一次提交")
    chain.commit("添加功能 A")
    chain.commit("修复 bug")
    chain.commit("添加功能 B")

    chain.print_history()

    print_key_point(
        "每个 commit 只有一个 parent。\n"
        "    git log 就是从 HEAD 开始，沿着 parent 指针往回遍历。\n"
        "    这就是单向链表——只能「往前」(向旧版本)走。"
    )

    # 哈希查找
    print_step(4, "哈希索引 — O(1) 定位 commit")
    found = chain.find("c0002")
    if found:
        print_note(f"通过 hash 前缀 'c0002' 找到: {found}")
    print_key_point(
        "Git 用 SHA-1 哈希作为 commit 的「身份证号」。\n"
        "    哈希表 (dict) 让你 O(1) 定位任意 commit。\n"
        "    没有哈希表？你得遍历整个链表来找一个 commit。"
    )


def demo_dag():
    """演示 DAG"""
    print_step(5, "DAG — 当分支要合并时")

    dag = DAG()
    # 构建: main=A→B→C, feature=D→E(从B分出), merge=M(parent: C 和 E)
    dag.add_edge("C", "B"); dag.add_edge("B", "A")
    dag.add_edge("E", "D"); dag.add_edge("D", "B")
    dag.add_edge("M", "C"); dag.add_edge("M", "E")

    dag.print_structure()
    dag.print_topo_order()

    print_key_point(
        "Merge commit 有 2 个 parent → 链表不够用了 → 需要 DAG。\n"
        "    DAG = 每个节点可以有多个 parent，但不能有环。\n"
        "    拓扑排序 = 从旧到新排列 commit（保证 parent 在 child 前面）。"
    )


def demo_mini_git_preview():
    """展示 Mini Git 框架"""
    print_step(6, "Mini Git 框架预览")

    from s01_mini_git.mini_git import MiniGit

    git = MiniGit.init()
    git.status()

    print_note("框架已搭好。需要你实现的方法:")
    print_note("  - commit(message)     → 创建新 commit")
    print_note("  - log()              → 查看提交历史")
    print_note("  - branch(name)       → 创建分支")
    print_note("  - checkout(name)     → 切换分支")
    print_note("  - merge(branch_name) → 合并分支")


def main():
    print_header("s01: Mini Git — 链表 + 哈希 + DAG")

    print(f"""
  {Color.HIGHLIGHT}本章的三个数据结构:{Color.RESET}

    {Color.DIM}单向链表{Color.RESET} —— commit chain，每个 commit 知道它的 parent
    {Color.DIM}哈希表{Color.RESET}   —— 用 commit hash 在 O(1) 时间内定位对象
    {Color.DIM}DAG{Color.RESET}       —— 分支合并历史，一个节点可以有多个 parent
""")

    demo_linked_list()
    demo_commit_chain()
    demo_dag()
    demo_mini_git_preview()

    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示完成！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}✅ 你理解了: 链表 → commit chain → DAG 的渐进关系{Color.RESET}

   {Color.DIM}1. 链表是最简单的有序集合 —— 每个节点指向下一个{Color.RESET}
   {Color.DIM}2. Commit chain = 链表的特化 —— parent 是「上一个版本」{Color.RESET}
   {Color.DIM}3. DAG = 链表的推广 —— 一个节点可以有多个 parent (merge){Color.RESET}
   {Color.DIM}4. 哈希表 = O(1) 查找 —— 通过 hash 快速定位 commit{Color.RESET}

{Color.HIGHLIGHT}下一步: 打开 mini_git.py，实现标记为 TODO 的方法！{Color.RESET}
""")


if __name__ == "__main__":
    main()
