#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s12: 深入 .git — Git 的内部原理

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - .git/ 目录里有什么？objects/、refs/、HEAD 各存了什么？
  - Git 的四种对象（blob/tree/commit/ref）分别是什么？
  - 为什么 Git 这么快？为什么 Git 这么可靠？
  - 用 git cat-file -p 偷看 Git 对象能发现什么？
═══════════════════════════════════════════════════════════════

启动方式:
    python s23_git/s12_internals/code.py
"""

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from s23_git.utils import (
    Color, run_git, show_time_tree,
    print_step, print_command, print_note, print_key_point,
    create_demo_repo, write_file, commit, ask_keep,
)


def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s12: 深入 .git — Git 的内部原理{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    repo = create_demo_repo(name="internals-demo")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: 创建一些 commit，生成对象
    # ═══════════════════════════════════════════════════════════
    print_step(1, "创建 commit — 在 .git/objects/ 中生成对象")

    write_file(repo, "README.md", "# My Project\n\nWelcome!\n")
    commit(repo, "初始提交")

    write_file(repo, "src/main.py", 'print("Hello, World!")\n')
    commit(repo, "添加 main.py")

    show_time_tree(repo, "当前时间树 — 2 个 commit")

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: 探索 .git 目录
    # ═══════════════════════════════════════════════════════════
    print_step(2, "探索 .git 目录结构")

    import os
    git_dir = repo / ".git"

    print(f"  {Color.HIGHLIGHT}.git/ 目录结构:{Color.RESET}")
    for item in sorted(os.listdir(git_dir)):
        item_path = git_dir / item
        if item_path.is_dir():
            count = len(list(item_path.rglob("*")))
            print(f"  {Color.DIM}  {item}/\t(目录, {count} 个文件){Color.RESET}")
        else:
            size = item_path.stat().st_size
            print(f"  {Color.DIM}  {item}\t({size} bytes){Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: 查看 HEAD
    # ═══════════════════════════════════════════════════════════
    print_step(3, "HEAD — 「你现在在哪」")

    head_content = (git_dir / "HEAD").read_text().strip()
    print(f"  {Color.COMMAND}$ cat .git/HEAD{Color.RESET}")
    print(f"  {Color.TREE}{head_content}{Color.RESET}")

    print_note("HEAD 指向 refs/heads/master——这就是当前分支。")
    print_note("当你 git switch 其他分支时，这个文件的内容会改变。")

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: 查看 refs — 分支指针
    # ═══════════════════════════════════════════════════════════
    print_step(4, "refs — 分支和标签指针")

    refs_dir = git_dir / "refs" / "heads"
    for branch_file in refs_dir.iterdir():
        hash_value = branch_file.read_text().strip()
        print(f"  {Color.COMMAND}$ cat .git/refs/heads/{branch_file.name}{Color.RESET}")
        print(f"  {Color.TREE}{hash_value}{Color.RESET}")
        print(f"  {Color.DIM}→ {branch_file.name} 分支指向 commit {hash_value[:7]}{Color.RESET}")

    print_key_point(
        "分支 = 一个文件，里面写了一行 commit hash。\n"
        "    创建分支 = 在 .git/refs/heads/ 下创建一个新文件。\n"
        "    这就是为什么分支操作这么快——只是文件 I/O。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: 追踪对象链 — commit → tree → blob
    # ═══════════════════════════════════════════════════════════
    print_step(5, "对象链追踪 — commit → tree → blob")

    # 获取最新 commit 的 hash
    result = run_git("log --oneline -1", repo)
    commit_hash = result.stdout.strip().split()[0]

    # 查看 commit 对象
    print_command(f"git cat-file -p {commit_hash}", "查看 commit 对象")
    result = run_git(f"cat-file -p {commit_hash}", repo)
    print(f"\n  {Color.TREE}{result.stdout.strip()}{Color.RESET}\n")

    # 提取 tree hash
    tree_line = [l for l in result.stdout.strip().split("\n") if l.startswith("tree")][0]
    tree_hash = tree_line.split()[1]

    # 查看 tree 对象
    print_command(f"git cat-file -p {tree_hash}", "查看 tree 对象（目录快照）")
    result = run_git(f"cat-file -p {tree_hash}", repo)
    print(f"\n  {Color.TREE}{result.stdout.strip()}{Color.RESET}\n")

    print_note("tree 里列出了目录中所有的文件和子目录，以及它们对应的 blob/tree hash。")

    # 找一个 blob 来查看
    # 从 tree 输出中提取第一个 blob hash
    blob_lines = [l for l in result.stdout.strip().split("\n") if "blob" in l]
    if blob_lines:
        first_blob = blob_lines[0]
        blob_hash = first_blob.split()[2]
        blob_name = first_blob.split()[-1]

        print_command(f"git cat-file -p {blob_hash}", f"查看 blob 对象（{blob_name} 的内容）")
        result = run_git(f"cat-file -p {blob_hash}", repo)
        print(f"\n  {Color.TREE}{result.stdout.strip()}{Color.RESET}\n")

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: 查看对象类型
    # ═══════════════════════════════════════════════════════════
    print_step(6, "git cat-file -t — 查看对象类型")

    for name, h in [("commit", commit_hash), ("tree", tree_hash), ("blob", blob_hash)]:
        result = run_git(f"cat-file -t {h}", repo)
        print(f"  {Color.DIM}{h[:7]} → {Color.HIGHLIGHT}{result.stdout.strip()}{Color.RESET} ({name})")

    # ═══════════════════════════════════════════════════════════
    # 第 7 步: .git/objects/ 里的实际文件
    # ═══════════════════════════════════════════════════════════
    print_step(7, ".git/objects/ — 对象的实际存储")

    objects_dir = git_dir / "objects"
    obj_count = 0
    for subdir in sorted(os.listdir(objects_dir)):
        subdir_path = objects_dir / subdir
        if subdir_path.is_dir() and len(subdir) == 2:  # hash 目录
            files = list(subdir_path.iterdir())
            obj_count += len(files)
            if obj_count <= 10:  # 只展示前几个
                print(f"  {Color.DIM}objects/{subdir}/ → {len(files)} 个文件{Color.RESET}")

    print(f"\n  {Color.HIGHLIGHT}总计: {obj_count} 个 Git 对象{Color.RESET}")
    print_note(f"对象文件名 = SHA-1 哈希。前 2 位 = 目录名，后 38 位 = 文件名。")

    # ═══════════════════════════════════════════════════════════
    # 第 8 步: 总结
    # ═══════════════════════════════════════════════════════════
    print_step(8, "从对象模型回看 Git 操作")

    print(f"""
  {Color.HIGHLIGHT}Git 对象模型总览:{Color.RESET}

    {Color.DIM}blob{Color.RESET}   — 文件内容（不存文件名）
      ↓ 被 tree 引用
    {Color.DIM}tree{Color.RESET}   — 目录快照（blob 列表 + 文件名 + 权限）
      ↓ 被 commit 引用
    {Color.DIM}commit{Color.RESET} — 时间树节点（tree + parent + 元信息）
      ↓ 被 ref 引用
    {Color.DIM}ref{Color.RESET}    — 人类可读的名字（main, feature, HEAD...）

  {Color.HIGHLIGHT}所有 Git 操作都可以理解为:{Color.RESET}
    - 创建对象（add → blob, commit → commit+tree）
    - 移动指针（branch, reset, checkout, merge, rebase）

  {Color.HIGHLIGHT}为什么 Git 这么快？{Color.RESET}
    - 内容寻址：相同内容 = 相同 hash = 只存一份
    - 快照模型：checkout 不需要计算差异
    - 本地操作：不需要网络

  {Color.HIGHLIGHT}为什么 Git 这么可靠？{Color.RESET}
    - SHA-1 校验：内容被篡改 → hash 对不上 → Git 会发现
    - 不可变：旧 commit 不会被修改，只会创建新的
    - 分布式：每个人有完整副本
""")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束 — s23 全部课程完成！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 恭喜！你完成了 s23 全部 13 章的学习！{Color.RESET}

   s00  心智模型        →  Git = 时间树
   s01  第一次提交      →  种下第一个节点
   s02  浏览历史        →  在树上自由跳转
   s03  暂存区          →  三个区域的秘密
   s04  分支            →  平行宇宙
   s05  合并            →  两条时间线汇合
   s06  冲突            →  当历史「打架」
   s07  远程仓库        →  分享你的树
   s08  协作工作流      →  团队标准流程
   s09  rebase          →  嫁接树枝
   s10  精细操作        →  stash/cherry-pick/reset
   s11  时间旅行        →  reflog 黑匣子
   s12  内部原理        →  blob → tree → commit → ref

{Color.DIM}你不仅学会了 Git 的命令，更理解了 Git 的模型。
现在每次敲 git 命令时，你都能「看到」时间树的变化。
这才是真正掌握 Git。{Color.RESET}
""")

    ask_keep(repo)


if __name__ == "__main__":
    main()
