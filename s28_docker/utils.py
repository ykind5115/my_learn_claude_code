#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s28_docker 公共工具模块"""

import subprocess, sys, os, shutil, tempfile
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class Color:
    RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    RED = "\033[31m"; GREEN = "\033[32m"; YELLOW = "\033[33m"
    BLUE = "\033[34m"; MAGENTA = "\033[35m"; CYAN = "\033[36m"
    HEADER = "\033[1m\033[36m"; SUCCESS = "\033[32m"; WARNING = "\033[33m"
    ERROR = "\033[31m"; HIGHLIGHT = "\033[1m\033[35m"; COMMAND = "\033[2m\033[32m"


def docker_available():
    """检查 Docker 是否可用"""
    return shutil.which("docker") is not None


def run_docker(args, timeout=30):
    """运行 docker 命令，返回 (returncode, stdout, stderr)"""
    cmd = ["docker"] + args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except FileNotFoundError:
        return -2, "", "DOCKER_NOT_FOUND"


def print_step(num, title):
    print(f"\n{Color.HEADER}── Step {num}: {title} ──{Color.RESET}")

def print_command(cmd):
    print(f"  {Color.COMMAND}$ {cmd}{Color.RESET}")

def print_output(text, max_lines=10):
    lines = text.strip().split("\n")
    for line in lines[:max_lines]:
        print(f"  {Color.DIM}{line}{Color.RESET}")
    if len(lines) > max_lines:
        print(f"  {Color.DIM}... ({len(lines)} lines total){Color.RESET}")

def print_note(text):
    print(f"  {Color.YELLOW}-> {text}{Color.RESET}")

def print_key_point(text):
    print(f"  {Color.HIGHLIGHT}* {text}{Color.RESET}")

def print_section(title):
    print(f"\n{Color.BOLD}{'='*60}{Color.RESET}")
    print(f"{Color.HEADER}{title}{Color.RESET}")
    print(f"{Color.BOLD}{'='*60}{Color.RESET}")

def print_docker_warning():
    print(f"\n  {Color.WARNING}[!] Docker 未安装或未启动{Color.RESET}")
    print(f"  {Color.DIM}请先安装 Docker Desktop 然后重新运行{Color.RESET}")
    print(f"  {Color.DIM}https://docs.docker.com/get-docker/{Color.RESET}")
