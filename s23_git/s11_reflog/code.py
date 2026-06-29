#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s11: 时间旅行 — reflog：Git 的黑匣子

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - reflog 记录了什么？和 git log 有什么区别？
  - 怎样用 reflog 恢复「丢失」的 commit？
  - 怎样用 reflog 恢复误删的分支？
  - HEAD@{1} 和 HEAD@{10.minutes.ago} 是什么意思？
═══════════════════════════════════════════════════════════════

启动方式:
    python s23_git/s11_reflog/code.py
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
    print(f"{Color.HEADER}  s11: 时间旅行 — reflog：Git 的黑匣子{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    repo = create_demo_repo(name="reflog-demo")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: 创建一些 commit，丰富历史
    # ═══════════════════════════════════════════════════════════
    print_step(1, "准备 — 创建一些 commit 作为「可丢失的」历史")

    write_file(repo, "important.txt", "非常重要的数据\n")
    commit(repo, "V1: 重要数据 v1")

    write_file(repo, "important.txt", "非常重要的数据 v2\n")
    commit(repo, "V2: 重要数据 v2")

    write_file(repo, "important.txt", "非常重要的数据 v3！（这个 commit 马上会被删掉）\n")
    commit(repo, "V3: 重要数据 v3 ★★★ 记住这个")

    show_time_tree(repo, "初始状态 — 3 个 commit")

    # 记录 V3 commit 的简短 hash（后面恢复用）
    result = run_git("log --oneline -1", repo)
    v3_hash = result.stdout.strip().split()[0]

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: git reflog — 查看操作日记
    # ═══════════════════════════════════════════════════════════
    print_step(2, "git reflog — 查看 HEAD 的移动轨迹")

    print_command("git reflog", "查看操作历史")
    result = run_git("reflog", repo)
    print(f"\n  {Color.TREE}{result.stdout.strip()}{Color.RESET}\n")

    print_note("每一条记录 = HEAD 的一次移动")
    print_note("HEAD@{0} 是最新的，数字越大越久远")

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: 模拟灾难 — git reset --hard
    # ═══════════════════════════════════════════════════════════
    print_step(3, "模拟灾难 — git reset --hard 删掉了重要 commit")

    print_command("git reset --hard HEAD~2", "⚠️ 回到 2 个 commit 之前")
    run_git("reset --hard HEAD~2", repo)

    show_time_tree(repo, "reset --hard 后 — V2 和 V3 不见了！")

    print(f"\n  {Color.ERROR}V3 commit ({v3_hash}) 从时间树上消失了！{Color.RESET}")
    print(f"  {Color.ERROR}important.txt 的内容回到了 v1 版本。{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: 用 reflog 救援！
    # ═══════════════════════════════════════════════════════════
    print_step(4, "用 reflog 救援 — 找回「丢失」的 commit")

    print_command("git reflog", "reflog 还记着 V3 commit 在哪！")
    result = run_git("reflog", repo)
    print(f"\n  {Color.TREE}{result.stdout.strip()}{Color.RESET}\n")

    # 找到 reset 之前的 HEAD (HEAD@{1})
    print_command("git reflog -1 HEAD@{1}", "reset 之前的 HEAD 在哪？")
    result = run_git("reflog -1 HEAD@{1}", repo)
    print(f"  {Color.TREE}{result.stdout.strip()}{Color.RESET}")

    print_key_point(
        "即使 git log 看不到了，reflog 还记得！\n"
        "    HEAD@{1} 就是 reset 之前 HEAD 所在的位置——\n"
        "    那个位置还有 V3 commit 的完整数据。"
    )

    # 恢复！
    print_command("git reset --hard HEAD@{1}", "回到 reset 之前的状��")
    run_git("reset --hard HEAD@{1}", repo)

    show_time_tree(repo, "恢复后 — V2 和 V3 都回来了！")

    print(f"  {Color.SUCCESS}🎉 V3 commit ({v3_hash}) 又回来了！important.txt 也恢复了！{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: 模拟误删分支 + 恢复
    # ═══════════════════════════════════════════════════════════
    print_step(5, "误删分支 + 用 reflog 恢复")

    # 创建一个分支并做 commit
    run_git("switch -c precious-branch", repo)
    write_file(repo, "precious.py", "# 珍贵的代码\n")
    commit(repo, "珍贵的代码 — 在这条分支上")

    # 记录 commit hash
    result = run_git("log --oneline -1", repo)
    precious_hash = result.stdout.strip().split()[0]

    # 切回 main
    run_git("switch master", repo)

    # 删除分支！
    print_command("git branch -D precious-branch", "⚠️ 删除分支")
    run_git("branch -D precious-branch", repo)

    show_time_tree(repo, "删除分支后 — precious-branch 不见了")

    # 用 reflog 找回
    print_command("git reflog --date=iso", "查看 reflog（带时间戳）")
    result = run_git("reflog --date=iso -5", repo)
    print(f"\n  {Color.TREE}{result.stdout.strip()}{Color.RESET}\n")

    print_command(f"git branch precious-branch {precious_hash}", "用 reflog 找到的 hash 恢复分支")
    run_git(f"branch precious-branch {precious_hash}", repo)

    show_time_tree(repo, "分支恢复了！precious-branch 回来了！")

    print_key_point(
        "删除分支只是删了标签（ref 文件）。\n"
        "    commit 节点还在 .git/objects/ 里。\n"
        "    reflog 记录了这个 hash → 你可以恢复。\n"
        "    （前提：在 Git 垃圾回收之前，默认 90 天）"
    )

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 你掌握了 Git 的时间旅行！{Color.RESET}

   {Color.HIGHLIGHT}git reflog{Color.RESET}                     →  查看 HEAD 的所有移动记录
   {Color.HIGHLIGHT}git reset --hard HEAD@{{N}}{Color.RESET}     →  回到 N 步前的状态
   {Color.HIGHLIGHT}git branch <name> <hash>{Color.RESET}      →  用 hash 恢复删除的分支
   {Color.HIGHLIGHT}HEAD@{{10.minutes.ago}}{Color.RESET}         →  时间引用

{Color.DIM}记住: 在 Git 里，没有什么是真正丢失的。reflog 就是你的后悔药。{Color.RESET}
{Color.DIM}(只要改动 commit 过，就能找回。没 commit 的改动 reflog 救不了——记得常 commit！){Color.RESET}
""")

    ask_keep(repo)


if __name__ == "__main__":
    main()
