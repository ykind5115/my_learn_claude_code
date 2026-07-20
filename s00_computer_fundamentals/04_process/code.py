#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s00-04: 进程 — fork, exec, stdin/stdout/stderr, 退出码, 环境变量

学习目标:
  - 理解 fork/exec/waitpid 模型
  - 区分 stdout 和 stderr
  - 理解退出码
  - 理解环境变量继承

运行: python 04_process/code.py
"""

import os
import sys
import subprocess
import time


# ═══════════════════════════════════════════════════════════
# Demo 1: 当前进程的基本信息
# ═══════════════════════════════════════════════════════════
def demo_1_process_info():
    print("── Demo 1: 进程基本信息 ──")
    print(f"  PID: {os.getpid()}")
    print(f"  父进程 PID: {os.getppid()}")
    print(f"  CWD (当前工作目录): {os.getcwd()}")
    print(f"  PATH 环境变量前 80 字符: {os.environ.get('PATH', 'N/A')[:80]}...")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 2: subprocess.run — 创建子进程
# ═══════════════════════════════════════════════════════════
def demo_2_subprocess_run():
    print("── Demo 2: subprocess.run 创建子进程 ──")

    # 成功命令
    r = subprocess.run(
        ["echo", "hello from child process"],
        capture_output=True,
        text=True,
    )
    print(f"  命令: echo hello")
    print(f"  stdout: {r.stdout.strip()!r}")
    print(f"  stderr: {r.stderr!r}")
    print(f"  退出码: {r.returncode} (0=成功)")

    # 失败命令
    print()
    r = subprocess.run(
        ["ls", "/nonexistent_path_xyz"],
        capture_output=True,
        text=True,
    )
    print(f"  命令: ls /nonexistent_path")
    print(f"  stdout: {r.stdout!r}")
    print(f"  stderr: {r.stderr.strip()!r}")
    print(f"  退出码: {r.returncode} (非0=失败)")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 3: stdout vs stderr — 为什么要合并？
# ═══════════════════════════════════════════════════════════
def demo_3_stdout_vs_stderr():
    print("── Demo 3: stdout vs stderr 分离对比 ──")

    # 用 Python 子进程同时写 stdout 和 stderr
    code = """
import sys
sys.stdout.write("这是 stdout: 正常输出\\n")
sys.stderr.write("这是 stderr: 错误信息\\n")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    print(f"  只读 stdout: {r.stdout.strip()!r}")
    print(f"  只读 stderr: {r.stderr.strip()!r}")
    print(f"  合并 (stdout+stderr): {(r.stdout + r.stderr).strip()!r}")
    print(f"  → s01 的做法: out = (r.stdout + r.stderr).strip()")
    print(f"    这样模型能看到完整输出，不会漏掉报错")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 4: 环境变量继承
# ═══════════════════════════════════════════════════════════
def demo_4_env_inheritance():
    print("── Demo 4: 环境变量继承 ──")

    # 父进程设置环境变量
    os.environ["S00_DEMO_VAR"] = "hello-from-parent"

    # 子进程能看到吗？
    code = """
import os
print(os.environ.get("S00_DEMO_VAR", "NOT FOUND"))
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=os.environ.copy(),  # 显式传递所有环境变量
    )
    print(f"  父进程设置: S00_DEMO_VAR=hello-from-parent")
    print(f"  子进程读取: {r.stdout.strip()}")
    print(f"  → 子进程继承了父进程的环境变量")
    print()

    # 隔离环境变量
    print(f"  传入空环境:")
    r2 = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env={"PATH": os.environ["PATH"]},  # 只传 PATH
    )
    print(f"  子进程读取: {r2.stdout.strip()}")
    print(f"  → 不传就看不到")

    # 清理
    del os.environ["S00_DEMO_VAR"]
    print()


# ═══════════════════════════════════════════════════════════
# Demo 5: shell=True vs shell=False
# ═══════════════════════════════════════════════════════════
def demo_5_shell_mode():
    print("── Demo 5: shell=True vs shell=False ──")

    # shell=False: 直接 exec，不经过 shell 解析
    r1 = subprocess.run(
        ["echo", "$HOME"],  # $HOME 被当作字面字符串
        capture_output=True, text=True,
    )
    print(f"  shell=False: echo $HOME → {r1.stdout.strip()!r}")
    print(f"    → $HOME 没有展开，因为是字面量")

    # shell=True: 经过 shell 解析，变量展开、通配符、管道都生效
    if sys.platform == "win32":
        r2 = subprocess.run(
            "echo %USERPROFILE%",
            shell=True, capture_output=True, text=True,
        )
        print(f"  shell=True:  echo %USERPROFILE% → {r2.stdout.strip()}")
    else:
        r2 = subprocess.run(
            "echo $HOME",
            shell=True, capture_output=True, text=True,
            executable="/bin/bash",
        )
        print(f"  shell=True:  echo $HOME → {r2.stdout.strip()}")
    print(f"    → 变量被 shell 展开了")
    print(f"  ⚠ shell=True 有注入风险：永远不要对用户输入用 shell=True")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 6: 超时和异常处理
# ═══════════════════════════════════════════════════════════
def demo_6_timeout():
    print("── Demo 6: 超时控制 ──")

    try:
        subprocess.run(
            [sys.executable, "-c", "import time; time.sleep(10)"],
            timeout=0.5,  # 0.5 秒超时
            capture_output=True,
        )
    except subprocess.TimeoutExpired as e:
        print(f"  捕获 TimeoutExpired!")
        print(f"  命令: {e.cmd}")
        print(f"  超时设置: {e.timeout}s")
        print(f"  → s01/s13 用 timeout 防止命令卡死")
    print()


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("s00-04: 进程 — subprocess, stdin/stdout/stderr, 退出码")
    print("=" * 60)
    print()

    demo_1_process_info()
    demo_2_subprocess_run()
    demo_3_stdout_vs_stderr()
    demo_4_env_inheritance()
    demo_5_shell_mode()
    demo_6_timeout()

    print("─" * 60)
    print("小结:")
    print("  进程 = fork() + exec() + waitpid()")
    print("  每个进程: stdin(0) stdout(1) stderr(2)")
    print("  退出码: 0=成功, 非0=失败")
    print("  子进程继承: 环境变量 + CWD")
    print("  s01 的 subprocess.run() → 以上全部")
