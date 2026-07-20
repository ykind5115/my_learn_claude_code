#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s26_linux 公共工具模块

提供所有 code.py 共享的辅助函数：
  - 执行 shell 命令并捕获输出
  - 彩色终端输出
  - 分步演示框架
"""

import subprocess
import sys
import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple

# ═══════════════════════════════════════════════════════════════
# Windows 终端编码处理
# ═══════════════════════════════════════════════════════════════
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════
# ANSI 颜色常量
# ═══════════════════════════════════════════════════════════════

class Color:
    """终端 ANSI 颜色代码"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # 组合快捷方式
    HEADER = BOLD + CYAN
    SUCCESS = GREEN
    WARNING = YELLOW
    ERROR = RED
    INFO = BLUE
    HIGHLIGHT = BOLD + MAGENTA
    COMMAND = DIM + GREEN
    FILE_PATH = BOLD + BLUE


# ═══════════════════════════════════════════════════════════════
# 核心函数
# ═══════════════════════════════════════════════════════════════

def run_cmd(cmd, cwd=None, timeout=10) -> Tuple[int, str, str]:
    """
    执行 shell 命令并返回 (returncode, stdout, stderr)。
    跨平台兼容：Windows 使用 shell=True + cmd.exe，
    Unix 使用 bash。
    """
    try:
        if sys.platform == "win32":
            r = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                cwd=str(cwd) if cwd else None,
                timeout=timeout,
                encoding="utf-8", errors="replace",
            )
        else:
            r = subprocess.run(
                ["/bin/bash", "-c", cmd],
                capture_output=True, text=True,
                cwd=str(cwd) if cwd else None,
                timeout=timeout,
            )
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except FileNotFoundError:
        return -2, "", "COMMAND_NOT_FOUND"


# ═══════════════════════════════════════════════════════════════
# 输出辅助函数
# ═══════════════════════════════════════════════════════════════

def print_step(num, title):
    """打印步骤标题"""
    print(f"\n{Color.BOLD}{Color.CYAN}── Step {num}: {title} ──{Color.RESET}")

def print_command(cmd):
    """打印执行的命令"""
    print(f"  {Color.COMMAND}$ {cmd}{Color.RESET}")

def print_result(text):
    """打印命令结果"""
    for line in text.strip().split("\n"):
        print(f"  {Color.DIM}{line}{Color.RESET}")

def print_note(text):
    """打印注释"""
    print(f"  {Color.YELLOW}→ {text}{Color.RESET}")

def print_key_point(text):
    """打印关键要点"""
    print(f"  {Color.HIGHLIGHT}◆ {text}{Color.RESET}")

def print_section(title):
    """打印大节标题"""
    print(f"\n{Color.BOLD}{'='*60}{Color.RESET}")
    print(f"{Color.HEADER}{title}{Color.RESET}")
    print(f"{Color.BOLD}{'='*60}{Color.RESET}")

def print_demo_title(title):
    """打印演示标题"""
    print(f"\n{Color.BOLD}{Color.YELLOW}{'▸' * 30}{Color.RESET}")
    print(f"{Color.BOLD}{Color.YELLOW}  {title}{Color.RESET}")
    print(f"{Color.BOLD}{Color.YELLOW}{'▸' * 30}{Color.RESET}")


# ═══════════════════════════════════════════════════════════════
# 工作区辅助
# ═══════════════════════════════════════════════════════════════

def create_demo_dir() -> Path:
    """在临时目录创建演示工作区"""
    demo = Path(tempfile.mkdtemp(prefix="s26_demo_"))
    print_note(f"演示工作区: {demo}")
    return demo

def cleanup_demo_dir(demo_dir: Path):
    """清理演示工作区"""
    import shutil
    if demo_dir.exists():
        shutil.rmtree(demo_dir, ignore_errors=True)
        print_note(f"已清理: {demo_dir}")


# ═══════════════════════════════════════════════════════════════
# 平台检测
# ═══════════════════════════════════════════════════════════════

def is_unix() -> bool:
    """是否在真正的 Unix/Linux/macOS 环境"""
    return sys.platform != "win32"

def is_wsl() -> bool:
    """是否在 WSL 环境"""
    if sys.platform != "win32":
        return False
    try:
        r = subprocess.run(["wsl", "--status"], capture_output=True, text=True)
        return r.returncode == 0
    except Exception:
        return False

def platform_note():
    """打印平台兼容性说明"""
    if sys.platform == "win32":
        print_note("运行在 Windows (Git Bash)。部分命令行为可能略有不同。")
    else:
        print_note(f"运行在 {sys.platform}")
