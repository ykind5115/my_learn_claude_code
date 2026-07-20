#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s27_network 公共工具模块
"""

import subprocess
import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    HEADER = "\033[1m\033[36m"
    SUCCESS = "\033[32m"
    WARNING = "\033[33m"
    ERROR = "\033[31m"
    INFO = "\033[34m"
    HIGHLIGHT = "\033[1m\033[35m"
    COMMAND = "\033[2m\033[32m"


def run_cmd(cmd, timeout=10):
    """执行命令返回 (returncode, stdout, stderr)"""
    try:
        if sys.platform == "win32":
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                             timeout=timeout, encoding="utf-8", errors="replace")
        else:
            r = subprocess.run(["bash", "-c", cmd], capture_output=True,
                             text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"


def print_step(num, title):
    print(f"\n{Color.HEADER}── Step {num}: {title} ──{Color.RESET}")

def print_command(cmd):
    print(f"  {Color.COMMAND}$ {cmd}{Color.RESET}")

def print_note(text):
    print(f"  {Color.YELLOW}→ {text}{Color.RESET}")

def print_key_point(text):
    print(f"  {Color.HIGHLIGHT}◆ {text}{Color.RESET}")

def print_section(title):
    print(f"\n{Color.BOLD}{'='*60}{Color.RESET}")
    print(f"{Color.HEADER}{title}{Color.RESET}")
    print(f"{Color.BOLD}{'='*60}{Color.RESET}")

def print_data(title, data):
    """以 hex + ascii 格式打印数据"""
    print(f"  {Color.INFO}{title}:{Color.RESET}")
    if isinstance(data, bytes):
        hex_str = " ".join(f"{b:02x}" for b in data[:40])
        ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in data[:40])
        print(f"    hex:  {hex_str}")
        print(f"    ascii: {ascii_str}")
        if len(data) > 40:
            print(f"    ... ({len(data)} bytes total)")
    else:
        print(f"    {data}")
