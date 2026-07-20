#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s26-04: 进程管理 — ps, kill, fg/bg, 信号, 僵尸进程

学习目标:
  - 查看和管理进程
  - 理解前台/后台切换
  - 理解信号的用途
  - 理解僵尸进程的产生和回收

运行: python s26_linux/s04_process/code.py
"""

import os
import sys
import time
import signal as sig_module
import subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, run_cmd, print_step, print_note,
                   print_key_point, print_section)


# ═══════════════════════════════════════════════════════════
def demo_1_current_process():
    print_step(1, "查看当前进程")
    pid = os.getpid()
    ppid = os.getppid()
    print(f"  当前 Python 进程 PID: {Color.HIGHLIGHT}{pid}{Color.RESET}")
    print(f"  父进程 PID: {Color.HIGHLIGHT}{ppid}{Color.RESET} (启动你的终端/shell)")

    # 在真正的 Linux 上展示 /proc
    if os.path.exists(f"/proc/{pid}/status"):
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith(("Name:", "State:", "VmRSS:", "Threads:")):
                    print(f"  {line.strip()}")


def demo_2_ps_and_pstree():
    print_step(2, "ps — 进程快照")
    ret, out, err = run_cmd("ps")
    if ret == 0 and out.strip():
        # 只显示几个关键进程
        lines = out.strip().split("\n")
        print(f"  {lines[0]}  (当前终端的进程)")
        for line in lines[1:5]:
            print(f"  {line}")
        if len(lines) > 5:
            print(f"  ... 共 {len(lines)-1} 个进程")


def demo_3_foreground_background():
    print_step(3, "前台 vs 后台")
    print(f"  前台进程: 占着终端，你得等它跑完")
    print(f"  后台进程: 在后台跑，终端还给你用")
    print(f"    command &      → 后台运行")
    print(f"    Ctrl+Z         → 暂停前台进程")
    print(f"    bg             → 让暂停的进程在后台继续")
    print(f"    fg             → 把后台进程拉回前台")
    print(f"    jobs           → 查看后台任务列表")

    # 演示后台子进程
    print(f"\n  启动一个后台子进程...")
    p = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(2); print('后台任务完成')"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    print(f"  子进程 PID: {p.pid}, 状态: {'运行中' if p.poll() is None else '已结束'}")
    print_note("主程序继续跑，不等子进程 → 这就是 & 的效果")

    # 等子进程结束并读取输出（用 communicate 避免死锁）
    out, _ = p.communicate()
    print(f"  子进程结束: {out.strip()}")


def demo_4_signals():
    print_step(4, "信号 — Linux 的对讲系统")

    signals = [
        ("SIGINT", 2, "Ctrl+C，可捕获的'请停下'"),
        ("SIGTERM", 15, "优雅退出(默认)，可捕获处理"),
        ("SIGKILL", 9, "立刻杀死，不可捕获不可忽略"),
        ("SIGSTOP", 19, "暂停进程，不可捕获"),
        ("SIGCONT", 18, "继续被暂停的进程"),
    ]
    for name, num, desc in signals:
        print(f"  {Color.BOLD}{name:10s}{Color.RESET} ({num:2d}) — {desc}")

    # 演示信号处理
    print(f"\n  {Color.HIGHLIGHT}演示: Python 捕获 SIGINT (Ctrl+C){Color.RESET}")

    def handler(signum, frame):
        print(f"\n  收到信号 {signum}! 优雅退出...")
        sys.exit(0)

    old = sig_module.signal(sig_module.SIGINT, handler)
    print_note("已注册信号处理器 (Ctrl+C 会优雅退出)")
    print_note(f"  s01 subprocess.run(timeout=5) → 超时先发 SIGTERM → 再发 SIGKILL")
    sig_module.signal(sig_module.SIGINT, old)


def demo_5_zombie():
    print_step(5, "僵尸进程")
    print(f"  僵尸 = 子进程已死，但父进程还没 waitpid() 收尸")
    print(f"  不占 CPU/内存，但占 PID 槽位")
    print(f"  ps 会显示 <defunct> 或 Z 状态")
    print_note("s01 的 subprocess.run() 自动 wait，不会产生僵尸")
    print_note("s13 后台任务需要手动管理子进程生命周期")

    # 实际创建一个子进程并正确回收
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    print(f"  waitpid → 退出码 {p.returncode} (已正确回收)")
    print_key_point("子进程 exit 后必须 wait/waitpid，否则变僵尸")


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print_section("s26-04: 进程管理")

    demo_1_current_process()
    demo_2_ps_and_pstree()
    demo_3_foreground_background()
    demo_4_signals()
    demo_5_zombie()

    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("小结:")
    print_key_point("  ps 看进程, & 后台, Ctrl+C=SIGINT, kill -9=SIGKILL")
    print_key_point("  subprocess.run() = fork+exec+waitpid (自动收尸)")
