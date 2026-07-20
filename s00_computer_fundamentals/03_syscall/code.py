#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s00-03: 系统调用 — 用户态/内核态，fork/exec/waitpid

学习目标:
  - 理解用户态和内核态的区分
  - 认识 Python 代码背后的系统调用
  - 理解 fork 的行为：一次调用，两次返回

运行: python 03_syscall/code.py
"""

import os
import sys
import time
import subprocess


# ═══════════════════════════════════════════════════════════
# Demo 1: Python 操作对应的系统调用
# ═══════════════════════════════════════════════════════════
def demo_1_python_to_syscall():
    print("── Demo 1: Python → 系统调用映射 ──")

    print("  你的 Python 代码底层都调了系统调用:")

    examples = [
        ("open('file.txt')", "open()"),
        ("os.read(fd, n)", "read()"),
        ("os.write(fd, data)", "write()"),
        ("subprocess.run()", "fork() + exec() + waitpid()"),
        ("time.sleep(1)", "nanosleep()"),
        ("os.getpid()", "getpid()"),
        ("os.mkdir('dir')", "mkdir()"),
        ("socket.connect()", "connect()"),
    ]
    for py_code, syscall in examples:
        print(f"    {py_code:30s} → {syscall}")

    # 演示：看系统调用开销
    print()
    print("  系统调用开销测试:")

    # 1 次系统调用
    start = time.time()
    for _ in range(100000):
        os.getpid()  # 每次都是一次 getpid 系统调用
    syscall_time = time.time() - start
    print(f"    10 万次 os.getpid() (每1次1个系统调用): {syscall_time:.4f}s")

    # 0 次系统调用（纯用户态）
    start = time.time()
    x = 0
    for _ in range(100000):
        x += 1  # 纯寄存器操作，没有系统调用
    user_time = time.time() - start
    print(f"    10 万次 x += 1 (纯用户态，0个系统调用): {user_time:.6f}s")
    if user_time > 0:
        print(f"    系统调用比纯计算慢: ~{syscall_time / user_time:.0f}x")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 2: fork() 演示 — Linux/macOS only
# ═══════════════════════════════════════════════════════════
def demo_2_fork():
    print("── Demo 2: fork() 演示 ──")

    if sys.platform == "win32":
        print("  Windows 没有 fork()，用 subprocess 模拟")
        print("  subprocess.run() 内部调用 CreateProcess()")
        r = subprocess.run(
            [sys.executable, "-c",
             "import os; print(f'子进程 PID: {os.getpid()}')"],
            capture_output=True, text=True,
        )
        print(f"  父进程 PID: {os.getpid()}")
        print(f"  {r.stdout.strip()}")
        print(f"  → 父子进程是不同的 PID")
    else:
        print(f"  父进程 PID: {os.getpid()}")
        pid = os.fork()
        if pid == 0:
            # 子进程：fork 返回 0
            print(f"  子进程 PID: {os.getpid()}, fork 返回值: {pid}")
            print(f"  → 子进程里 fork() 返回 0")
            os._exit(0)
        else:
            # 父进程：fork 返回子进程的 PID
            print(f"  父进程: fork 返回值 = {pid} (这是子进程的 PID)")
            os.waitpid(pid, 0)
            print(f"  → 父进程里 fork() 返回子进程的 PID")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 3: 追踪 subprocess 的系统调用流程
# ═══════════════════════════════════════════════════════════
def demo_3_subprocess_syscalls():
    print("── Demo 3: subprocess 底层流程 ──")

    print("  Python: subprocess.run(['echo', 'hello'])")
    print()
    if sys.platform == "win32":
        print("  Windows 流程:")
        print("    1. CreateProcess('echo', 'hello')")
        print("    2. WaitForSingleObject(process_handle)")
        print("    3. GetExitCodeProcess(process_handle)")
    else:
        print("  Unix 流程:")
        print("    1. fork()        — 复制当前进程")
        print("    2. exec('echo')  — 新程序覆盖子进程")
        print("    3. waitpid(pid)  — 等待子进程结束")

    # 实际跑一遍
    r = subprocess.run(["echo", "hello from subprocess"],
                       capture_output=True, text=True)
    print(f"  执行结果: stdout={r.stdout.strip()!r}, returncode={r.returncode}")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 4: 用户态 vs 内核态 — 操作系统的保护机制
# ═══════════════════════════════════════════════════════════
def demo_4_protection():
    print("── Demo 4: 用户态不能做的事 ──")

    print("  尝试直接访问硬件？不行——")
    print("    用户态程序不能执行 in/out 指令(端口 I/O)")
    print("    不能直接修改页表")
    print("    不能直接访问磁盘扇区")
    print("    必须通过系统调用让内核代劳")

    # 演示：尝试访问 /dev/mem (Linux)
    if sys.platform != "win32":
        try:
            with open("/dev/mem", "rb") as f:
                pass
            print("    (root 权限可以访问 /dev/mem)")
        except PermissionError:
            print("    /dev/mem: Permission denied (普通用户不行)")
        except FileNotFoundError:
            print("    /dev/mem: 不存在 (macOS 没有)")

    print("    → 这就是用户态/内核态隔离的意义：防止你（或 bug）搞坏系统")
    print()


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("s00-03: 系统调用 — 用户态/内核态的桥梁")
    print("=" * 60)
    print()

    demo_1_python_to_syscall()
    demo_2_fork()
    demo_3_subprocess_syscalls()
    demo_4_protection()

    print("─" * 60)
    print("小结:")
    print("  用户态(你的代码) ──系统调用──→ 内核态(OS)")
    print("  常见调用: open/read/write/fork/exec/waitpid")
    print("  fork: 一次调用，两次返回 (父进程得子进程PID，子进程得0)")
    print("  subprocess.run() = fork + exec + waitpid (Unix)")
    print("                    = CreateProcess (Windows)")
