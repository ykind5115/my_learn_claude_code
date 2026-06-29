#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s06: 合并冲突 — 当两段历史「打架」了

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - 冲突是怎么产生的？为什么 Git 不自动解决？
  - 冲突标记 <<<<<<< / ======= / >>>>>>> 怎么看？
  - 解决冲突的标准三步是什么？
  - 如何取消一次合并（git merge --abort）？
═══════════════════════════════════════════════════════════════

启动方式:
    python s23_git/s06_conflicts/code.py
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
    print(f"{Color.HEADER}  s06: 合并冲突 — 当两段历史「打架」了{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: 建立共同祖先
    # ═══════════════════════════════════════════════════════════
    print_step(1, "准备 — 创建两条会冲突的分支")

    repo = create_demo_repo(name="conflict-demo")

    write_file(repo, "app.py", (
        '"""Application config"""\n\n'
        'DEBUG = False\n'
        'VERSION = "1.0.0"\n'
    ))
    commit(repo, "创建 app.py（共同祖先）")

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: 在 main 上修改 app.py
    # ═══════════════════════════════════════════════════════════
    print_step(2, "在 main 分支上修改 app.py")

    write_file(repo, "app.py", (
        '"""Application config - MAIN VERSION"""\n\n'
        'DEBUG = True\n'                  # ← 改了这一行
        'VERSION = "1.0.0"\n'
        'AUTHOR = "zhangsan"\n'           # ← 加了这一行
    ))
    commit(repo, "main: 打开 DEBUG，添加作者信息")

    show_time_tree(repo, "main 分支的状态")

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: 创建 feature 分支，也改同一行
    # ═══════════════════════════════════════════════════════════
    print_step(3, "创建 feature 分支，也改 app.py 的同一行")

    # 回到共同祖先，创建 feature 分支
    # 先找到共同祖先的 hash
    result = run_git("log --oneline -2", repo)
    ancestor_hash = result.stdout.strip().split("\n")[-1].split()[0]

    run_git(f"switch -c feature-conflict {ancestor_hash}", repo)

    write_file(repo, "app.py", (
        '"""Application config - FEATURE VERSION"""\n\n'
        'DEBUG = "verbose"\n'             # ← 也改了同一行！
        'VERSION = "1.0.0"\n'
        'PORT = 8000\n'                   # ← 加了不同的一行
    ))
    commit(repo, "feature: 修改 DEBUG 为 verbose，添加 PORT")

    show_time_tree(repo, "合并前 — main 和 feature 各自改了 app.py")

    print_key_point(
        "注意看: main 把 DEBUG 改成了 True\n"
        "        feature 把 DEBUG 改成了 'verbose'\n"
        "        这两个分支改了「同一个文件的同一行」——这就是冲突的根源。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: 触发冲突！
    # ═══════════════════════════════════════════════════════════
    print_step(4, "合并！触发冲突")

    run_git("switch master", repo)

    print_command("git merge feature-conflict", "尝试合并——将会冲突！")
    result = run_git("merge feature-conflict", repo, check=False)

    if result.returncode != 0:
        print(f"\n  {Color.WARNING}⚡ 发生冲突了！Git 无法自动合并。{Color.RESET}")
        print(f"  {Color.DIM}{result.stderr.strip()}{Color.RESET}")

    show_status(repo, "冲突状态 — app.py 标记为 'both modified'")

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: 查看冲突标记
    # ═══════════════════════════════════════════════════════════
    print_step(5, "查看冲突标记 — 读懂 Git 在说什么")

    print_command("cat app.py", "查看冲突文件的内容")
    print(f"\n  {Color.WARNING}── 冲突文件内容 ──{Color.RESET}")

    app_content = (repo / "app.py").read_text(encoding="utf-8")
    for line in app_content.split("\n"):
        if line.startswith("<<<<<<<"):
            print(f"  {Color.RED}{line}{Color.RESET}")
        elif line.startswith("======="):
            print(f"  {Color.YELLOW}{line}{Color.RESET}")
        elif line.startswith(">>>>>>>"):
            print(f"  {Color.RED}{line}{Color.RESET}")
        else:
            print(f"  {Color.DIM}{line}{Color.RESET}")

    print(f"\n  {Color.WARNING}── 解读 ──{Color.RESET}")
    print(f"  {Color.DIM}<<<<<<< HEAD  = main 分支的版本（当前分支）{Color.RESET}")
    print(f"  {Color.DIM}=======       = 分隔线{Color.RESET}")
    print(f"  {Color.DIM}>>>>>>> xxx  = feature 分支的版本（被合并的分支）{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: 解决冲突
    # ═══════════════════════════════════════════════════════════
    print_step(6, "解决冲突 — 三步法")

    print(f"  {Color.HIGHLIGHT}第 1 步: 打开文件 app.py{Color.RESET}")
    print(f"  {Color.HIGHLIGHT}第 2 步: 决定保留哪边，删除冲突标记{Color.RESET}")
    print_note("这里我们选择保留 main 的 DEBUG = True，但加上 feature 的 PORT = 8000")

    # 手动解决冲突
    resolved_content = (
        '"""Application config - MERGED VERSION"""\n\n'
        'DEBUG = True\n'                    # 保留 main 的
        'VERSION = "1.0.0"\n'
        'AUTHOR = "zhangsan"\n'             # 保留 main 的
        'PORT = 8000\n'                     # 采纳 feature 的
    )
    write_file(repo, "app.py", resolved_content)

    print(f"\n  {Color.HIGHLIGHT}第 3 步: git add + git commit{Color.RESET}")
    print_command("git add app.py", "告诉 Git：冲突已解决")
    run_git("add app.py", repo)
    show_status(repo, "冲突已标记为解决")

    print_command('git commit -m "合并 feature-conflict，解决冲突"')
    run_git('commit -m "合并 feature-conflict，解决冲突"', repo, check=False)

    show_time_tree(repo, "冲突解决后 — merge commit 出现在时间树上")

    print_key_point(
        "冲突解决的完整流程:\n"
        "    ① git status → 找到冲突文件\n"
        '    ② 打开文件 → 删除 <<<<<<< / ======= / >>>>>>> → 保留想要的代码\n'
        "    ③ git add <文件> → git commit"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 7 步: 演示 git merge --abort
    # ═══════════════════════════════════════════════════════════
    print_step(7, "git merge --abort — 后悔药")

    # 再创建一个冲突场景来演示 --abort
    run_git("switch -c feature-abort-demo", repo)
    write_file(repo, "config.txt", "main version\n")
    commit(repo, "添加 config.txt")

    run_git("switch master", repo)
    write_file(repo, "config.txt", "feature version\n")
    commit(repo, "添加 config.txt（main 版本）")

    print_command("git merge feature-abort-demo", "尝试合并")
    result = run_git("merge feature-abort-demo", repo, check=False)
    print(f"  {Color.WARNING}⚡ 冲突！{Color.RESET}")

    print_command("git merge --abort", "取消合并，回到合并前的状态")
    run_git("merge --abort", repo)

    show_status(repo, "--abort 之后 — 工作区干净，像什么都没发生过")
    print_note("git merge --abort = 完整回退到合并之前的状态。安心合并，错了就 abort。")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 冲突不再是可怕的事了！{Color.RESET}

   {Color.HIGHLIGHT}冲突的本质{Color.RESET}      →  两个分支改了同一行
   {Color.HIGHLIGHT}冲突标记{Color.RESET}        →  <<<<<<< / ======= / >>>>>>>
   {Color.HIGHLIGHT}解决三步{Color.RESET}        →  打开文件 → 选择 → git add → git commit
   {Color.HIGHLIGHT}git merge --abort{Color.RESET} →  后悔药，回到合并前

{Color.DIM}冲突不可怕。不理解冲突标记才可怕。现在你已经会读了。{Color.RESET}
""")

    ask_keep(repo)


if __name__ == "__main__":
    main()
