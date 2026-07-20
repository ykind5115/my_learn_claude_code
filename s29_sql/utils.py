#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s29_sql 公共工具模块"""

import sqlite3, sys

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
    SQL = "\033[1m\033[33m"


def get_db(memory=True, path=None):
    """获取 SQLite 连接（默认内存数据库）"""
    if memory:
        conn = sqlite3.connect(":memory:")
    else:
        conn = sqlite3.connect(path or ":memory:")
    conn.row_factory = sqlite3.Row  # 让结果可以用列名访问
    return conn


def run_sql(conn, sql, params=None):
    """执行 SQL 并返回结果列表"""
    cur = conn.cursor()
    if params:
        cur.execute(sql, params)
    else:
        cur.execute(sql)
    return cur.fetchall()


def print_step(num, title):
    print(f"\n{Color.HEADER}-- Step {num}: {title} --{Color.RESET}")

def print_sql(sql):
    for line in sql.strip().split("\n"):
        print(f"  {Color.SQL}{line.strip()}{Color.RESET}")

def print_table(rows, max_rows=10):
    """打印查询结果表格"""
    if not rows:
        print(f"  {Color.DIM}(empty){Color.RESET}")
        return
    keys = rows[0].keys()
    col_widths = [max(len(str(k)), max(len(str(r[k])) for r in rows[:max_rows])) for k in keys]
    header = " | ".join(f"{Color.BOLD}{k:<{w}}{Color.RESET}" for k, w in zip(keys, col_widths))
    print(f"  {header}")
    print(f"  {Color.DIM}{'-'*len(header.replace(chr(27),'')*2)}{Color.RESET}")
    for row in rows[:max_rows]:
        vals = " | ".join(f"{str(row[k]):<{w}}" for k, w in zip(keys, col_widths))
        print(f"  {vals}")
    if len(rows) > max_rows:
        print(f"  {Color.DIM}... ({len(rows)} rows total){Color.RESET}")

def print_note(text):
    print(f"  {Color.YELLOW}-> {text}{Color.RESET}")

def print_key_point(text):
    print(f"  {Color.HIGHLIGHT}* {text}{Color.RESET}")

def print_section(title):
    print(f"\n{Color.BOLD}{'='*60}{Color.RESET}")
    print(f"{Color.HEADER}{title}{Color.RESET}")
    print(f"{Color.BOLD}{'='*60}{Color.RESET}")
