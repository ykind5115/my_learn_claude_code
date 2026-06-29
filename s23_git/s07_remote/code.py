#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s07: 远程仓库 — 把你的时间树分享给别人

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - origin 是什么？origin/main 和 main 有什么区别？
  - git push / git fetch / git pull 各自做了什么？
  - git clone 和 git init + git remote add 有什么区别？
  - 为什么 push 有时会被拒绝？
═══════════════════════════════════════════════════════════════

启动方式:
    python s23_git/s07_remote/code.py

注意: 本演示模拟两个「本地目录」充当两台电脑，不需要 GitHub 账号。
"""

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from s23_git.utils import (
    Color, run_git, show_time_tree, show_status,
    print_step, print_command, print_note, print_key_point,
    create_demo_repo, write_file, commit, ask_keep,
)


def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s07: 远程仓库 — 把你的时间树分享给别人{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print_note("本演示用两个本地目录模拟两台电脑，无需 GitHub 账号。")
    print_note("「远程仓库」= 一个 bare 仓库（没有工作区的纯时间树）")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: 创建「远程仓库」
    # ═══════════════════════════════════════════════════════════
    print_step(1, "创建「远程仓库」—— 模拟 GitHub")

    import tempfile
    base_dir = Path(tempfile.mkdtemp(prefix="s23git_remote_"))
    remote_dir = base_dir / "remote-repo.git"
    remote_dir.mkdir(parents=True)

    run_git("init --bare", remote_dir)
    print_command("git init --bare", "创建一个 bare 仓库（没有工作区的纯时间树）")
    print(f"  {Color.DIM}远程仓库位置: {remote_dir}{Color.RESET}")
    print_note("bare 仓库 = GitHub 上的仓库：只有 .git 的内容，不能直接编辑文件。")

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: 「张三」clone 远程仓库并开发
    # ═══════════════════════════════════════════════════════════
    print_step(2, "张三 clone 远程仓库并开始开发")

    zhangsan_dir = base_dir / "zhangsan"
    run_git(f"clone {remote_dir} {zhangsan_dir}", base_dir)
    print_command(f"git clone <remote-url>", "张三：复制整棵时间树到本地")

    show_time_tree(zhangsan_dir, "张三的仓库 — clone 后（可能为空）")

    # 张三做首次提交
    write_file(zhangsan_dir, "README.md", "# 团队项目\n\n这是我们的项目。\n")
    commit(zhangsan_dir, "张三：创建 README")

    write_file(zhangsan_dir, "app.py", 'print("Hello Team!")\n')
    commit(zhangsan_dir, "张三：创建 app.py")

    show_time_tree(zhangsan_dir, "张三做了 2 个 commit 后的时间树")

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: 张三 push 到远程
    # ═══════════════════════════════════════════════════════════
    print_step(3, "张三 git push — 把节点推送到远程")

    print_command("git push origin master", "张三：把我的新节点上传到远程")
    run_git("push origin master", zhangsan_dir)

    # 在远程仓库中查看
    show_time_tree(remote_dir, "远程仓库 — 现在有了张三的 commit")

    print_key_point(
        "git push 做了两件事:\n"
        "    1. 把本地的新节点（commit 对象）上传到远程\n"
        "    2. 把远程的 master 标签移到和本地一致的位置"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: 「李四」clone 并开发
    # ═══════════════════════════════════════════════════════════
    print_step(4, "李四 clone 并开发自己的功能")

    lisi_dir = base_dir / "lisi"
    run_git(f"clone {remote_dir} {lisi_dir}", base_dir)
    print_command("git clone <remote-url>", "李四：我也加入开发")

    show_time_tree(lisi_dir, "李四 clone 后 — 和张三的树一样")

    # 李四开发新功能
    run_git("switch -c feature-utils", lisi_dir)
    write_file(lisi_dir, "utils.py", 'def add(a, b): return a + b\n')
    commit(lisi_dir, "李四：添加工具函数")
    write_file(lisi_dir, "utils.py", 'def add(a, b):\n    return a + b\n\ndef sub(a, b):\n    return a - b\n')
    commit(lisi_dir, "李四：完善工具函数")

    show_time_tree(lisi_dir, "李四在 feature-utils 分支上开发了 2 个 commit")

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: 李四 push 自己的分支
    # ═══════════════════════════════════════════════════════════
    print_step(5, "李四 push 自己的分支到远程")

    print_command("git push origin feature-utils", "李四：把我的分支推上去")
    run_git("push origin feature-utils", lisi_dir)

    show_time_tree(remote_dir, "远程仓库 — 现在有两个分支了")

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: 张三 fetch — 看看有什么新东西
    # ═══════════════════════════════════════════════════════════
    print_step(6, "张三 git fetch — 看看远程有什么新东西")

    print_command("git fetch origin", "张三：下载远程更新（不合并）")
    run_git("fetch origin", zhangsan_dir)

    print_note("fetch 只更新了 origin/* 指针，本地 master 和 HEAD 没变。")

    show_time_tree(zhangsan_dir, "张三 fetch 后 — origin/feature-utils 出现了")

    print_command("git branch -r", "查看远程分支")
    result = run_git("branch -r", zhangsan_dir)
    print(f"\n  {Color.TREE}{result.stdout.strip()}{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 7 步: 张三 pull = fetch + merge
    # ═══════════════════════════════════════════════════════════
    print_step(7, "git pull — fetch + merge 一步完成")

    # 先让张三在 master 上也做一个 commit，产生交叉
    write_file(zhangsan_dir, "config.py", 'VERSION = "1.0"\n')
    commit(zhangsan_dir, "张三：添加配置文件")

    # 现在模拟 pull：把李四的 feature-utils 合并进来
    print_command("git pull origin feature-utils", "张三：拉取李四的分支并合并")
    # 用 fetch + merge 代替 pull，更清楚地展示过程
    run_git("fetch origin", zhangsan_dir)
    result = run_git("merge origin/feature-utils -m '合并李四的工具函数'", zhangsan_dir, check=False)

    show_time_tree(zhangsan_dir, "合并后 — 张三的时间树有了李四的节点")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 你理解了远程协作的核心！{Color.RESET}

   {Color.HIGHLIGHT}git clone <url>{Color.RESET}     →  复制整棵时间树到本地
   {Color.HIGHLIGHT}git push{Color.RESET}             →  把我的节点发给远程
   {Color.HIGHLIGHT}git fetch{Color.RESET}            →  下载远程的新节点（不合并）
   {Color.HIGHLIGHT}git pull{Color.RESET}             →  fetch + merge 一步完成
   {Color.HIGHLIGHT}origin/main{Color.RESET}          →  远程 main 的本地镜像指针

{Color.DIM}远程仓库 = 另一棵独立的时间树。push/fetch/pull 就是同步两棵树。{Color.RESET}
""")

    # 清理（Windows 上某些 git 文件可能被锁定，忽略错误）
    import shutil
    try:
        shutil.rmtree(base_dir)
    except PermissionError:
        pass
    print(f"{Color.SUCCESS}✅ 演示环境已清理{Color.RESET}\n")


if __name__ == "__main__":
    main()
