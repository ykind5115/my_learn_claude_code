#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s26-06: 用户、组、sudo — UID/GID, root, 文件属主

学习目标:
  - 理解 UID/GID 和文件属主
  - 理解 root 和 sudo 的区别
  - 知道什么时候需要 sudo

运行: python s26_linux/s06_users_perms/code.py
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, run_cmd, print_step, print_note,
                   print_key_point, print_section)


# ═══════════════════════════════════════════════════════════
def demo_1_whoami():
    print_step(1, "我是谁？")
    print(f"  用户名: {Color.HIGHLIGHT}{os.environ.get('USER', os.environ.get('USERNAME', '?'))}{Color.RESET}")
    print(f"  PID: {os.getpid()}")
    print(f"  实际 UID: {os.getuid() if hasattr(os, 'getuid') else 'N/A (Windows)'}")
    print(f"  有效 UID: {os.geteuid() if hasattr(os, 'geteuid') else 'N/A (Windows)'}")
    print_note("有效 UID (euid) 是实际用来做权限检查的——sudo 会改变它")


def demo_2_passwd_and_group():
    print_step(2, "用户和组数据库")

    if sys.platform != "win32":
        # 读 /etc/passwd
        print(f"  /etc/passwd 中的用户 (前 5 个):")
        try:
            with open("/etc/passwd") as f:
                for i, line in enumerate(f):
                    if i >= 5:
                        break
                    parts = line.strip().split(":")
                    if len(parts) >= 7:
                        print(f"    {parts[0]:15s} UID={parts[2]:5s} GID={parts[3]:5s}  {parts[4]:20s} {parts[5]}")
        except PermissionError:
            print_note("(无权限读取)")

        # 当前用户
        try:
            import pwd
            me = pwd.getpwuid(os.getuid())
        except (ImportError, AttributeError):
            print_note("(Windows — 用户管理用 net user 命令)")
            return
        print(f"\n  当前用户信息:")
        print(f"    pw_name: {me.pw_name}")
        print(f"    pw_uid:  {me.pw_uid}")
        print(f"    pw_gid:  {me.pw_gid}")
        print(f"    pw_dir:  {me.pw_dir}")
        print(f"    pw_shell: {me.pw_shell}")
    else:
        print_note("(Windows — 用户管理用 net user 命令)")


def demo_3_file_ownership():
    print_step(3, "文件属主")
    print(f"  每个文件都有属主(user)和属组(group):")
    print(f"    $ ls -l script.sh")
    print(f"    -rwxr-xr-x  1 {Color.BOLD}alice  dev{Color.RESET}  1024  Jul 20 10:00  script.sh")
    print(f"                  ─┬──   ─┬─")
    print(f"                 属主    属组")

    # 演示当前文件的属主
    current_file = __file__
    st = os.stat(current_file)
    print(f"\n  当前文件: {current_file}")
    try:
        import pwd, grp
        owner = pwd.getpwuid(st.st_uid).pw_name
        group = grp.getgrgid(st.st_gid).gr_name
        print(f"    属主: {owner} (UID {st.st_uid})")
        print(f"    属组: {group} (GID {st.st_gid})")
        print_note(f"chown {owner}:{group} file → 改属主和属组")
    except (ImportError, AttributeError):
        print_note("(Windows — 无 pwd/grp 模块，但概念相同)")


def demo_4_root_and_sudo():
    print_step(4, "root 和 sudo")

    print(f"  {Color.BOLD}root (UID=0){Color.RESET}")
    print(f"    → 系统总管，所有权限")
    print(f"    → 能绑定 1-1023 端口")
    print(f"    → 能改任何文件")
    print(f"    → 能杀任何进程")

    print(f"\n  {Color.BOLD}sudo{Color.RESET}")
    print(f"    → '以 root 身份执行这条命令'")
    print(f"    → sudo apt install nginx")
    print(f"    → sudo python -m http.server 80 (需要 root 才能绑 80 端口)")
    print(f"    → /etc/sudoers 控制谁可以用 sudo")
    print_note("s03 权限系统 = Linux 文件权限 + sudo 的 Agent 版本")


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print_section("s26-06: 用户、组、sudo")

    demo_1_whoami()
    demo_2_passwd_and_group()
    demo_3_file_ownership()
    demo_4_root_and_sudo()

    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("小结:")
    print_key_point("  root(UID=0) = 总管, sudo = 临时借总管的钥匙")
    print_key_point("  每个文件有属主(UID)和属组(GID)")
    print_key_point("  Agent 权限系统 对应 Linux rwx + sudo 模型")
