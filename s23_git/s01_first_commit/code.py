#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s01: 第一次提交 — 种下时间树的第一个节点

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - git init 做了什么？.git 目录是什么？
  - git add 和 git commit 的区别是什么？
  - commit 节点里包含了什么信息？
  - 时间树是怎么一步步长出来的？
═══════════════════════════════════════════════════════════════

启动方式:
    python s23_git/s01_first_commit/code.py
"""

import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中，以便导入 utils
_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from s23_git.utils import (
    Color,
    run_git,
    show_time_tree,
    show_status,
    print_step,
    print_command,
    print_note,
    print_key_point,
    create_demo_repo,
    write_file,
    append_file,
    commit,
    ask_keep,
)


def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s01: 第一次提交 — 种下时间树的第一个节点{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: git init — 创建一棵空的时间树
    # ═══════════════════════════════════════════════════════════
    print_step(1, "git init — 创建一棵空的时间树")

    repo = create_demo_repo(name="learn-git")

    print_command("git init", "在项目文件夹中创建 .git/ 目录")
    print(f"  {Color.SUCCESS}✅ 空的时间树已创建{Color.RESET}")
    print(f"  {Color.DIM}仓库位置: {repo}{Color.RESET}")
    print_note(".git/ 目录 = 整棵时间树。所有历史、分支、快照都存在这里。")

    show_time_tree(repo, "初始状态 — 空的时间树")

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: git config — 给树签名
    # ═══════════════════════════════════════════════════════════
    print_step(2, "git config — 告诉 Git 你是谁")

    print_command('git config user.name "s23-demo"')
    print_command('git config user.email "demo@s23-git.local"')
    print_note("每个 commit 节点都会记录作者信息。")
    print_note("(本演示中 utils.py 已自动完成 config，这里展示的是命令本身)")

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: 创建文件 — 工作区有了内容
    # ═══════════════════════════════════════════════════════════
    print_step(3, "创建文件 — 工作区有了内容")

    write_file(repo, "README.md", "# 我的项目\n\n这是我的第一个 Git 仓库。\n")
    print_command('echo "# 我的项目" > README.md', "在编辑器中创建了一个文件")

    show_status(repo, "文件在工作区，尚未被 Git 跟踪")

    print_key_point(
        "此时 README.md 只是「工作区里的一个普通文件」。\n"
        "    Git 看到了它，但还没有把它纳入版本控制。\n"
        "    用 git status 可以查看哪些文件是「未跟踪」(Untracked) 的。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: git add — 把文件加入暂存区
    # ═══════════════════════════════════════════════════════════
    print_step(4, "git add — 把文件从工作区复制到暂存区")

    run_git("add README.md", repo)
    print_command("git add README.md", "告诉 Git：'这个文件要放进下一次快照'")

    show_status(repo, "文件已进入暂存区 (Staged)")

    print_key_point(
        "暂存区 = 你选择的「下一张快照要包含的文件列表」。\n"
        "    此时还没有创建 commit 节点，时间树仍然是空的。\n"
        '    暂存区只是「准备好了」，等 git commit 按下快门。'
    )

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: git commit — 种下第一个节点！
    # ═══════════════════════════════════════════════════════════
    print_step(5, "git commit — 种下时间树的第一个节点！")

    print_command('git commit -m "第一次提交：创建 README"')
    result = run_git('commit -m "第一次提交：创建 README"', repo)

    # 打印 commit 的完整信息
    print(f"\n  {Color.SUCCESS}🌱 第一个节点已种下！{Color.RESET}")
    show_time_tree(repo, "第一次提交后 — 树上有了第一个节点")

    print_key_point(
        "git commit 做了 5 件事:\n"
        "    ① 给暂存区所有文件拍快照\n"
        "    ② 创建 commit 节点 (内容 + 作者 + 时间 + 信息 + parent)\n"
        "    ③ 把节点存入 .git/objects/\n"
        "    ④ 把 HEAD 和 main 标签指向这个节点\n"
        "    ⑤ 清空暂存区"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: 再做两次提交 — 观察时间树生长
    # ═══════════════════════════════════════════════════════════
    print_step(6, "再做两次提交 — 观察时间树如何生长")

    # 第二次提交
    print_command('echo "版本: 1.0.0" >> README.md', "修改文件")
    append_file(repo, "README.md", "\n版本: 1.0.0\n")
    print_command("git add README.md")
    print_command('git commit -m "添加版本号"')
    commit(repo, "添加版本号", "README.md")
    show_time_tree(repo, "第二次提交后 — 两个节点连成一条线")

    # 第三次提交
    print_command('echo "作者: zhangsan" >> README.md', "再次修改")
    append_file(repo, "README.md", "作者: zhangsan\n")
    commit(repo, "添加作者信息", "README.md")
    show_time_tree(repo, "第三次提交后 — 三个节点，时间线在生长")

    print_key_point(
        "观察时间树的变化:\n"
        "    - 每提交一次，树上就多一个节点\n"
        "    - 新节点总是指向前一个节点 (parent)\n"
        "    - main 标签和 HEAD 始终指向最新的节点\n"
        "    - 这形成了一条「链」—— Git 的提交历史"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 7 步: git log — 查看完整历史
    # ═══════════════════════════════════════════════════════════
    print_step(7, "git log — 查看时间线的完整记录")

    print_command("git log", "查看每个 commit 的详细信息")
    result = run_git("log", repo)
    print(result.stdout)

    print_command("git log --oneline", "简洁模式：一行一个 commit")
    result = run_git("log --oneline", repo)
    print(f"\n  {Color.TREE}{result.stdout.strip()}{Color.RESET}\n")

    print_note("--oneline 只显示 commit hash 的前 7 位 + 提交信息")
    print_note("这在后面章节会经常用到。")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 恭喜！你已经理解了 Git 最核心的三步:{Color.RESET}

   {Color.HIGHLIGHT}git init{Color.RESET}    →  创建一棵空的时间树
   {Color.HIGHLIGHT}git add{Color.RESET}     →  选择哪些文件进入下一次快照
   {Color.HIGHLIGHT}git commit{Color.RESET}  →  种下节点，生长时间树

{Color.DIM}这三个命令你会用几千次——它们就是 Git 的「呼吸」。{Color.RESET}
""")

    ask_keep(repo)


if __name__ == "__main__":
    main()
