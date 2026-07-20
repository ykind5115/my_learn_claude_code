#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s26-01: 文件系统层次结构 — FHS 标准目录

学习目标:
  - 认识 Linux 根目录下每个标准目录的用途
  - 理解 /proc 虚拟文件系统
  - 掌握绝对路径和相对路径

运行: python s26_linux/s01_filesystem/code.py
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, run_cmd, print_step, print_note, print_key_point, print_section

# ═══════════════════════════════════════════════════════════
FHS_DIRS = {
    "/bin": "基础命令 (ls, cat, cp, bash)",
    "/etc": "系统配置文件",
    "/home": "用户家目录 (你的文件在这里)",
    "/var": "动态数据 (日志, 缓存, 数据库)",
    "/tmp": "临时文件 (所有人可写, 重启清空)",
    "/proc": "虚拟文件系统 (进程信息, CPU/内存信息)",
    "/dev": "设备文件 (硬盘, 终端, 随机数)",
    "/usr": "用户程序 (/usr/bin, /usr/lib)",
    "/opt": "第三方大型软件",
    "/boot": "启动文件 (内核, 引导程序)",
    "/root": "root 用户的家目录",
}


# ═══════════════════════════════════════════════════════════
def demo_1_root_dirs():
    print_step(1, "查看根目录")
    ret, out, err = run_cmd("ls -1 /")
    if ret == 0:
        print(f"  $ ls /")
        for line in sorted(out.strip().split("\n")):
            marker = " ←" if line in FHS_DIRS else ""
            print(f"    {Color.BOLD}{line}{Color.RESET}{Color.DIM}{marker}{Color.RESET}")


def demo_2_fhs_explained():
    print_step(2, "FHS 标准目录说明")
    for path, desc in FHS_DIRS.items():
        print(f"  {Color.FILE_PATH}{path:10s}{Color.RESET} {Color.DIM}→{Color.RESET} {desc}")


def demo_3_proc_explore():
    print_step(3, "/proc — 窥探内核")

    # 进程自身信息
    print(f"\n  {Color.HIGHLIGHT}当前进程信息:{Color.RESET}")
    pid = os.getpid()
    print(f"  PID: {pid}")

    # /proc/self 总是指向当前进程
    if os.path.exists("/proc/self/status"):
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith(("Name:", "Pid:", "VmRSS:", "Threads:")):
                    key, val = line.strip().split("\t")
                    print(f"  {key:12s} {val}")
    else:
        print_note("(不在 Linux 上 — /proc 不可用)")
        print_note("  模拟 /proc/self/status:")
        print(f"    Name:   python")
        print(f"    Pid:    {pid}")
        print(f"    VmRSS:  ~30 MB (进程占用物理内存)")
        print(f"    Threads: 1")

    # CPU 信息
    if os.path.exists("/proc/cpuinfo"):
        print(f"\n  {Color.HIGHLIGHT}CPU 信息 (/proc/cpuinfo):{Color.RESET}")
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    print(f"  {line.strip()}")
                    break
    else:
        print_note("(不在 Linux 上 — /proc/cpuinfo 不可用)")

    print_key_point("/proc 是虚拟的——这些'文件'不存在于磁盘，内核实时生成")


def demo_4_path_types():
    print_step(4, "绝对路径 vs 相对路径")
    cwd = os.getcwd()
    print(f"  当前工作目录 (CWD): {cwd}")

    examples = [
        ("绝对路径", "/home/user/project/code.py", "从 / 开始，在哪都能找到"),
        ("相对路径", "./code.py", "从当前目录 . 出发"),
        ("相对路径(上级)", "../s01/code.py", ".. 回到父目录再进入"),
    ]
    for kind, path, note in examples:
        print(f"  {Color.BOLD}{kind:15s}{Color.RESET} {Color.FILE_PATH}{path:35s}{Color.RESET} {Color.DIM}{note}{Color.RESET}")


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print_section("s26-01: 文件系统层次结构 (FHS)")

    demo_1_root_dirs()
    demo_2_fhs_explained()
    demo_3_proc_explore()
    demo_4_path_types()

    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("小结:")
    print_key_point("  /bin=工具间  /etc=配置柜  /home=储物柜  /var=动态区  /tmp=临时区")
    print_key_point("  /proc 是虚拟文件系统 — 进程信息、CPU、内存都'伪装'成文件")
    print_key_point("  绝对路径从 / 开始，相对路径从当前目录 . 开始")
