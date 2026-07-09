#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s25_redis 公共工具模块

提供所有 code.py 共享的辅助函数：
  - 连接本地 Redis
  - 可视化「共享黑板」状态
  - 彩色终端输出
  - 演示辅助函数
"""

import sys
import os
from typing import Optional, Any

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

    # 背景色
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"

    # 组合快捷方式
    HEADER = BOLD + CYAN
    SUCCESS = GREEN
    WARNING = YELLOW
    ERROR = RED
    INFO = BLUE
    HIGHLIGHT = BOLD + MAGENTA
    BOARD = BOLD + GREEN
    COMMAND = DIM + GREEN


# ═══════════════════════════════════════════════════════════════
# Redis 连接管理
# ═══════════════════════════════════════════════════════════════

def get_redis_client():
    """
    获取 Redis 客户端连接。

    优先使用环境变量 REDIS_URL，否则连接本地默认 6379。
    如果 redis 模块未安装，打印安装提示。
    """
    try:
        import redis
    except ImportError:
        print(f"{Color.ERROR}[✗] 未安装 redis 模块{Color.RESET}")
        print(f"   {Color.DIM}请运行: pip install redis{Color.RESET}")
        sys.exit(1)

    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    try:
        client = redis.Redis.from_url(redis_url, decode_responses=True)
        client.ping()
        return client
    except redis.ConnectionError:
        print(f"{Color.ERROR}[✗] 无法连接到 Redis: {redis_url}{Color.RESET}")
        print(f"   {Color.DIM}请确认 Redis 已启动。Docker 快速启动:{Color.RESET}")
        print(f"   {Color.DIM}  docker run -d --name redis-demo -p 6379:6379 redis:7-alpine{Color.RESET}")
        sys.exit(1)


def get_raw_client():
    """获取 decode_responses=False 的客户端（用于查看底层编码）"""
    try:
        import redis
    except ImportError:
        print(f"{Color.ERROR}[✗] 未安装 redis 模块{Color.RESET}")
        sys.exit(1)

    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    try:
        client = redis.Redis.from_url(redis_url, decode_responses=False)
        client.ping()
        return client
    except redis.ConnectionError:
        print(f"{Color.ERROR}[✗] 无法连接到 Redis{Color.RESET}")
        sys.exit(1)


# ═══════════════════════════════════════════════════════════════
# 黑板可视化（核心函数）
# ═══════════════════════════════════════════════════════════════

def show_blackboard(client, title: str = "当前黑板", pattern: str = "*"):
    """
    可视化 Redis 黑板状态 — 扫描所有匹配的 key 并打印类型和值。

    这是整个 s25 模块最核心的可视化函数——
    每一步操作后都调用它，让学习者看到黑板的变化。

    参数:
        client: Redis 客户端
        title: 打印的标题
        pattern: key 匹配模式（默认 * 表示所有）
    """
    print(f"\n{Color.BOARD}📋 {title}{Color.RESET}")
    print(f"{Color.BOARD}{'─' * 55}{Color.RESET}")

    try:
        keys = sorted(client.keys(pattern))
    except Exception:
        keys = []

    if not keys:
        print(f"  {Color.DIM}(黑板上什么也没有 — 一片空白){Color.RESET}")
    else:
        print(f"  {Color.DIM}{'KEY':<24} {'TYPE':<10} VALUE{Color.RESET}")
        print(f"  {Color.DIM}{'─' * 55}{Color.RESET}")
        for key in keys:
            key_type = client.type(key)
            value = _get_value_preview(client, key, key_type)
            ttl = client.ttl(key)
            ttl_str = f"  {Color.DIM}(TTL: {ttl}s){Color.RESET}" if ttl > 0 else ""

            print(f"  {Color.YELLOW}{key:<24}{Color.RESET} "
                  f"{Color.CYAN}{key_type:<10}{Color.RESET} "
                  f"{value}{ttl_str}")

    print(f"{Color.BOARD}{'─' * 55}{Color.RESET}\n")


def _get_value_preview(client, key: str, key_type: str) -> str:
    """根据 key 类型返回值的简要预览"""
    try:
        if key_type == "string":
            val = client.get(key)
            if val is None:
                return f"{Color.DIM}(nil){Color.RESET}"
            return f'"{val}"' if len(str(val)) <= 30 else f'"{str(val)[:30]}..."'
        elif key_type == "list":
            length = client.llen(key)
            items = client.lrange(key, 0, 2)
            preview = ", ".join(f'"{x}"' for x in items)
            return f"[{preview}{'...' if length > 3 else ''}] ({length} items)"
        elif key_type == "hash":
            length = client.hlen(key)
            items = client.hgetall(key)
            preview = ", ".join(f"{k}: {v}" for k, v in list(items.items())[:3])
            return f"{{{preview}{'...' if length > 3 else ''}}} ({length} fields)"
        elif key_type == "set":
            length = client.scard(key)
            items = list(client.smembers(key))[:3]
            preview = ", ".join(f'"{x}"' for x in items)
            return f"{{{preview}{'...' if length > 3 else ''}}} ({length} members)"
        elif key_type == "zset":
            length = client.zcard(key)
            items = client.zrange(key, 0, 2, withscores=True)
            preview = ", ".join(f"{m}: {s}" for m, s in items)
            return f"[{preview}{'...' if length > 3 else ''}] ({length} members)"
        elif key_type == "stream":
            length = client.xlen(key)
            return f"(stream, {length} entries)"
        elif key_type == "none":
            return f"{Color.DIM}(expired / deleted){Color.RESET}"
        else:
            return f"({key_type})"
    except Exception as e:
        return f"{Color.ERROR}(error: {e}){Color.RESET}"


def show_key_detail(client, key: str):
    """展示一个 key 的详细信息"""
    key_type = client.type(key)
    if key_type == "none":
        print(f"  {Color.DIM}key '{key}' 不存在或已过期{Color.RESET}")
        return

    ttl = client.ttl(key)
    print(f"\n  {Color.HIGHLIGHT}🔍 {key}{Color.RESET}  ({Color.CYAN}{key_type}{Color.RESET})"
          f"  TTL: {Color.YELLOW}{ttl}s{Color.RESET}")

    if key_type == "string":
        print(f"  value: \"{client.get(key)}\"")
        print(f"  strlen: {client.strlen(key)}")
    elif key_type == "list":
        print(f"  length: {client.llen(key)}")
        print(f"  all: {client.lrange(key, 0, -1)}")
    elif key_type == "hash":
        print(f"  all: {client.hgetall(key)}")
    elif key_type == "set":
        print(f"  members: {client.smembers(key)}")
    elif key_type == "zset":
        print(f"  all (with scores): {client.zrange(key, 0, -1, withscores=True)}")


# ═══════════════════════════════════════════════════════════════
# 输出辅助函数
# ═══════════════════════════════════════════════════════════════

def print_step(number: int, title: str):
    """打印格式化的步骤标题"""
    print(f"\n{Color.HEADER}{'═' * 60}{Color.RESET}")
    print(f"{Color.HEADER}  第 {number} 步: {title}{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 60}{Color.RESET}\n")


def print_command(cmd: str, explanation: str = ""):
    """打印即将执行的 Redis 命令及解释"""
    print(f"{Color.COMMAND}> {cmd}{Color.RESET}")
    if explanation:
        print(f"  {Color.DIM}→ {explanation}{Color.RESET}")


def print_note(text: str):
    """打印一条注释/提示"""
    print(f"  {Color.DIM}💡 {text}{Color.RESET}")


def print_key_point(text: str):
    """打印关键要点"""
    print(f"\n{Color.HIGHLIGHT}🔑 关键理解：{text}{Color.RESET}\n")


def print_result(result: Any, label: str = ""):
    """打印命令执行结果"""
    prefix = f"{label} = " if label else ""
    if result is None:
        print(f"  → {prefix}{Color.DIM}(nil){Color.RESET}")
    elif isinstance(result, bool):
        print(f"  → {prefix}{Color.SUCCESS if result else Color.WARNING}{result}{Color.RESET}")
    elif isinstance(result, (int, float)):
        print(f"  → {prefix}{Color.HIGHLIGHT}{result}{Color.RESET}")
    else:
        print(f"  → {prefix}{Color.SUCCESS}{result}{Color.RESET}")


def section(title: str):
    """打印章内小节标题"""
    print(f"\n{Color.INFO}{'─' * 50}{Color.RESET}")
    print(f"{Color.INFO}  {title}{Color.RESET}")
    print(f"{Color.INFO}{'─' * 50}{Color.RESET}")


# ═══════════════════════════════════════════════════════════════
# 演示辅助函数
# ═══════════════════════════════════════════════════════════════

def flush_db(client):
    """
    清空当前数据库（仅限演示用）。

    会先打印警告并确认——防止误操作生产环境。
    """
    db = client.connection_pool.connection_kwargs.get("db", 0)
    print(f"\n{Color.WARNING}⚠ 即将清空数据库 db{db} 的所有数据{Color.RESET}")
    try:
        ans = input(f"{Color.WARNING}  确认? (y/N): {Color.RESET}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        ans = "n"

    if ans in ("y", "yes"):
        client.flushdb()
        print(f"  {Color.SUCCESS}✅ 数据库已清空{Color.RESET}")
    else:
        print(f"  {Color.DIM}已取消，数据保留{Color.RESET}")
    print()


def cleanup_demo_keys(client, pattern: str = "demo:*"):
    """清理演示用的 key"""
    keys = client.keys(pattern)
    if keys:
        client.delete(*keys)
        print(f"  {Color.DIM}已清理 {len(keys)} 个演示 key ({pattern}){Color.RESET}")
