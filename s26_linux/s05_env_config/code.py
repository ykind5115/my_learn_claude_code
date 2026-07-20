#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s26-05: 环境变量与 Shell 配置 — env, export, source, .env

学习目标:
  - 理解环境变量的继承规则
  - 区分 export vs 普通赋值
  - 理解 .bashrc vs .profile vs .env

运行: python s26_linux/s05_env_config/code.py
"""

import os
import sys
import subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, print_step, print_note,
                   print_key_point, print_section, create_demo_dir, cleanup_demo_dir)


# ═══════════════════════════════════════════════════════════
def demo_1_current_env():
    print_step(1, "查看当前进程的环境变量")
    env_vars = ["HOME", "USER", "PATH", "SHELL", "PWD"]
    if sys.platform == "win32":
        env_vars = ["USERPROFILE", "USERNAME", "PATH", "COMSPEC"]

    for var in env_vars:
        val = os.environ.get(var, "(未设置)")
        if len(val) > 80:
            val = val[:77] + "..."
        print(f"  {Color.BOLD}{var:15s}{Color.RESET} = {Color.DIM}{val}{Color.RESET}")


def demo_2_inheritance():
    print_step(2, "环境变量继承")
    os.environ["S26_DEMO"] = "parent_value"

    code = "import os; print(os.environ.get('S26_DEMO', 'NOT_FOUND'))"

    # 继承所有环境变量
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True,
        env=os.environ.copy(),
    )
    print(f"  父进程: S26_DEMO=parent_value")
    print(f"  子进程 (继承全部): {r.stdout.strip()!r}")
    print_key_point("子进程继承了父进程的环境变量")

    # 不传环境变量
    r2 = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True,
        env={"PATH": os.environ["PATH"]},  # 只传 PATH
    )
    print(f"  子进程 (只传 PATH): {r2.stdout.strip()!r}")
    print_key_point("不传就看不到 → s01 的 subprocess 可以控制子进程的环境")

    # export vs 普通赋值
    print()
    print(f"  {Color.HIGHLIGHT}export vs 普通赋值:{Color.RESET}")
    print(f"    export VAR=val  → 当前进程 + 所有子进程可见")
    print(f"    VAR=val         → 只当前进程可见，子进程看不到")
    print_note("在 Python 里: os.environ['X']='y' 相当于 export X=y")

    del os.environ["S26_DEMO"]


def demo_3_dotenv():
    print_step(3, ".env 文件 — 应用程序约定")
    demo = create_demo_dir()

    env_file = demo / ".env"
    env_file.write_text("API_KEY=sk-ant-secret123\nMODEL=claude-sonnet-5\n")
    print(f"  .env 内容: {env_file.read_text().strip()}")
    print_note(".env 不是 Linux 原生的——是应用约定")

    # 手动模拟 load_dotenv
    env_vars = {}
    for line in env_file.read_text().strip().split("\n"):
        if "=" in line:
            k, v = line.split("=", 1)
            env_vars[k] = v
    print(f"  解析结果: {env_vars}")
    print_note("Python 中 pip install python-dotenv → load_dotenv() 自动完成")

    cleanup_demo_dir(demo)


def demo_4_config_files():
    print_step(4, "Shell 配置文件加载顺序")
    print(f"  登录 Shell:")
    print(f"    /etc/profile         → 全局系统配置")
    print(f"    ~/.bash_profile      → 用户登录配置")
    print(f"    ~/.bashrc            → (通常由 .bash_profile source)")
    print()
    print(f"  非登录 Shell (脚本、子进程):")
    print(f"    ~/.bashrc            → 每次打开都加载")
    print()
    print_key_point("配 alias 和 PATH → 写在 ~/.bashrc 里")
    print_key_point("配 Agent API Key → 写在 .env 里 (不进版本控制)")


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print_section("s26-05: 环境变量与 Shell 配置")

    demo_1_current_env()
    demo_2_inheritance()
    demo_3_dotenv()
    demo_4_config_files()

    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("小结:")
    print_key_point("  export = 当前进程 + 子进程都可见")
    print_key_point("  .env = 应用约定, load_dotenv() 读入 os.environ")
    print_key_point("  配 alias → ~/.bashrc, 配 API Key → .env")
