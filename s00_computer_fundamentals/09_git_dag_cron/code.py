#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s00-09: Git、DAG、Cron — 工程基础设施

学习目标:
  - 理解 Git 的 commit/branch/worktree 模型
  - 理解 DAG 和拓扑排序
  - 理解 Cron 表达式

运行: python 09_git_dag_cron/code.py
"""

import os
import subprocess
from collections import deque


# ═══════════════════════════════════════════════════════════
# Demo 1: Git 基本操作 (subprocess 调 git)
# ═══════════════════════════════════════════════════════════
def demo_1_git():
    print("── Demo 1: Git 基本概念 ──")

    print("  Git 的核心对象:")
    print("    commit  = 一次保存的快照 (用 SHA-1 hash 标识)")
    print("    branch  = 指向某个 commit 的指针 (轻量级)")
    print("    worktree = 同一仓库的多份工作副本")

    # 检查当前是否有 git
    try:
        r = subprocess.run(["git", "rev-parse", "--git-dir"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            print()
            print(f"  当前在 Git 仓库中: {r.stdout.strip()}")

            r2 = subprocess.run(["git", "log", "--oneline", "-5"],
                                capture_output=True, text=True)
            print(f"  最近 5 个 commit:")
            for line in r2.stdout.strip().split("\n"):
                if line:
                    print(f"    {line}")

            r3 = subprocess.run(["git", "branch"],
                                capture_output=True, text=True)
            print(f"  分支:")
            for line in r3.stdout.strip().split("\n"):
                if line:
                    print(f"    {line}")

            r4 = subprocess.run(["git", "worktree", "list"],
                                capture_output=True, text=True)
            print(f"  工作树:")
            for line in r4.stdout.strip().split("\n"):
                print(f"    {line}")
    except FileNotFoundError:
        print("  (未安装 git 或不在 PATH 中)")
        print("  模拟 git worktree:")
        print("    $ git worktree add /tmp/isolated feature-branch")
        print("    → 在 /tmp/isolated 创建独立工作副本")
        print("    → s18 的核心就是这个命令")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 2: DAG — 有向无环图
# ═══════════════════════════════════════════════════════════
def demo_2_dag():
    print("── Demo 2: DAG (Directed Acyclic Graph) ──")

    # 任务依赖图
    tasks = {
        "A": {"title": "设计 API", "blockedBy": []},
        "B": {"title": "实现模型", "blockedBy": ["A"]},
        "C": {"title": "写测试", "blockedBy": ["A"]},
        "D": {"title": "部署到生产", "blockedBy": ["B", "C"]},
    }

    print("  任务依赖图:")
    print("    A (设计) ──→ B (实现) ──→ D (部署)")
    print("         └──→ C (测试) ──┘")
    print()
    for tid, info in tasks.items():
        blocked = info["blockedBy"]
        if blocked:
            print(f"    {tid} ({info['title']}): 等待 {blocked} 完成")
        else:
            print(f"    {tid} ({info['title']}): 可以直接开始")

    # 拓扑排序
    print()
    print("  拓扑排序 (找出可行的执行顺序):")
    order = topological_sort(tasks)
    if order:
        print(f"    顺序: {' → '.join(order)}")
        for tid in order:
            info = tasks[tid]
            if info["blockedBy"]:
                print(f"      {tid}: {info['title']} (依赖 {info['blockedBy']} 已完成) ✓")
            else:
                print(f"      {tid}: {info['title']} (无依赖，率先开始) ✓")
    else:
        print("    检测到循环依赖！")

    # 检测环
    print()
    print("  环检测:")
    test_cycle = {"A": ["B"], "B": ["C"], "C": ["A"]}  # A→B→C→A
    print(f"    有效 DAG: {not has_cycle(tasks)}")
    print(f"    循环依赖: {not has_cycle(test_cycle)} ← 这会报错")
    print()


def topological_sort(tasks):
    """Kahn 算法：拓扑排序"""
    in_degree = {t: 0 for t in tasks}
    for t, info in tasks.items():
        for dep in info.get("blockedBy", []):
            if isinstance(dep, str):
                in_degree[t] += 1

    queue = deque([t for t, d in in_degree.items() if d == 0])
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)
        for t, info in tasks.items():
            if node in info.get("blockedBy", []):
                in_degree[t] -= 1
                if in_degree[t] == 0:
                    queue.append(t)

    return result if len(result) == len(tasks) else None


def has_cycle(tasks):
    """检测图中是否有环"""
    deps = {}
    for t in tasks:
        deps[t] = tasks[t] if isinstance(tasks[t], list) else tasks[t].get("blockedBy", [])

    visited = set()
    rec_stack = set()

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in deps.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        rec_stack.discard(node)
        return False

    for node in deps:
        if node not in visited:
            if dfs(node):
                return True
    return False


# ═══════════════════════════════════════════════════════════
# Demo 3: Cron 表达式
# ═══════════════════════════════════════════════════════════
def demo_3_cron():
    print("── Demo 3: Cron 表达式 ──")

    print("  Cron 格式: 分 时 日 月 星期")
    print("             ┬ ┬ ┬ ┬ ┬")
    print("             │ │ │ │ └─ 星期 (0-6, 0=周日)")
    print("             │ │ │ └─── 月 (1-12)")
    print("             │ │ └───── 日 (1-31)")
    print("             │ └─────── 时 (0-23)")
    print("             └───────── 分 (0-59)")
    print()

    examples = [
        ("0 9 * * 1", "每周一早上 9:00"),
        ("*/5 * * * *", "每 5 分钟"),
        ("0 0 1 * *", "每月 1 号 00:00"),
        ("30 14 * * 1-5", "工作日(周一~五) 14:30"),
        ("0 0 * * *", "每天 00:00"),
        ("0 */2 * * *", "每 2 小时"),
    ]

    print("  常见表达式:")
    for expr, meaning in examples:
        print(f"    {expr:20s} → {meaning}")

    print()
    print("  Python 解析 Cron:")
    try:
        from croniter import croniter
        from datetime import datetime

        cron = croniter("0 9 * * 1", datetime.now())
        print(f"    '0 9 * * 1' 接下来 3 次触发:")
        for i in range(3):
            print(f"      {cron.get_next(datetime)}")
    except ImportError:
        print("    (croniter 未安装。安装: pip install croniter)")
        print("    手动解析 '0 9 * * 1':")
        print("      分=0, 时=9, 日=*, 月=*, 星期=1")
        print("      → 每周一早上 9:00")
    print()


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("s00-09: Git、DAG、Cron — 工程基础设施")
    print("=" * 60)
    print()

    demo_1_git()
    demo_2_dag()
    demo_3_cron()

    print("─" * 60)
    print("小结:")
    print("  Git: commit=快照, branch=工作线, worktree=隔离副本")
    print("  DAG: 有向无环图，拓扑排序，s12 任务系统的核心")
    print("  Cron: 5字段表达式，s14 定时调度器的基础")
