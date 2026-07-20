#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s26-03: 管道与重定向 — stdin/stdout/stderr, pipe, redirect

学习目标:
  - 理解 stdin/stdout/stderr 三根"管子"
  - 掌握重定向: > >> 2> 2>&1
  - 理解管道 | 的并行数据流

运行: python s26_linux/s03_pipes_redirect/code.py
"""

import os
import sys
import subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, run_cmd, print_step, print_note,
                   print_key_point, print_section, create_demo_dir, cleanup_demo_dir)


# ═══════════════════════════════════════════════════════════
def demo_1_three_streams():
    print_step(1, "三根管子: stdin/stdout/stderr")
    print(f"  每个进程自带:")
    print(f"    {Color.BOLD}stdin  (fd 0){Color.RESET} — 输入流 (默认接键盘)")
    print(f"    {Color.BOLD}stdout (fd 1){Color.RESET} — 输出流 (默认接屏幕)")
    print(f"    {Color.BOLD}stderr (fd 2){Color.RESET} — 错误流 (默认接屏幕)")

    # 写一个同时输出 stdout 和 stderr 的 Python 片段
    code = """
import sys
sys.stdout.write("stdout: 正常输出\\n")
sys.stderr.write("stderr: 错误信息\\n")
"""
    # 分开捕获
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    print(f"\n  {Color.COMMAND}同时写 stdout 和 stderr:{Color.RESET}")
    print(f"    stdout: {r.stdout.strip()!r}")
    print(f"    stderr: {r.stderr.strip()!r}")
    print_note("s01 的做法: out = (r.stdout + r.stderr).strip() → 合并二者")


def demo_2_redirect():
    print_step(2, "重定向: > >> 2> 2>&1")
    demo = create_demo_dir()

    # > 覆盖写入
    f1 = demo / "out1.txt"
    run_cmd(f'echo "line 1" > {f1}')
    run_cmd(f'echo "line 2" > {f1}')  # 覆盖！
    content = f1.read_text().strip()
    print(f"  用 > 写两次: {content!r}")
    print_note("> 是覆盖——第二次写入覆盖了第一次")

    # >> 追加写入
    f2 = demo / "out2.txt"
    run_cmd(f'echo "line 1" >> {f2}')
    run_cmd(f'echo "line 2" >> {f2}')
    content = f2.read_text().strip()
    print(f"  用 >> 写两次: {content!r}")
    print_note(">> 是追加——两次都保留")

    # 2> 重定向 stderr
    f3 = demo / "errors.txt"
    code = "import sys; sys.stdout.write('ok\\n'); sys.stderr.write('bad\\n')"
    ret, out, err = run_cmd(f'{sys.executable} -c "{code}" 2> {f3}')
    print(f"  2> errors.txt 后:")
    print(f"    屏幕上: {out.strip()!r}")
    print(f"    errors.txt: {f3.read_text().strip()!r}")
    print_note("stderr 被重定向到文件，屏幕上只剩 stdout")

    cleanup_demo_dir(demo)


def demo_3_pipe():
    print_step(3, "管道 | — 传送带")

    # 用 Python 模拟管道效果
    print(f"\n  {Color.COMMAND}echo -e 'a\\nb\\nc' | grep a{Color.RESET}")
    r1 = subprocess.run(["echo", "a\nb\nc"], capture_output=True, text=True)
    # 把 r1.stdout 作为 r2 的 stdin
    r2 = subprocess.run(["grep", "a"], input=r1.stdout, capture_output=True, text=True)
    print(f"    结果: {r2.stdout.strip()!r}")
    print_note("管道 = 前一个进程的 stdout → 后一个进程的 stdin")

    # 多级管道
    print(f"\n  {Color.COMMAND}echo -e 'a\\nb\\nab\\nabc' | grep ab | wc -l{Color.RESET}")
    r1 = subprocess.run(["echo", "a\nb\nab\nabc"], capture_output=True, text=True)
    r2 = subprocess.run(["grep", "ab"], input=r1.stdout, capture_output=True, text=True)
    r3 = subprocess.run(["wc", "-l"], input=r2.stdout, capture_output=True, text=True)
    print(f"    含 'ab' 的行数: {r3.stdout.strip()}")


def demo_4_merge_stderr():
    print_step(4, "2>&1 — 合并 stderr 到 stdout")
    print(f"  {Color.HIGHLIGHT}这就是 s01 Agent 的核心操作!{Color.RESET}")
    print()

    code = "import sys; sys.stdout.write('OK\\n'); sys.stderr.write('ERROR\\n')"

    # 不合并
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    print(f"  只读 stdout: {r.stdout.strip()!r}")
    print(f"  → 错过了 stderr 的报错信息!")
    print()

    # 合并
    r2 = subprocess.run(
        [sys.executable, "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    print(f"  合并后 (stderr→stdout): {r2.stdout.strip()!r}")
    print_key_point("Agent 用 subprocess.STDOUT 合并 → 模型看到完整输出")


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print_section("s26-03: 管道与重定向")

    demo_1_three_streams()
    demo_2_redirect()
    demo_3_pipe()
    demo_4_merge_stderr()

    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("小结:")
    print_key_point("  stdin(0) stdout(1) stderr(2) — 每个进程的三根管子")
    print_key_point("  > 覆盖  >> 追加  2> stderr重定向  2>&1 合并")
    print_key_point("  | 管道 = 传送带: A.stdout → B.stdin (并行运行)")
    print_key_point("  Agent 用 subprocess.STDOUT 合并 stdout+stderr")
