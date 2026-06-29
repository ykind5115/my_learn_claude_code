#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s23_git 公共工具模块

提供所有 code.py 共享的辅助函数：
  - 在临时目录中创建演示用 Git 仓库
  - 执行 git 命令并捕获输出
  - 可视化「时间树」
  - 彩色终端输出
"""

import subprocess
import sys
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

# ═══════════════════════════════════════════════════════════════
# Windows 终端编码处理
# ═══════════════════════════════════════════════════════════════
# Windows 的终端默认使用 GBK 编码，无法输出 emoji 等 Unicode 字符。
# 在支持的情况下，强制使用 UTF-8。
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

    # 背景色
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"

    # 组合快捷方式
    HEADER = BOLD + CYAN
    SUCCESS = GREEN
    WARNING = YELLOW
    ERROR = RED
    INFO = BLUE
    HIGHLIGHT = BOLD + MAGENTA
    TREE = BOLD + YELLOW
    COMMAND = DIM + GREEN


# ═══════════════════════════════════════════════════════════════
# 核心函数
# ═══════════════════════════════════════════════════════════════

def run(cmd, cwd=None, check=True):
    """
    执行 shell 命令并返回 (returncode, stdout, stderr)。

    参数:
        cmd: 要执行的命令字符串
        cwd: 工作目录 (Path 或 str)
        check: 如果为 True，命令失败时打印警告但不中断
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if check and result.returncode != 0:
            print(f"{Color.WARNING}[!] 命令返回 {result.returncode}: {cmd}{Color.RESET}")
            if result.stderr:
                print(f"    {Color.DIM}{result.stderr.strip()}{Color.RESET}")
        return result
    except Exception as e:
        print(f"{Color.ERROR}[✗] 命令执行异常: {e}{Color.RESET}")
        raise


def run_git(git_cmd, cwd, check=True):
    """
    在指定目录执行 git 命令的快捷方式。

    用法:
        run_git("init", cwd)
        run_git('commit -m "hello"', cwd)
    """
    return run(f"git {git_cmd}", cwd=cwd, check=check)


def show_time_tree(cwd, title="当前时间树", show_all=True):
    """
    用 git log --graph 可视化时间树。

    这是整个 s23 模块最核心的可视化函数——
    每一步操作后都调用它，让学习者看到时间树的变化。

    参数:
        cwd: 仓库路径
        title: 打印的标题
        show_all: 是否包含所有分支（--all）
    """
    print(f"\n{Color.TREE}🌳 {title}{Color.RESET}")
    print(f"{Color.TREE}{'─' * 50}{Color.RESET}")

    cmd_parts = [
        "git log",
        "--graph",          # 画 ASCII 图
        "--oneline",        # 每个 commit 一行
        "--decorate",       # 显示分支名、HEAD、tag
        "--color=always",   # 保留颜色
    ]
    if show_all:
        cmd_parts.append("--all")

    cmd = " ".join(cmd_parts)
    result = run(cmd, cwd=cwd, check=False)

    if result.returncode == 0 and result.stdout.strip():
        print(result.stdout.strip())
    elif not result.stdout.strip():
        print(f"  {Color.DIM}(仓库还没有任何 commit){Color.RESET}")
    else:
        # 可能不是 git 仓库
        print(f"  {Color.DIM}(还不是 git 仓库或没有历史){Color.RESET}")

    print(f"{Color.TREE}{'─' * 50}{Color.RESET}\n")


def show_status(cwd, title="当前状态"):
    """显示 git status 的简要输出"""
    print(f"{Color.INFO}📋 {title}{Color.RESET}")
    result = run_git("status --short", cwd, check=False)
    if result.stdout.strip():
        print(result.stdout.strip())
    else:
        print(f"  {Color.DIM}(工作区干净，没有未提交的改动){Color.RESET}")
    print()


def print_step(number, title):
    """打印格式化的步骤标题"""
    print(f"\n{Color.HEADER}{'═' * 60}{Color.RESET}")
    print(f"{Color.HEADER}  第 {number} 步: {title}{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 60}{Color.RESET}\n")


def print_command(cmd, explanation=""):
    """打印即将执行的命令及解释"""
    print(f"{Color.COMMAND}$ {cmd}{Color.RESET}")
    if explanation:
        print(f"  {Color.DIM}→ {explanation}{Color.RESET}")


def print_note(text):
    """打印一条注释/提示"""
    print(f"  {Color.DIM}💡 {text}{Color.RESET}")


def print_key_point(text):
    """打印关键要点"""
    print(f"\n{Color.HIGHLIGHT}🔑 关键理解：{text}{Color.RESET}\n")


def create_demo_repo(parent_dir=None, name="demo-repo"):
    """
    创建一个干净的演示用 Git 仓库。

    返回临时目录的 Path 对象。
    调用者负责在演示结束后清理（调用 cleanup_demo_repo）。
    """
    if parent_dir is None:
        parent_dir = Path(tempfile.mkdtemp(prefix="s23git_"))
    else:
        parent_dir = Path(parent_dir)

    repo_path = Path(parent_dir) / name
    repo_path.mkdir(parents=True, exist_ok=True)

    run_git("init", repo_path)
    # 设置演示用的用户名和邮箱（避免首次使用时的配置提示）
    run_git('config user.name "s23-demo"', repo_path)
    run_git('config user.email "demo@s23-git.local"', repo_path)

    return repo_path


def write_file(repo_path, filename, content):
    """在仓库中写入一个文件（覆盖）"""
    filepath = Path(repo_path) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")
    return filepath


def append_file(repo_path, filename, content):
    """在仓库中追加内容到文件"""
    filepath = Path(repo_path) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content)
    return filepath


def commit(repo_path, message, filename="."):
    """快捷方式: add + commit"""
    run_git(f'add {filename}', repo_path)
    run_git(f'commit -m "{message}"', repo_path)
    print(f"  {Color.SUCCESS}✓ 已提交: {message}{Color.RESET}")


def cleanup_demo_repo(repo_path):
    """清理演示仓库（删除临时目录）"""
    try:
        shutil.rmtree(repo_path)
    except Exception:
        pass


def ask_keep(repo_path):
    """
    询问用户是否保留演示仓库以便自行探索。

    如果用户输入 y/yes，保留目录并打印路径。
    否则删除。
    """
    print(f"\n{Color.INFO}{'─' * 50}{Color.RESET}")
    try:
        answer = input(
            f"{Color.INFO}🔍 是否保留演示仓库以便自己探索？(y/N): {Color.RESET}"
        ).strip().lower()
    except (EOFError, KeyboardInterrupt):
        answer = "n"

    if answer in ("y", "yes"):
        print(f"\n{Color.SUCCESS}✅ 演示仓库已保留:{Color.RESET}")
        print(f"   {Color.HIGHLIGHT}{repo_path}{Color.RESET}")
        print(f"\n   {Color.DIM}cd {repo_path}{Color.RESET}")
        print(f"   {Color.DIM}git log --graph --all --oneline --decorate{Color.RESET}")
        print(f"\n   {Color.DIM}# 探索完后可手动删除:{Color.RESET}")
        print(f"   {Color.DIM}rm -rf {repo_path}{Color.RESET}")
    else:
        cleanup_demo_repo(repo_path.parent if repo_path.name != repo_path.parent.name else repo_path.parent)
        print(f"{Color.SUCCESS}✅ 演示仓库已清理{Color.RESET}")

    print()
