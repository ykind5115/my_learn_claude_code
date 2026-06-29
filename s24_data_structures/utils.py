#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s24_data_structures 公共工具模块

提供所有 code.py 共享的辅助功能：
  - ANSI 颜色输出
  - 性能计时
  - ASCII 树形图绘制
"""

import sys
import time
from functools import wraps


# ═══════════════════════════════════════════════════════════════
# Windows 终端编码处理
# ═══════════════════════════════════════════════════════════════
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════
# ANSI 颜色常量
# ═══════════════════════════════════════════════════════════════

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
    WHITE = "\033[37m"

    HEADER = BOLD + CYAN
    SUCCESS = GREEN
    WARNING = YELLOW
    ERROR = RED
    INFO = BLUE
    HIGHLIGHT = BOLD + MAGENTA


# ═══════════════════════════════════════════════════════════════
# 输出辅助
# ═══════════════════════════════════════════════════════════════

def print_header(title):
    """打印章节大标题"""
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  {title}{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")


def print_step(number, title):
    """打印步骤标题"""
    print(f"\n{Color.HEADER}{'─' * 50}{Color.RESET}")
    print(f"{Color.HEADER}  步骤 {number}: {title}{Color.RESET}")
    print(f"{Color.HEADER}{'─' * 50}{Color.RESET}\n")


def print_note(text):
    """打印注释"""
    print(f"  {Color.DIM}💡 {text}{Color.RESET}")


def print_key_point(text):
    """打印关键要点"""
    print(f"\n{Color.HIGHLIGHT}🔑 关键: {text}{Color.RESET}\n")


def print_warning(text):
    """打印警告"""
    print(f"  {Color.WARNING}⚠️  {text}{Color.RESET}")


def print_success(text):
    """打印成功信息"""
    print(f"  {Color.SUCCESS}✅ {text}{Color.RESET}")


def print_error(text):
    """打印错误信息"""
    print(f"  {Color.ERROR}✗ {text}{Color.RESET}")


# ═══════════════════════════════════════════════════════════════
# 性能计时
# ═══════════════════════════════════════════════════════════════

def time_it(func):
    """装饰器：打印函数执行时间"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"  {Color.DIM}[{func.__name__}] 耗时: {elapsed:.6f}s{Color.RESET}")
        return result
    return wrapper


def compare_performance(name1, time1, name2, time2):
    """对比两种实现的性能"""
    print(f"\n  {Color.HIGHLIGHT}性能对比:{Color.RESET}")
    print(f"    {name1}: {Color.DIM}{time1:.6f}s{Color.RESET}")
    print(f"    {name2}: {Color.DIM}{time2:.6f}s{Color.RESET}")
    if time1 > 0 and time2 > 0:
        ratio = max(time1, time2) / min(time1, time2)
        faster = name1 if time1 < time2 else name2
        print(f"    {Color.SUCCESS}{faster} 快 {ratio:.1f}x{Color.RESET}")
    print()


# ═══════════════════════════════════════════════════════════════
# ASCII 树形图绘制
# ═══════════════════════════════════════════════════════════════

def print_ascii_tree(root, get_children, get_label=str, indent=0, prefix=""):
    """
    通用 ASCII 树形图打印。

    参数:
        root: 根节点
        get_children: callable(node) → list of children
        get_label: callable(node) → str
        indent: 内部使用
        prefix: 内部使用
    """
    if root is None:
        print(f"{prefix}{Color.DIM}(空){Color.RESET}")
        return

    # 打印当前节点
    connector = "└── " if indent > 0 else ""
    print(f"{prefix}{connector}{Color.HIGHLIGHT}{get_label(root)}{Color.RESET}")

    children = get_children(root)
    if not children:
        return

    for i, child in enumerate(children):
        is_last = (i == len(children) - 1)
        if indent > 0:
            new_prefix = prefix.replace("├── ", "│   ").replace("└── ", "    ")
        else:
            new_prefix = ""
        new_prefix += ("    " if is_last else "│   ") if indent >= 0 else ""
        new_prefix = new_prefix if indent > 0 or i > 0 else ""

        child_prefix = ""
        parent_prefix = prefix.replace("├── ", "│   ").replace("└── ", "    ")
        child_prefix = parent_prefix + ("└── " if is_last else "├── ")

        print_ascii_tree(child, get_children, get_label, indent + 1, child_prefix)


def print_linked_list(head, get_next, get_label=str, max_nodes=20):
    """打印链表结构"""
    print(f"\n  {Color.HIGHLIGHT}链表结构:{Color.RESET}")
    current = head
    nodes = []
    count = 0
    while current and count < max_nodes:
        nodes.append(str(get_label(current)))
        current = get_next(current)
        count += 1
    if current:
        nodes.append("...")
    print(f"  {Color.HIGHLIGHT}{' → '.join(nodes)}{Color.RESET}\n")


def print_array_grid(items, cols=5, cell_width=12):
    """以网格形式打印数组元素"""
    for i, item in enumerate(items):
        if i > 0 and i % cols == 0:
            print()
        print(f"  {Color.DIM}[{i}]{Color.RESET} {str(item):<{cell_width}}", end="")
    print()
