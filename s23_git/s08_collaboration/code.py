#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s08: 协作工作流 — 团队开发的标准化流程

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - GitHub Flow 的 6 个步骤是什么？
  - Pull Request 的本质是什么？为什么要 Code Review？
  - 两个人同时开发，冲突了怎么处理？
  - 日常开发的一天应该怎么用 Git？
═══════════════════════════════════════════════════════════════

启动方式:
    python s23_git/s08_collaboration/code.py

注意: 本演示模拟多人协作场景，不需要 GitHub 账号。
"""

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from s23_git.utils import (
    Color, run_git, show_time_tree,
    print_step, print_command, print_note, print_key_point,
    create_demo_repo, write_file, append_file, commit,
)


def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s08: 协作工作流 — 团队开发的标准化流程{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    import tempfile, shutil
    base_dir = Path(tempfile.mkdtemp(prefix="s23git_flow_"))

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: 初始化远程仓库 + main 分支
    # ═══════════════════════════════════════════════════════════
    print_step(1, "初始化 — 创建远程仓库和 main 分支")

    remote_dir = base_dir / "central.git"
    remote_dir.mkdir()
    run_git("init --bare", remote_dir)

    # 张三创建初始项目
    zhangsan = base_dir / "zhangsan"
    run_git(f"clone {remote_dir} {zhangsan}", base_dir)
    write_file(zhangsan, "README.md", "# Team Project\n")
    write_file(zhangsan, ".gitignore", "__pycache__/\n*.pyc\n.env\n")
    commit(zhangsan, "初始化项目")
    run_git("push origin master", zhangsan)

    show_time_tree(zhangsan, "初始 main 分支")

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: 张三开发功能 — GitHub Flow 步骤 1~3
    # ═══════════════════════════════════════════════════════════
    print_step(2, "张三开发功能 — GitHub Flow 步骤 1~3")

    print(f"  {Color.HIGHLIGHT}步骤 1: 从 main 创建 feature 分支{Color.RESET}")
    run_git("switch -c feature-search", zhangsan)

    print(f"\n  {Color.HIGHLIGHT}步骤 2: 开发 + 小步 commit{Color.RESET}")
    write_file(zhangsan, "search.py", 'def search(query):\n    pass\n')
    commit(zhangsan, "搜索功能：创建基础框架")
    append_file(zhangsan, "search.py", '\ndef format_results(items):\n    return items\n')
    commit(zhangsan, "搜索功能：添加结果格式化")

    print(f"\n  {Color.HIGHLIGHT}步骤 3: push 到远程（备份 + 准备开 PR）{Color.RESET}")
    run_git("push -u origin feature-search", zhangsan)
    print_note("在真实场景中，接下来去 GitHub 页面点 'New Pull Request'")

    show_time_tree(zhangsan, "张三的 feature-search 已推到远程")

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: 李四 clone + 开发 — 模拟第二个人
    # ═══════════════════════════════════════════════════════════
    print_step(3, "李四 clone + 开发另一个功能")

    lisi = base_dir / "lisi"
    run_git(f"clone {remote_dir} {lisi}", base_dir)

    print(f"  {Color.HIGHLIGHT}步骤 1: 创建自己的 feature 分支{Color.RESET}")
    run_git("switch -c feature-login", lisi)

    print(f"  {Color.HIGHLIGHT}步骤 2~3: 开发 + push{Color.RESET}")
    write_file(lisi, "login.py", 'def login(u, p):\n    return True\n')
    commit(lisi, "登录功能：基础实现")
    run_git("push -u origin feature-login", lisi)

    show_time_tree(lisi, "李四的 feature-login 也推上去了")

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: 模拟 PR Review → Merge
    # ═══════════════════════════════════════════════════════════
    print_step(4, "模拟 PR Review → Merge")

    print_note("在真实 GitHub Flow 中，会有人在 PR 页面 Review 代码。")
    print_note("这里我们模拟「审查通过，合并到 main」")

    # 张三的 PR 先合并
    print(f"\n  {Color.HIGHLIGHT}张三的 PR 先合并到 main{Color.RESET}")
    run_git("switch master", zhangsan)
    run_git("fetch origin", zhangsan)
    run_git("merge origin/feature-search -m 'Merge PR: 搜索功能'", zhangsan)
    run_git("push origin master", zhangsan)
    print_note("张三的 feature-search 已合并到 main，feature-search 分支可以删了")

    show_time_tree(zhangsan, "张三合并后 — main 上有了搜索功能")

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: 李四面对冲突 — 后合并的人要处理
    # ═══════════════════════════════════════════════════════════
    print_step(5, "李四合并前先同步 main")

    print_note("张三的 PR 已经合并到 main 了。李四合并前要先同步。")

    print_command("git switch master && git pull", "李四：更新本地的 main")
    run_git("switch master", lisi)
    run_git("pull origin master", lisi)

    print_command("git switch feature-login", "切回自己的分支")
    run_git("switch feature-login", lisi)

    print_command("git merge master", "把最新 main 合并到 feature-login")
    result = run_git("merge master -m '同步 main 的更新'", lisi, check=False)

    show_time_tree(lisi, "李四同步后 — feature-login 基于最新的 main")

    print_key_point(
        "这是协作的关键步骤：在开 PR 或合并之前，\n"
        "    先把最新的 main 合并到自己的分支。\n"
        "    这样 PR 的 diff 只包含自己的改动，不会和 main 冲突。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: 清理 — 删除已合并的分支
    # ═══════════════════════════════════════════════════════════
    print_step(6, "清理已合并的分支")

    print_command("git branch -d feature-search", "张三：删除已合并的分支")
    run_git("branch -d feature-search", zhangsan)
    print_note("分支删了，但 commit 节点还在时间树上——历史完整保留。")

    show_time_tree(zhangsan, "删除 feature-search 分支后 — 历史完整")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 GitHub Flow 的 6 步你都体验了！{Color.RESET}

   1. 从 main 创建 feature 分支
   2. 开发 + 小步 commit
   3. push 到远程
   4. 创建 Pull Request
   5. Code Review + 讨论修改
   6. 合并到 main + 删除 feature 分支

{Color.DIM}Git 提供机制，工作流提供策略。好的工作流让团队有序协作。{Color.RESET}
""")

    # 清理
    try:
        shutil.rmtree(base_dir)
    except PermissionError:
        pass
    print(f"{Color.SUCCESS}✅ 演示环境已清理{Color.RESET}\n")


if __name__ == "__main__":
    main()
