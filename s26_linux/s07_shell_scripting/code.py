#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s26-07: Shell 脚本 — 变量, 条件, 循环, 函数, shebang

学习目标:
  - 写一个完整的 shell 脚本
  - 理解变量、条件、循环
  - 理解退出码和 $?

运行: python s26_linux/s07_shell_scripting/code.py
"""

import os
import sys
import stat
import subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, print_step, print_note,
                   print_key_point, print_section, create_demo_dir, cleanup_demo_dir)


# ═══════════════════════════════════════════════════════════
def demo_1_first_script():
    print_step(1, "第一个 Shell 脚本")
    demo = create_demo_dir()

    script = demo / "hello.sh"
    script.write_text("""#!/bin/bash
# 我的第一个脚本
NAME="Linux Learner"
echo "Hello, $NAME!"
echo "当前目录: $(pwd)"
echo "Python 版本: $(python --version 2>&1)"
""")
    # 加执行权限
    script.chmod(script.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    print(f"  脚本内容:")
    for line in script.read_text().strip().split("\n"):
        print(f"    {Color.DIM}{line}{Color.RESET}")

    # 执行
    r = subprocess.run(["bash", str(script)], capture_output=True, text=True)
    print(f"\n  执行结果:")
    for line in r.stdout.strip().split("\n"):
        print(f"    {Color.SUCCESS}{line}{Color.RESET}")

    cleanup_demo_dir(demo)


def demo_2_variables():
    print_step(2, "变量")
    demo = create_demo_dir()

    script = demo / "vars.sh"
    script.write_text("""#!/bin/bash
# 赋值不能有空格!
NAME="world"
echo "Hello, $NAME"
echo "Hello, ${NAME}"   # 花括号明确边界

# 命令替换
NOW=$(date)
echo "现在: $NOW"

# 特殊变量
echo "脚本名: $0"
echo "第一个参数: ${1:-无}"
echo "参数个数: $#"
echo "退出码(上一条命令): $?"
""")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)

    r = subprocess.run(["bash", str(script), "arg1"], capture_output=True, text=True)
    print(f"  变量演示:")
    for line in r.stdout.strip().split("\n"):
        print(f"    {line}")

    cleanup_demo_dir(demo)


def demo_3_conditions_and_loops():
    print_step(3, "条件和循环")
    demo = create_demo_dir()

    script = demo / "control.sh"
    script.write_text("""#!/bin/bash
# 条件判断
FILE="/etc/hosts"
if [ -f "$FILE" ]; then
    echo "[OK] $FILE 存在"
else
    echo "[--] $FILE 不存在"
fi

# 循环遍历
echo ""
echo "当前目录的 Python 文件:"
for f in *.py; do
    [ -f "$f" ] && echo "  [file] $f"
done

# 计数器循环
echo ""
echo "计数:"
for i in 1 2 3 4 5; do
    echo -n "$i "
done
echo ""
""")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)

    r = subprocess.run(
        ["bash", str(script)],
        capture_output=True, text=True,
        cwd=str(demo),
    )
    print(f"  执行结果:")
    for line in r.stdout.strip().split("\n"):
        print(f"    {line}")

    cleanup_demo_dir(demo)


def demo_4_exit_codes():
    print_step(4, "退出码和 $?")

    code = "exit 0"
    r = subprocess.run(["bash", "-c", code], capture_output=True, text=True)
    print(f"  exit 0 → 退出码 {r.returncode} (成功)")

    code = "exit 1"
    r = subprocess.run(["bash", "-c", code], capture_output=True, text=True)
    print(f"  exit 1 → 退出码 {r.returncode} (失败)")

    # && 和 || 的短路
    print(f"\n  && (前成功才跑后):  true && echo '跑了' → ", end="")
    r = subprocess.run(["bash", "-c", "true && echo '跑了'"], capture_output=True, text=True)
    print(f"{r.stdout.strip()!r}")

    print(f"  || (前失败才跑后):  false || echo '跑了' → ", end="")
    r = subprocess.run(["bash", "-c", "false || echo '跑了'"], capture_output=True, text=True)
    print(f"{r.stdout.strip()!r}")

    print_key_point("Agent 用退出码判断工具执行成功/失败")


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print_section("s26-07: Shell 脚本")

    demo_1_first_script()
    demo_2_variables()
    demo_3_conditions_and_loops()
    demo_4_exit_codes()

    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("小结:")
    print_key_point("  #!/bin/bash = shebang, $VAR = 变量, $? = 退出码")
    print_key_point("  if [ -f file ]; then ... fi = 条件判断")
    print_key_point("  for f in *.py; do ... done = 循环")
    print_key_point("  && (前成功才跑后)  || (前失败才跑后)")
