#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s04: 分支 — 时间树的平行宇宙

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - 分支到底是什么？为什么创建分支这么快？
  - git switch -c 做了什么？HEAD 和 branch 的关系是什么？
  - 分支在时间树上是什么样子的？
  - 什么时候应该创建分支？
═══════════════════════════════════════════════════════════════

启动方式:
    python s23_git/s04_branches/code.py
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
    print(f"{Color.HEADER}  s04: 分支 — 时间树的平行宇宙{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: 先建立一条主线时间线
    # ═══════════════════════════════════════════════════════════
    print_step(1, "准备 — 在 main 上建立一条主线时间线")

    repo = create_demo_repo(name="branch-demo")

    write_file(repo, "app.py", 'print("v1.0")\n')
    commit(repo, "v1.0: 项目启动")

    write_file(repo, "index.html", "<h1>Welcome</h1>\n")
    commit(repo, "添加首页")

    write_file(repo, "style.css", "body { margin: 0; }\n")
    commit(repo, "添加样式文件")

    show_time_tree(repo, "当前时间树 — main 分支上的 3 个节点")

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: 创建分支 — 给 commit 贴一张新标签
    # ═══════════════════════════════════════════════════════════
    print_step(2, "创建分支 — 给当前节点贴一张新标签")

    print_command("git branch feature-login", "创建分支（但不切换）")
    run_git("branch feature-login", repo)
    print_note("feature-login 标签已创建，指向和 main 同一个节点")

    print_command("git branch", "查看所有分支")
    result = run_git("branch", repo)
    print(f"\n{Color.TREE}{result.stdout.strip()}{Color.RESET}\n")
    print_note("* 表示 HEAD 当前指向的分支（你现在站在哪个分支上）")

    show_time_tree(repo, "两个标签指向同一个节点 — 时间树外形没变")

    print_key_point(
        "创建分支只是创建了一个新指针，指向当前 commit。\n"
        "    没有复制任何文件，所以几乎是瞬间完成的。\n"
        "    这就是为什么 Git 的分支「极轻量」——只是一个 41 字节的文件。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: 切换到新分支并开发
    # ═══════════════════════════════════════════════════════════
    print_step(3, "在 feature-login 分支上开发")

    print_command("git switch feature-login", "切换到 feature-login 分支")
    run_git("switch feature-login", repo)

    # 在新分支上做 commit
    write_file(repo, "login.py", 'def login(user, pwd):\n    return True\n')
    commit(repo, "添加登录功能（第 1 步：基础代码）")

    write_file(repo, "login.html", '<form>...</form>\n')
    commit(repo, "添加登录页面")

    show_time_tree(repo, "feature-login 分支长出了新节点")

    print_key_point(
        "feature-login 标签随着 commit 自动前移了。\n"
        "    main 标签还在原处——两个分支已经「分叉」了。\n"
        "    这就是时间树的「平行宇宙」：两个分支各自生长。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: 切回 main — 一切如初
    # ═══════════════════════════════════════════════════════════
    print_step(4, "切回 main — 工作区瞬间恢复")

    print_command("git switch master", "切回 main 分支")
    run_git("switch master", repo)

    print_note("注意：工作区里的 login.py 和 login.html 消失了！")
    print_note("它们只存在于 feature-login 分支上，main 上没有。")

    show_status(repo, "main 分支上 — 没有 login 相关的文件")
    show_time_tree(repo, "HEAD 回到了 main，但 feature-login 的节点还在")

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: 在 main 上也做点事 — 真正的分叉
    # ═══════════════════════════════════════════════════════════
    print_step(5, "在 main 上开发 — 两条线同时生长")

    print_command("git switch -c hotfix-bug", "创建并切换到 hotfix 分支")
    run_git("switch -c hotfix-bug", repo)

    write_file(repo, "fix.txt", "修复了首页显示问题\n")
    commit(repo, "紧急修复：首页显示异常")

    show_time_tree(repo, "现在有 3 个分支：main, feature-login, hotfix-bug")

    print_key_point(
        "时间树上现在有三个分支标签：\n"
        "    - main: 指着最初的 commit\n"
        "    - feature-login: 指着登录功能的 commit\n"
        "    - hotfix-bug: 指着 bug 修复的 commit\n\n"
        "    三条线各自生长，互不干扰。这就是分支的力量。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: git switch -c — 创建+切换的一步到位
    # ═══════════════════════════════════════════════════════════
    print_step(6, "git switch -c — 最常用的分支命令")

    print_command("git switch -c experiment", "一步：创建 experiment 分支并切换过去")
    run_git("switch -c experiment", repo)
    write_file(repo, "experiment.md", "# 实验记录\n")
    commit(repo, "实验：尝试新算法")

    show_time_tree(repo, "第 4 个分支！时间树越来越茂盛了")

    print_note("git switch -c <name> = git branch <name> + git switch <name>")

    # ═══════════════════════════════════════════════════════════
    # 第 7 步: 删除分支
    # ═══════════════════════════════════════════════════════════
    print_step(7, "删除分支 — 撕掉便利贴")

    # 先切回 main（不能删除当前所在的分支）
    run_git("switch master", repo)

    print_command("git branch -d hotfix-bug", "删除 hotfix-bug 分支")
    run_git("branch -d hotfix-bug", repo)
    print_note("hotfix-bug 分支的标签被删除了，但 commit 节点还在！")

    show_time_tree(repo, "hotfix-bug 标签消失了，但节点还在时间树上")

    # 演示结束
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 你理解了分支的本质！{Color.RESET}

   {Color.HIGHLIGHT}git branch{Color.RESET}           →  查看所有分支
   {Color.HIGHLIGHT}git switch -c <name>{Color.RESET}  →  创建并切换分支（最常用）
   {Color.HIGHLIGHT}git switch <name>{Color.RESET}     →  切换分支
   {Color.HIGHLIGHT}git branch -d <name>{Color.RESET}  →  删除分支

{Color.DIM}记住: 分支只是一个指向 commit 的指针。轻量、快速、没有成本。{Color.RESET}
{Color.DIM}大胆创建分支吧！用完删掉就好。{Color.RESET}
""")

    ask_keep(repo)


if __name__ == "__main__":
    main()
