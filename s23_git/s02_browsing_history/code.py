#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s02: 浏览历史 — 在时间树上自由跳转

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - git log 有哪些常用选项？--graph --all --oneline 各起什么作用？
  - git checkout / switch 做了什么？HEAD 是怎么移动的？
  - Detached HEAD 是什么状态？什么时候会出现？
  - 怎样不用 commit hash 就能回到"上一个 commit"？
═══════════════════════════════════════════════════════════════

启动方式:
    python s23_git/s02_browsing_history/code.py
"""

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from s23_git.utils import (
    Color, run_git, show_time_tree, show_status,
    print_step, print_command, print_note, print_key_point,
    create_demo_repo, write_file, commit, ask_keep,
)


def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s02: 浏览历史 — 在时间树上自由跳转{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: 先创建一棵有多个节点的树
    # ═══════════════════════════════════════════════════════════
    print_step(1, "准备 — 创建一棵有多个节点的树")

    repo = create_demo_repo(name="time-travel")

    # 创建多个 commit，构建一棵有 5 个节点的树
    write_file(repo, "story.txt", "# 时间旅行日记\n\n第 1 天: 项目启动。\n")
    commit(repo, "第 1 天: 项目启动")

    write_file(repo, "src/main.py", 'print("Hello, World!")\n')
    commit(repo, "第 2 天: 创建 main.py")

    write_file(repo, "src/utils.py", 'def add(a, b):\n    return a + b\n')
    commit(repo, "第 3 天: 添加工具函数")

    write_file(repo, "src/config.py", 'VERSION = "1.0.0"\n')
    commit(repo, "第 4 天: 添加配置文件")

    write_file(repo, "README.md", "# My Project\n\nA demo project.\n")
    commit(repo, "第 5 天: 添加 README")

    show_time_tree(repo, "当前时间树 — 5 个节点排成一条线")

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: git log 的各种用法
    # ═══════════════════════════════════════════════════════════
    print_step(2, "git log — 查看时间线的不同方式")

    print_command("git log --oneline", "最简洁的视图")
    result = run_git("log --oneline", repo)
    print(f"\n  {Color.TREE}{result.stdout.strip()}{Color.RESET}\n")

    print_command("git log --oneline -3", "只看最近 3 个")
    result = run_git("log --oneline -3", repo)
    print(f"\n  {Color.TREE}{result.stdout.strip()}{Color.RESET}\n")

    print_command("git log --stat", "看每个 commit 改了哪些文件")
    result = run_git("log --stat --max-count=2", repo)
    print(result.stdout[:600])

    print_note("--stat 显示每个 commit 的统计信息：哪些文件被改了、增删了多少行")

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: 时间旅行 — git checkout
    # ═══════════════════════════════════════════════════════════
    print_step(3, "时间旅行 — 用 git checkout 回到过去")

    print_command("git log --oneline", "先看看有哪些节点可以去")
    result = run_git("log --oneline", repo)
    hashes = result.stdout.strip().split("\n")
    print(f"\n  {Color.TREE}{result.stdout.strip()}{Color.RESET}\n")

    # 取出第 3 个 commit 的 hash（从最新往回数第 3 个）
    if len(hashes) >= 3:
        target_hash = hashes[2].split()[0]  # 第 3 个（0-indexed）
        target_msg = " ".join(hashes[2].split()[1:])
        print_command(f"git checkout {target_hash}", f"回到「{target_msg}」的瞬间")
        run_git(f"checkout {target_hash}", repo)

        # 此时查看时间树
        result = run_git("log --oneline --all --graph --decorate", repo)
        print(f"\n  {Color.TREE}{result.stdout.strip()}{Color.RESET}\n")

        print_key_point(
            "你注意到 HEAD 现在直接指向 commit 了吗？\n"
            "    HEAD 旁边没有 'main' 分支名 → 这就是 'detached HEAD'\n"
            "    你的工作区文件已经变成了「第 3 天」时的样子！"
        )

        # 展示 HEAD 的内容
        result = run_git("rev-parse HEAD", repo)
        print_note(f"当前 HEAD 指向: {result.stdout.strip()}")

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: 用相对引用跳转
    # ═══════════════════════════════════════════════════════════
    print_step(4, "相对引用 — 不需要记 hash 的跳转方式")

    # 先回到 main
    run_git("checkout master", repo)

    print_command("git checkout HEAD~1", "回到 '上一个' commit")
    run_git("checkout HEAD~1", repo)
    result = run_git("log --oneline -1", repo)
    print(f"  {Color.TREE}当前在: {result.stdout.strip()}{Color.RESET}")

    print_command("git checkout HEAD~2", "回到 '上上个' commit")
    run_git("checkout HEAD~2", repo)
    result = run_git("log --oneline -1", repo)
    print(f"  {Color.TREE}当前在: {result.stdout.strip()}{Color.RESET}")

    print_command("git checkout HEAD~4", "回到 '4 个 commit 之前'")
    run_git("checkout HEAD~4", repo)
    result = run_git("log --oneline -1", repo)
    print(f"  {Color.TREE}当前在: {result.stdout.strip()}{Color.RESET}")

    print_key_point(
        "HEAD~1 = 上一个 commit\n"
        "    HEAD~2 = 上上个 commit\n"
        "    HEAD~N = N 个 commit 之前\n"
        "    不需要记住长长的 hash 值！"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: Detached HEAD 体验
    # ═══════════════════════════════════════════════════════════
    print_step(5, "Detached HEAD — 直接站在 commit 上")

    # 先回到 main
    run_git("checkout master", repo)
    show_time_tree(repo, "回到 main 后 — HEAD → main → 最新节点")

    print_command("git checkout <hash>", "直接切换到某个 commit（不是分支）")
    first_hash = hashes[-1].split()[0]
    run_git(f"checkout {first_hash}", repo)
    show_time_tree(repo, "Detached HEAD — HEAD 直接指向 commit，不通过 branch")

    print_key_point(
        "Detached HEAD 的两个特征:\n"
        "    1. HEAD 旁边没有分支名（只有 'HEAD'）\n"
        "    2. Git 会提示: 'You are in detached HEAD state'\n\n"
        "    此时做 commit 不会更新任何分支——\n"
        "    如果切到别处，新 commit 就「丢失」了（实际还在 reflog 里）。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: 回到 main — 欢迎回来
    # ═══════════════════════════════════════════════════════════
    print_step(6, "回到 main — 安全归来")

    print_command("git checkout master", "回到 main 分支")
    run_git("checkout master", repo)
    show_time_tree(repo, "已安全回到 main 分支")

    print_note("如果忘记自己在 detached HEAD，运行 git status 会明确告诉你。")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 你学会了在时间树上自由移动！{Color.RESET}

   {Color.HIGHLIGHT}git log --graph --all --oneline{Color.RESET}  →  可视化时间树（最常用）
   {Color.HIGHLIGHT}git checkout <hash>{Color.RESET}            →  时间旅行到任意节点
   {Color.HIGHLIGHT}git checkout HEAD~N{Color.RESET}           →  用相对引用回到过去
   {Color.HIGHLIGHT}git switch main{Color.RESET}               →  回到主分支（安全）

{Color.DIM}记住: HEAD = 你在时间树上的「当前位置光标」{Color.RESET}
""")

    ask_keep(repo)


if __name__ == "__main__":
    main()
