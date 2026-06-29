#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s10: 精细操作 — stash、cherry-pick、reset

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - git stash 解决了什么问题？pop 和 apply 有什么区别？
  - cherry-pick 在时间树上做了什么？
  - reset --soft / --mixed / --hard 三种模式的区别是什么？
  - 怎么用时间树模型统一理解这三个操作？
═══════════════════════════════════════════════════════════════

启动方式:
    python s23_git/s10_fine_operations/code.py
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
    print(f"{Color.HEADER}  s10: 精细操作 — stash、cherry-pick、reset{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # Part A: git stash
    # ═══════════════════════════════════════════════════════════
    print(f"\n{Color.HIGHLIGHT}{'─' * 15} Part A: git stash {'─' * 15}{Color.RESET}\n")

    repo = create_demo_repo(name="fine-ops-demo")

    write_file(repo, "app.py", 'print("Hello")\n')
    commit(repo, "初始提交")

    print_step("A1", "场景：改了一半，突然要修 bug")

    # 模拟"改了一半"的状态
    write_file(repo, "app.py", 'print("Hello")\n\n# 正在开发的新功能（还没写完）\n')
    write_file(repo, "new_feature.py", "# 半成品...\n")

    show_status(repo, "工作区有一堆半成品改动")

    print_command("git stash", "把工作区和暂存区的改动暂存起来")
    run_git("stash", repo)

    show_status(repo, "stash 后 — 工作区干净了！可以自由切换分支")
    print_note("现在你可以放心地 git switch 到其他分支修 bug 了。")

    # 修完 bug 回来
    print_command("git stash pop", "恢复之前暂存的改动")
    result = run_git("stash pop", repo)
    print(f"  {Color.SUCCESS}{result.stdout.strip()}{Color.RESET}")

    show_status(repo, "stash pop 后 — 半成品改动回来了！")
    print_note("git stash pop = git stash apply + git stash drop（恢复并清理）")

    # ═══════════════════════════════════════════════════════════
    # Part B: git cherry-pick
    # ═══════════════════════════════════════════════════════════
    print(f"\n{Color.HIGHLIGHT}{'─' * 15} Part B: git cherry-pick {'─' * 15}{Color.RESET}\n")

    print_step("B1", "cherry-pick — 从别的分支「摘」一个 commit 过来")

    # 创建另一个分支，上面有个好用的 commit
    run_git("switch -c feature-utils", repo)
    write_file(repo, "utils.py", 'def add(a, b):\n    return a + b\n\ndef sub(a, b):\n    return a - b\n')
    commit(repo, "添加工具函数（add + sub）")

    # 拿到这个 commit 的 hash
    result = run_git("log --oneline -1", repo)
    cherry_hash = result.stdout.strip().split()[0]
    print_note(f"要摘取的 commit: {cherry_hash} — 添加工具函数（add + sub）")

    # 切回 main，cherry-pick
    run_git("switch master", repo)
    show_time_tree(repo, "cherry-pick 前 — main 上没有 utils.py")

    print_command(f"git cherry-pick {cherry_hash}", "把那个 commit 复制到 main 上")
    run_git(f"cherry-pick {cherry_hash}", repo)

    show_time_tree(repo, "cherry-pick 后 — utils.py 出现在 main 上了")
    print_note("注意：新 commit 的 hash 和原来的不同——但是内容一样。")

    # ═══════════════════════════════════════════════════════════
    # Part C: git reset
    # ═══════════════════════════════════════════════════════════
    print(f"\n{Color.HIGHLIGHT}{'─' * 15} Part C: git reset {'─' * 15}{Color.RESET}\n")

    print_step("C1", "reset --soft — 撤销 commit，保留 add")

    write_file(repo, "test.py", '# 测试文件\n')
    commit(repo, "添加测试文件")

    show_time_tree(repo, "reset 前 — 有一个 '添加测试文件' commit")

    print_command("git reset --soft HEAD~1", "撤销 commit，改动回到暂存区")
    run_git("reset --soft HEAD~1", repo)
    show_status(repo, "reset --soft 后 — test.py 在暂存区，等待重新 commit")

    print_step("C2", "reset --mixed (默认) — 撤销 commit 和 add")

    # 先重新 commit
    commit(repo, "添加测试文件（重新提交）")

    print_command("git reset HEAD~1", "撤销 commit 和 add，改动回到工作区")
    run_git("reset HEAD~1", repo)
    show_status(repo, "reset (--mixed) 后 — test.py 在工作区，连 add 都撤了")

    print_step("C3", "reset --hard ⚠️ — 全部丢弃")

    # 先重新 commit
    run_git("add test.py", repo)
    run_git('commit -m "添加测试文件（再次提交）"', repo)

    show_time_tree(repo, "reset --hard 前")

    print_command("git reset --hard HEAD~1", "⚠️ 完全回到上一个 commit，丢弃所有改动")
    run_git("reset --hard HEAD~1", repo)
    show_time_tree(repo, "reset --hard 后 — commit 消失了，文件也没了")

    print_key_point(
        "三种 reset 的区别:\n"
        "    --soft:  只移动分支指针（commit 撤销，add 保留）\n"
        "    --mixed: 移动分支指针 + 重置暂存区（commit 和 add 都撤销）\n"
        "    --hard:  移动分支指针 + 重置暂存区 + 重置工作区（全丢！）\n\n"
        "    在时间树上: 都是把当前分支标签移到另一个节点。\n"
        "    区别只是「移标签的时候，工作区和暂存区怎么处理」。"
    )

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 三个精细操作，一个统一理解！{Color.RESET}

   {Color.HIGHLIGHT}git stash{Color.RESET}                 →  暂存改动，清空工作区
   {Color.HIGHLIGHT}git stash pop{Color.RESET}             →  恢复最近的 stash
   {Color.HIGHLIGHT}git cherry-pick <hash>{Color.RESET}    →  从别的分支借一个 commit
   {Color.HIGHLIGHT}git reset --soft HEAD~1{Color.RESET}   →  撤销 commit，保留 add
   {Color.HIGHLIGHT}git reset HEAD~1{Color.RESET}          →  撤销 commit + add
   {Color.HIGHLIGHT}git reset --hard HEAD~1{Color.RESET}   →  全部丢弃 ⚠️

{Color.DIM}它们都是在时间树上移动指针——只是移动的方式和附带效果不同。{Color.RESET}
""")

    ask_keep(repo)


if __name__ == "__main__":
    main()
