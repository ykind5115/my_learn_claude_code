#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s30_design_pattern 公共工具模块"""
import sys

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass


class Color:
    RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    RED = "\033[31m"; GREEN = "\033[32m"; YELLOW = "\033[33m"
    BLUE = "\033[34m"; MAGENTA = "\033[35m"; CYAN = "\033[36m"
    HEADER = "\033[1m\033[36m"; SUCCESS = "\033[32m"; WARNING = "\033[33m"
    ERROR = "\033[31m"; HIGHLIGHT = "\033[1m\033[35m"; COMMAND = "\033[2m\033[32m"


def print_step(num, title):
    print(f"\n{Color.HEADER}-- Step {num}: {title} --{Color.RESET}")

def print_note(text):
    print(f"  {Color.YELLOW}-> {text}{Color.RESET}")

def print_key_point(text):
    print(f"  {Color.HIGHLIGHT}* {text}{Color.RESET}")

def print_section(title):
    print(f"\n{Color.BOLD}{'='*60}{Color.RESET}")
    print(f"{Color.HEADER}{title}{Color.RESET}")
    print(f"{Color.BOLD}{'='*60}{Color.RESET}")

def print_agent_link(pattern, chapter, usage):
    print(f"  {Color.DIM}Agent: {pattern} -> {chapter} ({usage}){Color.RESET}")
