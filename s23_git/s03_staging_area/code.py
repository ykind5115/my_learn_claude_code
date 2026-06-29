#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s03: 理解暂存区 — Git 最容易被误解的概念

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - 工作区、暂存区、仓库三者的区别是什么？
  - git status 的三种文件状态分别是什么意思？
  - git diff 和 git diff --staged 的区别是什么？
  - 为什么要有暂存区？它解决了什么问题？
═══════════════════════════════════════════════════════════════

启动方式:
    python s23_git/s03_staging_area/code.py
"""

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from s23_git.utils import (
    Color, run_git, show_time_tree, show_status,
    print_step, print_command, print_note, print_key_point,
    create_demo_repo, write_file, append_file, commit, ask_keep,
)


def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s03: 理解暂存区 — Git 最容易被误解的概念{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: 先创建一个有文件的仓库
    # ═══════════════════════════════════════════════════════════
    print_step(1, "准备 — 创建项目并做一次初始提交")

    repo = create_demo_repo(name="staging-demo")

    write_file(repo, "app.py", 'print("Hello, World!")\n')
    write_file(repo, "config.py", 'DEBUG = True\n')
    write_file(repo, "utils.py", 'def helper():\n    return 42\n')
    commit(repo, "初始提交：创建项目文件")
    show_time_tree(repo, "初始状态 — 1 个 commit，三个区域一致")

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: 修改文件 — 工作区变了，暂存区没变
    # ═══════════════════════════════════════════════════════════
    print_step(2, "修改文件 — 工作区和仓库产生差异")

    print_command("vim app.py", "在编辑器中修改了 app.py")
    append_file(repo, "app.py", 'print("Version 2.0")\n')
    print_command("vim config.py", "在编辑器中修改了 config.py")
    append_file(repo, "config.py", "PORT = 8000\n")
    print_command("touch new_feature.py", "创建了一个新文件（还在开发中）")
    write_file(repo, "new_feature.py", "# 还在开发中...\n")

    print_key_point(
        "此时：工作区有 3 个变化（2 修改 + 1 新文件）\n"
        "    暂存区：没变（和初始 commit 一致）\n"
        "    仓库：没变"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: git status — 诊断三个区域
    # ═══════════════════════════════════════════════════════════
    print_step(3, "git status — 读懂诊断报告")

    print_command("git status", "查看三个区域的关系")
    result = run_git("status", repo)
    print(result.stdout)

    print_key_point(
        "git status 告诉你三件事:\n"
        '    1. "Changes not staged" — 被跟踪的文件改了，但没 add\n'
        '    2. "Untracked files"    — 新文件，Git 从未跟踪过\n'
        '    3. 暂存区是空的          — 没有东西等着被提交'
    )

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: git diff — 看具体改了什么
    # ═══════════════════════════════════════════════════════════
    print_step(4, "git diff — 查看工作区 vs 暂存区的差异")

    print_command("git diff", "工作区 vs 暂存区：改了但还没 add 的部分")
    result = run_git("diff", repo)
    print(result.stdout[:800])

    print_note("以 '-' 开头的行 = 旧版本；以 '+' 开头的行 = 新版本")

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: 选择性 git add — 暂存区的核心价值
    # ═══════════════════════════════════════════════════════════
    print_step(5, "选择性 add — 暂存区的核心价值")

    print_command("git add app.py config.py", "只 add 修复 bug 的两个文件")
    run_git("add app.py config.py", repo)
    print_note("new_feature.py 没有 add——它还在开发中，不该进入这次提交")

    show_status(repo, "add 之后 — app.py 和 config.py 进入暂存区")

    print_command("git diff --staged", "暂存区 vs 仓库：看看下次会提交什么")
    result = run_git("diff --staged", repo)
    print(result.stdout[:600])

    print_command("git diff", "工作区 vs 暂存区：new_feature.py 还在外面")
    result = run_git("diff", repo)
    if result.stdout.strip():
        print(result.stdout[:400])
    else:
        print(f"  {Color.DIM}(已跟踪的文件没有差异——改动都在暂存区了){Color.RESET}")

    print_key_point(
        "这就是暂存区的核心价值：\n"
        "    你改了 3 个文件，但只把 2 个加入暂存区。\n"
        "    下次 commit 只包含这 2 个文件。\n"
        "    new_feature.py 继续待在工���区，不影响。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: commit — 只提交暂存区的内容
    # ═══════════════════════════════════════════════════════════
    print_step(6, "git commit — 只提交暂存区的内容")

    print_command('git commit -m "修复 bug: 更新 app.py 和 config.py"')
    commit(repo, "修复 bug: 更新 app.py 和 config.py")

    show_status(repo, "commit 之后 — new_feature.py 仍在工作区，未被提交")
    show_time_tree(repo, "时间树上新增一个节点")

    # ═══════════════════════════════════════════════════════════
    # 第 7 步: add 完又改 — 最常见的陷阱
    # ═══════════════════════════════════════════════════════════
    print_step(7, "陷阱演示 — add 完又改同一个文件")

    print_command('echo "新的改动" >> app.py', "add 完之后又改了 app.py")
    run_git("add app.py", repo)
    print_note("暂存区现在有 app.py 的「版本 A」")
    append_file(repo, "app.py", "# 这是 add 之后又加的改动\n")
    print_note("工作区现在是 app.py 的「版本 B」")

    show_status(repo, "同一个文件同时出现在两个区域！")

    print_key_point(
        "app.py 同时出现在 'staged' 和 'not staged':\n"
        "    - staged 里是 git add 时的版本\n"
        "    - not staged 里是 add 之后新增的改动\n"
        "    如果现在 commit，只会提交 staged 的版本！"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 8 步: git restore — 撤回操作
    # ═══════════════════════════════════════════════════════════
    print_step(8, "git restore — 从暂存区撤回")

    print_command("git restore --staged app.py", "把 app.py 从暂存区撤出")
    run_git("restore --staged app.py", repo)
    show_status(repo, "app.py 已从暂存区撤出，改动全在工作区")

    print_note("git restore --staged 不影响文件内容，只是从「准备提交」队列里移除")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 三个区域的关系现在清楚了吗？{Color.RESET}

   工作区（你的文件）
     │  git add         ↗
     ↓                  │  git restore --staged
   暂存区（准备拍照）
     │  git commit      ↗
     ↓                  │（已提交的不
   仓库（时间树）         │  能从暂存区撤回）

{Color.DIM}暂存区 = Git 给你的「后悔和选择」的空间{Color.RESET}
""")

    ask_keep(repo)


if __name__ == "__main__":
    main()
