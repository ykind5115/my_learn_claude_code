#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s05: 合并 — 两条时间线汇合

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - Fast-forward merge 和 three-way merge 的区别是什么？
  - Merge commit 为什么有两个 parent？
  - 怎么用 git log --graph 看懂合并历史？
  - 合并后删除分支安全吗？节点还在吗？
═══════════════════════════════════════════════════════════════

启动方式:
    python s23_git/s05_merge/code.py
"""

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from s23_git.utils import (
    Color, run_git, show_time_tree,
    print_step, print_command, print_note, print_key_point,
    create_demo_repo, write_file, append_file, commit, ask_keep,
)


def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s05: 合并 — 两条时间线汇合{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: 准备 — 创建基础项目
    # ═══════════════════════════════════════════════════════════
    print_step(1, "准备 — 创建基础项目和 main 分支")

    repo = create_demo_repo(name="merge-demo")

    write_file(repo, "main.py", 'print("Hello")\n')
    commit(repo, "创建 main.py")

    write_file(repo, "utils.py", 'def add(a, b): return a + b\n')
    commit(repo, "添加工具函数")

    show_time_tree(repo, "初始的 main 分支 — 2 个节点")

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: Fast-forward merge
    # ═══════════════════════════════════════════════════════════
    print_step(2, "Fast-forward merge — 一条线在另一条线的前方")

    print_command("git switch -c feature-fast", "创建 feature-fast 分支")
    run_git("switch -c feature-fast", repo)

    # 在 feature-fast 上做 commit
    write_file(repo, "feature.py", "# 新功能的代码\n")
    commit(repo, "添加新功能模块")
    append_file(repo, "feature.py", "def new_func():\n    pass\n")
    commit(repo, "完善新功能")

    show_time_tree(repo, "合并前 — feature-fast 在 main 的前方")

    print_command("git switch master", "切回 main")
    run_git("switch master", repo)

    print_command("git merge feature-fast", "执行合并")
    result = run_git("merge feature-fast", repo)
    print(f"\n  {Color.SUCCESS}{result.stdout.strip()}{Color.RESET}")

    show_time_tree(repo, "Fast-forward 合并后 — main 直接移到 feature-fast 的位置")

    print_key_point(
        "Fast-forward merge 的特征:\n"
        "    - 没有产生新的 merge commit\n"
        "    - 只是把 main 标签移到了 feature-fast 的位置\n"
        "    - 时间线仍然是线性的，没有分叉的痕迹\n"
        "    - 条件：main 在分出 feature 后没有自己独有的 commit"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: Three-way merge
    # ═══════════════════════════════════════════════════════════
    print_step(3, "Three-way merge — 两条线各自有了新 commit")

    # 创建 feature-3way 分支（从当前 main 分出去）
    print_command("git switch -c feature-3way", "创建 feature-3way 分支")
    run_git("switch -c feature-3way", repo)

    write_file(repo, "login.py", 'def login():\n    return "ok"\n')
    commit(repo, "添加登录功能")
    append_file(repo, "login.py", 'def logout():\n    return "bye"\n')
    commit(repo, "添加登出功能")

    show_time_tree(repo, "feature-3way 上有了 2 个新 commit")

    # 切回 main，也在 main 上做 commit（制造真正的分叉）
    print_command("git switch master", "切回 main")
    run_git("switch master", repo)

    write_file(repo, "config.py", 'DEBUG = False\n')
    commit(repo, "添加配置文件")

    show_time_tree(repo, "合并前 — main 和 feature-3way 各自前进了")

    print_key_point(
        "现在两条线都各自有了新 commit：\n"
        "    - main 独有：'添加配置文件'\n"
        "    - feature-3way 独有：'添加登录功能' + '添加登出功能'\n"
        "    这种情况下 fast-forward 不可能了——需要 three-way merge。"
    )

    # 执行 three-way merge
    print_command("git merge feature-3way -m '合并登录功能到 main'")
    result = run_git('merge feature-3way -m "合并登录功能到 main"', repo)
    print(f"  {Color.SUCCESS}Merge successful!{Color.RESET}")

    show_time_tree(repo, "Three-way 合并后 — 出现了 merge commit")

    print_key_point(
        "Three-way merge 的特征:\n"
        "    - 产生了一个新的 merge commit（有两个 parent）\n"
        "    - 时间树清楚地显示了分支和合并的历史\n"
        "    - merge commit = 两条时间线的「汇合点」"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: 查看 merge commit 的细节
    # ═══════════════════════════════════════════════════════════
    print_step(4, "merge commit 的细节 — 两个 parent")

    print_command("git log --graph --oneline --all", "查看合并后的时间树")
    result = run_git("log --graph --oneline --all", repo)
    print(f"\n  {Color.TREE}{result.stdout.strip()}{Color.RESET}\n")

    print_command("git log -1 --format=fuller", "查看 merge commit 的详细信息")
    result = run_git("log -1 --format=fuller", repo)
    for line in result.stdout.strip().split("\n"):
        if "Merge" in line or "Parent" in line or "Author" in line or "commit" in line:
            print(f"  {Color.DIM}{line}{Color.RESET}")

    print_note("merge commit 的 Parent 字段有两个 hash——这就是「两个来源」的证据")

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: 合并后删除分支
    # ═══════════════════════════════════════════════════════════
    print_step(5, "合并后删除分支 — 节点还在")

    print_command("git branch -d feature-3way", "删除已合并的分支")
    run_git("branch -d feature-3way", repo)
    print_command("git branch -d feature-fast", "也删掉 feature-fast")
    run_git("branch -d feature-fast", repo)

    show_time_tree(repo, "分支标签删除了，但所有 commit 节点完好无损")

    print_note("看到吗？'feature-3way' 和 'feature-fast' 的标签没了，节点的提交信息还在。")
    print_note("合并后删除分支是标准操作——历史完整保留，只是标签清理了。")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 你掌握了两种合并方式！{Color.RESET}

   {Color.HIGHLIGHT}Fast-forward merge{Color.RESET}  →  一条线在前方，直接移动标签
   {Color.HIGHLIGHT}Three-way merge{Color.RESET}    →  两条线都前进了，创建 merge commit
   {Color.HIGHLIGHT}git merge <branch>{Color.RESET}  →  把指定分支合并到当前分支
   {Color.HIGHLIGHT}git branch -d{Color.RESET}       →  合并后安全删除分支

{Color.DIM}merge commit 有两个 parent——这就是「汇合」在时间树上的样子。{Color.RESET}
""")

    ask_keep(repo)


if __name__ == "__main__":
    main()
