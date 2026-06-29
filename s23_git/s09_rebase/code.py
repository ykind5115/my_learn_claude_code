#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s09: rebase — 把树枝「嫁接」到别处

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - rebase 和 merge 的本质区别是什么？
  - rebase 在时间树上做了什么操作？
  - git rebase -i 能做什么？squash / fixup / reword 各是什么？
  - 什么是 rebase 的黄金法则？为什么不能 rebase 公共分支？
═══════════════════════════════════════════════════════════════

启动方式:
    python s23_git/s09_rebase/code.py
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
    print(f"{Color.HEADER}  s09: rebase — 把树枝「嫁接」到别处{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: 准备 — 创建分叉的时间树
    # ═══════════════════════════════════════════════════════════
    print_step(1, "准备 — 创建分叉的时间树（merge 和 rebase 的对比起跑线）")

    repo = create_demo_repo(name="rebase-demo")

    write_file(repo, "main.py", 'print("v1.0")\n')
    commit(repo, "main: 初始版本")

    write_file(repo, "utils.py", 'def helper():\n    pass\n')
    commit(repo, "main: 添加工具函数")

    # 创建 feature 分支并开发
    run_git("switch -c feature-rebase", repo)
    write_file(repo, "feature.py", '# 新功能（第 1 步）\n')
    commit(repo, "feature: 新功能第 1 步")
    write_file(repo, "feature.py", '# 新功能（第 1 步）\n\ndef do_stuff():\n    pass\n')
    commit(repo, "feature: 新功能第 2 步")
    write_file(repo, "feature.py", '# 新功能（第 1 步）\n\ndef do_stuff():\n    pass\n\ndef more_stuff():\n    pass\n')
    commit(repo, "feature: 新功能完成")

    # 切回 main，也在 main 上做 commit
    run_git("switch master", repo)
    write_file(repo, "config.py", 'DEBUG = False\n')
    commit(repo, "main: 添加配置文件")
    write_file(repo, "README.md", "# Project\n")
    commit(repo, "main: 添加 README")

    show_time_tree(repo, "分叉的时间树 — feature 和 main 各自前进了")

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: rebase — 把 feature 嫁接到 main 的最新节点
    # ═══════════════════════════════════════════════════════════
    print_step(2, "rebase — 把 feature 的底座搬到 main 最新节点")

    print_command("git switch feature-rebase", "切换到 feature 分支")
    run_git("switch feature-rebase", repo)

    print_command("git rebase master", "把 feature 嫁接到 main 上")
    result = run_git("rebase master", repo, check=False)
    print(f"\n  {Color.SUCCESS}{result.stdout.strip()}{Color.RESET}")
    if result.stderr.strip():
        print(f"  {Color.DIM}{result.stderr.strip()}{Color.RESET}")

    show_time_tree(repo, "rebase 后 — 时间线变直了！")

    print_key_point(
        "rebase 做了什么:\n"
        "    1. 找到 feature 和 main 的共同祖先\n"
        "    2. 把 feature 的 3 个 commit 「暂存」\n"
        "    3. 把 feature 的底座从原位置搬到 main 最新节点\n"
        "    4. 把 3 个 commit 逐个应用到新底座上\n\n"
        "    结果是线性历史——看不出 feature 是从哪分出来的。\n"
        "    原来的 3 个 commit 还在 .git 里（reflog 能找到），但 hash 变了。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: 对比 — merge 会是什么样？
    # ═══════════════════════════════════════════════════════════
    print_step(3, "对比 — 如果用的是 merge，时间树会是什么样？")

    # 创建另一个 feature 分支用 merge 来对比
    run_git("switch master", repo)
    run_git("switch -c feature-merge-demo", repo)
    write_file(repo, "merge_demo.py", "# merge 演示\n")
    commit(repo, "merge-demo: 第 1 步")
    write_file(repo, "merge_demo.py", "# merge 演示\n\ndef test():\n    pass\n")
    commit(repo, "merge-demo: 第 2 步")

    run_git("switch master", repo)
    write_file(repo, "readme_update.md", "# 更新说明\n")
    commit(repo, "main: 更新说明")

    run_git("switch feature-merge-demo", repo)
    result = run_git("merge master -m 'Merge main into feature-merge-demo'", repo, check=False)

    show_time_tree(repo, "merge 方式 — 保留了分叉的痕迹")

    print_key_point(
        "对比 rebase 和 merge 的时间树:\n"
        "    - feature-rebase: 一条直线，嫁接后看不出分叉\n"
        "    - feature-merge-demo: 保留了分叉 + merge commit\n\n"
        "    选哪个？取决于你想要什么样的历史。\n"
        "    个人分支推荐 rebase（干净），公共分支推荐 merge（保留痕迹）。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: 交互式 rebase 简介
    # ═══════════════════════════════════════════════════════════
    print_step(4, "交互式 rebase — 整理凌乱的 commit")

    # 创建一个有凌乱 commit 的分支
    run_git("switch master", repo)
    run_git("switch -c messy-feature", repo)

    write_file(repo, "messy.py", "# step 1\n")
    commit(repo, "WIP: 开始写")
    append_file(repo, "messy.py", "# step 2\n")
    commit(repo, "继续写")
    append_file(repo, "messy.py", "# step 3\n")
    commit(repo, "修了个 typo")
    append_file(repo, "messy.py", "# step 4\n")
    commit(repo, "完成了！")

    show_time_tree(repo, "凌乱的历史 — 4 个不专业的 commit")

    print_note("这些 'WIP' '修了个typo' '继续写' 的 commit 对 reviewer 很不友好。")
    print_note("交互式 rebase 可以把它们整理成 1 个干净的 commit。")

    print_command("git rebase -i HEAD~4", "交互式整理最近 4 个 commit")
    print(f"\n  {Color.DIM}编辑器会打开，显示:{Color.RESET}")
    print(f"  {Color.DIM}  pick xxx WIP: 开始写{Color.RESET}")
    print(f"  {Color.DIM}  squash xxx 继续写{Color.RESET}")
    print(f"  {Color.DIM}  squash xxx 修了个 typo{Color.RESET}")
    print(f"  {Color.DIM}  squash xxx 完成了！{Color.RESET}")
    print(f"\n  {Color.DIM}把后 3 个 pick 改成 squash → 4 合 1 → 干净的提交{Color.RESET}")

    print_note("由于 git rebase -i 需要交互式编辑器，本演示不能自动运行。请在自己的仓库里试试！")

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: 黄金法则
    # ═══════════════════════════════════════════════════════════
    print_step(5, "rebase 的黄金法则")

    print(f"""
  {Color.WARNING}⚠️  黄金法则: 不要 rebase 已经 push 到公共仓库的分支！{Color.RESET}

  {Color.DIM}为什么？{Color.RESET}
  {Color.DIM}  rebase 会生成新的 commit（新 hash），和远程的旧 commit 冲突。{Color.RESET}
  {Color.DIM}  队友 pull 时会看到「分叉历史」，不知所措。{Color.RESET}

  {Color.SUCCESS}✅ 安全用法:{Color.RESET}
  {Color.DIM}  - rebase 自己独用的 feature 分支{Color.RESET}
  {Color.DIM}  - rebase 还没 push 的本地 commit{Color.RESET}
  {Color.DIM}  - git pull --rebase（等同于 fetch + rebase）{Color.RESET}

  {Color.ERROR}❌ 危险用法:{Color.RESET}
  {Color.DIM}  - rebase main / master 分支{Color.RESET}
  {Color.DIM}  - rebase 队友也在用的分支{Color.RESET}
  {Color.DIM}  - rebase 后 git push --force{Color.RESET}
""")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 你理解了 rebase —— 时间树的「嫁接」操作！{Color.RESET}

   {Color.HIGHLIGHT}git rebase <target>{Color.RESET}     →  把当前分支嫁接到 target 上
   {Color.HIGHLIGHT}git rebase -i HEAD~N{Color.RESET}   →  交互式整理最近 N 个 commit
   {Color.HIGHLIGHT}squash / fixup{Color.RESET}          →  合并凌乱的 commit
   {Color.HIGHLIGHT}git rebase --abort{Color.RESET}     →  取消 rebase
   {Color.HIGHLIGHT}git pull --rebase{Color.RESET}      →  pull 时用 rebase 代替 merge

{Color.DIM}记住黄金法则: 不要 rebase 已 push 的公共分支。{Color.RESET}
""")

    ask_keep(repo)


if __name__ == "__main__":
    main()
