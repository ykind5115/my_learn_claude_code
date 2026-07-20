#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s26-02: 文件操作与权限 — rwx, chmod, chown, inode

学习目标:
  - 理解 rwx 权限的三元组
  - 掌握 chmod (符号和数字两种方式)
  - 理解 inode 和硬链接

运行: python s26_linux/s02_file_ops/code.py
"""

import os
import sys
import stat
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, run_cmd, print_step, print_note,
                   print_key_point, print_section, create_demo_dir, cleanup_demo_dir)


def permission_str(mode):
    """把 st_mode 转成 ls -l 格式的权限字符串"""
    kind = "d" if stat.S_ISDIR(mode) else "-"
    r = "r" if mode & stat.S_IRUSR else "-"
    w = "w" if mode & stat.S_IWUSR else "-"
    x = "x" if mode & stat.S_IXUSR else "-"
    return f"{kind}{r}{w}{x}"


# ═══════════════════════════════════════════════════════════
def demo_1_create_and_stat():
    print_step(1, "创建文件并查看权限")
    demo = create_demo_dir()

    # 创建文件
    f = demo / "hello.txt"
    f.write_text("Hello Linux!")
    print(f"  创建: {f}")

    # stat 查看
    st = f.stat()
    print(f"  inode: {st.st_ino}")
    print(f"  大小: {st.st_size} bytes")
    print(f"  权限: {permission_str(st.st_mode)} (八进制: {oct(stat.S_IMODE(st.st_mode))})")
    print_note(f"默认新文件权限由 umask 决定，通常是 644 (rw-r--r--)")

    cleanup_demo_dir(demo)


def demo_2_chmod():
    print_step(2, "chmod — 改权限")
    demo = create_demo_dir()
    f = demo / "script.sh"
    f.write_text("#!/bin/bash\necho hello")

    # 查看默认权限
    st = f.stat()
    mode = stat.S_IMODE(st.st_mode)
    print(f"  初始权限: {permission_str(st.st_mode)} ({oct(mode)})")

    # 加执行权限
    os.chmod(str(f), mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    st = f.stat()
    new_mode = stat.S_IMODE(st.st_mode)
    print(f"  chmod +x 后: {permission_str(st.st_mode)} ({oct(new_mode)})")
    print_note("chmod +x = 给所有人加执行权限")
    print_note("chmod 755 = rwxr-xr-x (属主全权限，其他人读+执行)")
    print_note("chmod 600 = rw------- (只有属主能读写)")

    # 数字权限速查
    print(f"\n  {Color.HIGHLIGHT}数字权限速查:{Color.RESET}")
    for num, perms, meaning in [
        (7, "rwx", "读+写+执行"),
        (6, "rw-", "读+写"),
        (5, "r-x", "读+执行"),
        (4, "r--", "只读"),
    ]:
        print(f"    {num} = {perms} ({meaning})")

    cleanup_demo_dir(demo)


def demo_3_directory_perms():
    print_step(3, "目录权限的特殊性")
    demo = create_demo_dir()
    subdir = demo / "secret"
    subdir.mkdir()
    (subdir / "note.txt").write_text("top secret")

    print(f"  目录: {subdir}")
    print(f"  r(读) = 能 ls 看到目录内容")
    print(f"  x(执行) = 能 cd 进入目录")
    print(f"  → 只有 r 没有 x: 能看到文件名但进不去")
    print(f"  → 只有 x 没有 r: 能进去但看不到文件列表(如果知道文件名可以访问)")

    cleanup_demo_dir(demo)


def demo_4_hard_link():
    print_step(4, "硬链接 — 多个文件名指向同一个 inode")
    demo = create_demo_dir()

    # 创建原始文件
    orig = demo / "original.txt"
    orig.write_text("same data")
    orig_ino = orig.stat().st_ino
    print(f"  original.txt → inode {orig_ino}")

    # 创建硬链接
    link = demo / "hardlink.txt"
    os.link(str(orig), str(link))
    link_ino = link.stat().st_ino
    print(f"  hardlink.txt → inode {link_ino}")
    print_key_point(f"同一个 inode! ({orig_ino} == {link_ino})")

    # 修改任意一个，两个都看到变化
    link.write_text("modified via link!")
    print(f"  修改硬链接后:")
    print(f"    original.txt: {orig.read_text()!r}")
    print(f"    hardlink.txt: {link.read_text()!r}")
    print_key_point("硬链接 = 同一个文件的两个名字，改谁都是一样的")

    cleanup_demo_dir(demo)


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print_section("s26-02: 文件操作与权限")

    demo_1_create_and_stat()
    demo_2_chmod()
    demo_3_directory_perms()
    demo_4_hard_link()

    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("小结:")
    print_key_point("  r=4 w=2 x=1 → chmod 755 = rwxr-xr-x")
    print_key_point("  目录 x = 能 cd 进入, 目录 r = 能 ls")
    print_key_point("  硬链接 = 多个文件名 → 同一个 inode (同一份数据)")
