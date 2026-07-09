#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s13: 主从复制 — 多块黑板同步

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - 主从复制解决了什么问题？
  - 全量同步和增量同步有什么区别？
  - REPLICAOF、INFO REPLICATION 怎么用？
  - replication backlog 的作用是什么？
  - 读写分离怎么配置？有什么陷阱？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s13_replication/code.py
"""

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from s25_redis.utils import (
    Color,
    get_redis_client,
    print_step,
    print_command,
    print_note,
    print_key_point,
    print_result,
    section,
    cleanup_demo_keys,
)


def show_replication_info(client):
    """获取并展示 INFO REPLICATION 信息"""
    info = client.info("replication")
    if not info:
        print(f"  {Color.DIM}(无法获取复制信息){Color.RESET}")
        return

    print(f"\n  {Color.HEADER}INFO REPLICATION 输出:{Color.RESET}")
    print(f"  {Color.DIM}{'─' * 45}{Color.RESET}")

    role = info.get("role", "unknown")
    print(f"  {Color.HIGHLIGHT}role{Color.RESET}: {Color.YELLOW}{role}{Color.RESET}")

    if role == "master":
        slaves = info.get("connected_slaves", 0)
        print(f"  {Color.HIGHLIGHT}connected_slaves{Color.RESET}: {Color.SUCCESS}{slaves}{Color.RESET}")
        for i in range(slaves):
            slave_key = f"slave{i}"
            slave_info = info.get(slave_key, "")
            print(f"  {Color.HIGHLIGHT}{slave_key}{Color.RESET}: {Color.DIM}{slave_info}{Color.RESET}")

        repl_offset = info.get("master_repl_offset", 0)
        print(f"  {Color.HIGHLIGHT}master_repl_offset{Color.RESET}: {repl_offset}")

        backlog_active = info.get("repl_backlog_active", 0)
        backlog_size = info.get("repl_backlog_size", 0)
        print(f"  {Color.HIGHLIGHT}repl_backlog_active{Color.RESET}: {Color.SUCCESS if backlog_active else Color.WARNING}{backlog_active}{Color.RESET}")
        if backlog_active:
            print(f"  {Color.HIGHLIGHT}repl_backlog_size{Color.RESET}: {backlog_size}")

    elif role == "slave":
        master_host = info.get("master_host", "")
        master_port = info.get("master_port", 0)
        link_status = info.get("master_link_status", "")
        offset = info.get("slave_repl_offset", 0)
        lag = info.get("master_last_io_seconds_ago", -1)

        link_color = Color.SUCCESS if link_status == "up" else Color.ERROR
        print(f"  {Color.HIGHLIGHT}master_host{Color.RESET}: {master_host}:{master_port}")
        print(f"  {Color.HIGHLIGHT}master_link_status{Color.RESET}: {link_color}{link_status}{Color.RESET}")
        print(f"  {Color.HIGHLIGHT}slave_repl_offset{Color.RESET}: {offset}")
        print(f"  {Color.HIGHLIGHT}master_last_io_seconds_ago{Color.RESET}: {lag}s")

    print(f"  {Color.DIM}{'─' * 45}{Color.RESET}\n")


def print_config_setup():
    """打印主从配置示例"""
    section("REPLICAOF 配置示例")

    print(f"""
{Color.COMMAND}# 方法一：配置文件（redis.conf）{Color.RESET}
  在从节点的 redis.conf 中写入：
    replicaof 192.168.1.10 6379
    replica-read-only yes

{Color.COMMAND}# 方法二：命令行（运行时生效，重启后丢失）{Color.RESET}
  redis-cli> REPLICAOF 192.168.1.10 6379

{Color.COMMAND}# 取消复制{Color.RESET}
  redis-cli> REPLICAOF NO ONE

{Color.COMMAND}# 查看复制状态{Color.RESET}
  redis-cli> INFO REPLICATION
""")


def print_fullsync_diagram():
    """打印全量同步过程的 ASCII 图解"""
    section("全量同步过程图解")
    print(f"""
{Color.YELLOW}  ┌─────────────────────────────────────────────────────┐
  │                   全量同步                      │
  ├─────────────────────────────────────────────────────┤
  │                                                     │
  │  从节点                     主节点                   │
  │    │                          │                      │
  │    │  1. REPLICAOF 127.0.0.1:6379                    │
  │    │─────────────────────────→│                      │
  │    │                          │                      │
  │    │  2. PSYNC ? -1           │  ← "我没有任何数据"    │
  │    │─────────────────────────→│                      │
  │    │                          │                      │
  │    │                          │  3. BGSAVE           │
  │    │                          │     生成 RDB 快照     │
  │    │                          │     同时写 buffer     │
  │    │                          │                      │
  │    │  4. RDB 文件传输         │                      │
  │    │←─────────────────────────│                      │
  │    │                          │                      │
  │    │  5. 清空自己 + 载入 RDB  │                      │
  │    │                          │                      │
  │    │  6. buffer 增量命令      │                      │
  │    │←─────────────────────────│                      │
  │    │                          │                      │
  │    ▼                          ▼                      │
  │  数据一致！                  继续服务                  │
  │                                                     │
  └─────────────────────────────────────────────────────┘{Color.RESET}
""")

    print_key_point(
        "全量同步的核心思想：\n"
        "    「从节点什么都没有 → 主节点拍快照 → 传过去 → 补增量」\n"
        "    代价很大（CPU、内存、网络），所以尽量用增量同步。"
    )


def print_backlog_diagram():
    """打印 replication backlog 环形缓冲区图解"""
    section("replication backlog — 环形缓冲区")

    print(f"""
{Color.YELLOW}  写方向 ◀─── ◀─── ◀─── ◀─── ◀───
      ┌───┬───┬───┬───┬───┬───┬───┬───┐
      │ A │ B │ C │ D │ E │ F │ G │   │
      └───┴───┴───┴───┴───┴───┴───┴───┘
      ▲           ▲               ▲
      │           │               └── 主节点当前位置 (offset=7)
      │           └── 从节点曾在此 (offset=4)
      └── 最早可追到的位置 (offset=1){Color.RESET}
""")

    print_note("backlog 是环形缓冲区，新数据会覆盖旧数据。")
    print_note("默认大小 1MB，可用 repl-backlog-size 调整。")
    print("")
    print(f"  {Color.CYAN}增量同步流程：{Color.RESET}")
    print(f"    从节点重连 → PSYNC replid offset")
    print(f"      ├── offset 在 backlog 范围内 → 增量同步 ✅")
    print(f"      └── offset 已过期             → 全量同步 🔄")
    print("")

    print_key_point(
        "如何确定 backlog 大小？\n"
        "    按「主节点峰值写入速度 × 可接受的最大断连时间」估算。\n"
        "    比如每秒 10KB 写入，允许断连 5 分钟：\n"
        "    10KB × 300s = 3MB → 设置 repl-backlog-size 3mb"
    )


def print_read_write_split():
    """打印读写分离架构说明"""
    section("读写分离架构图")

    print(f"""
{Color.YELLOW}  客户端（应用层）
        │
        ├── 写操作 ──────→  主节点 (192.168.1.10:6379)
        │                      SET / DEL / INCR / ...
        │
        └── 读操作 ──────→  从节点 1 (192.168.1.11:6379)
                        └── 从节点 2 (192.168.1.12:6379)
                              GET / EXISTS / LRANGE / ...{Color.RESET}
""")

    print_key_point(
        "读写分离的陷阱 — 主从延迟：\n"
        "    写入主节点后立即读从节点，可能读到旧数据。\n"
        "    对一致性要求高的操作，强制走主节点读。"
    )


def print_warning_diagram():
    """打印主节点挂了没人自动切的警告"""
    section("⚠ 主从复制的一个重要限制")

    print(f"""
{Color.YELLOW}  主节点挂了 → 需要人工操作：

    1. 发现主节点挂了  (人工监控 or 监控报警)
    2. 选一个从节点     (人工判断哪个从节点数据最新)
    3. 升它为主         REPLICAOF NO ONE
    4. 改其他从指向新主  REPLICAOF new-master 6379
    5. 通知客户端更新配置 (或者改 DNS)

    整个过程：可能需要几分钟甚至更久。
    这期间：写服务不可用。{Color.RESET}
""")

    print_note("主从复制只解决「数据冗余」，不解决「故障自动转移」。")
    print_note("下一章（s14 — Sentinel）会让这个过程完全自动化。")


def print_common_mistakes():
    """打印常见错误"""
    section("常见错误")

    errors = [
        ("从节点上有过期键",
         "从节点不主动删除过期键，依赖主节点的 DEL 命令同步。\n"
         "    如果主节点忙，从节点上可能读到本该过期的数据。"),
        ("主从延迟导致读到旧数据",
         "写后立即读从节点 = 可能读到旧值。\n"
         "    对策：强一致操作走主节点读。"),
        ("从节点可写（replica-read-only no）",
         "从节点写入不会同步给主节点 → 数据不一致。\n"
         "    默认是只读的，不要修改这个配置。"),
        ("一台从节点连多个主",
         "REPLICAOF 会覆盖之前的配置，一个从只能有一个主。"),
    ]

    for title, desc in errors:
        print(f"  {Color.ERROR}❌ {title}{Color.RESET}")
        print(f"    {Color.DIM}{desc}{Color.RESET}")
        print("")


def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s13: 主从复制 — 多块黑板同步{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: 连接 Redis，检查复制状态
    # ═══════════════════════════════════════════════════════════
    print_step(1, "连接 Redis — 查看当前复制状态")

    client = None
    try:
        client = get_redis_client()
    except SystemExit:
        pass  # Redis 不可用，降级到纯概念模式

    if client is not None:
        print(f"  {Color.SUCCESS}✅ Redis 已连接{Color.RESET}")

        try:
            show_replication_info(client)
        except Exception as e:
            print(f"  {Color.WARNING}⚠ 获取复制信息时出错: {e}{Color.RESET}")

        # 查看复制相关配置
        section("复制相关配置")

        for cfg_key, cfg_label in [
            ("repl-backlog-size", "backlog 大小"),
            ("replica-read-only", "从节点只读"),
            ("repl-timeout", "复制超时(秒)"),
        ]:
            try:
                cfg = client.config_get(cfg_key)
                if cfg:
                    print_command(f"CONFIG GET {cfg_key}")
                    print_result(cfg.get(cfg_key, "unknown"), cfg_label)
            except Exception as e:
                print(f"  {Color.WARNING}⚠ 读取 {cfg_key} 失败: {e}{Color.RESET}")
    else:
        print(f"  {Color.WARNING}⚠ 无法连接到 Redis，将以纯概念模式运行{Color.RESET}")
        print(f"  {Color.DIM}  部分命令演示将使用模拟输出{Color.RESET}\n")
        # 展示模拟的 INFO REPLICATION 输出
        print(f"\n  {Color.HEADER}模拟 INFO REPLICATION 输出（主节点视角）:{Color.RESET}")
        print(f"  {Color.DIM}{'─' * 45}{Color.RESET}")
        print(f"  role: master")
        print(f"  connected_slaves: 2")
        print(f"  slave0: ip=192.168.1.11,port=6379,state=online,offset=12345")
        print(f"  slave1: ip=192.168.1.12,port=6379,state=online,offset=12345")
        print(f"  master_repl_offset: 12345")
        print(f"  repl_backlog_active: 1")
        print(f"  repl_backlog_size: 1048576")
        print(f"  repl_backlog_histlen: 12345")
        print(f"  {Color.DIM}{'─' * 45}{Color.RESET}\n")

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: 配置主从关系
    # ═══════════════════════════════════════════════════════════
    print_step(2, "配置主从关系 — REPLICAOF 命令")

    print_config_setup()

    print_key_point(
        "REPLICAOF 告诉从节点：\n"
        "    「从今天起，你是我的主节点，我跟着你同步。」\n"
        "    从节点会主动连接主节点请求数据。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: 全量同步过程
    # ═══════════════════════════════════════════════════════════
    print_step(3, "全量同步 — 从节点第一次连接主节点")

    print_fullsync_diagram()

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: 增量同步与 backlog
    # ═══════════════════════════════════════════════════════════
    print_step(4, "增量同步 — 断线重连后只追差异")

    print_backlog_diagram()

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: 读写分离
    # ═══════════════════════════════════════════════════════════
    print_step(5, "读写分离 — 写走主，读走从")

    print_read_write_split()

    # 如果 Redis 已连接，试试 WAIT 命令演示
    if client is not None:
        try:
            section("WAIT 命令演示")
            print_command("WAIT 1 1000", "等待至少 1 个从节点确认，超时 1 秒")
            result = client.execute_command("WAIT", 1, 1000)
            print_result(result, "WAIT 返回 (确认的从节点数)")
            print_note(f"WAIT 返回 {result}，表示有 {result} 个从节点确认了写入")
            print_note("注意：当前实例可能没有从节点，返回 0 是正常的")
        except Exception as e:
            print(f"  {Color.DIM}WAIT 命令不可用: {e}{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: 常见错误
    # ═══════════════════════════════════════════════════════════
    print_step(6, "常见错误 — 避免踩坑")

    print_common_mistakes()

    # ═══════════════════════════════════════════════════════════
    # 第 7 步: 主从复制的局限 — 引出 Sentinel
    # ═══════════════════════════════════════════════════════════
    print_step(7, "主从复制的局限 — 为什么需要 Sentinel？")

    print_warning_diagram()

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 恭喜！你已经理解了 Redis 主从复制的核心概念:{Color.RESET}

   {Color.HIGHLIGHT}REPLICAOF{Color.RESET}      →  配置主从关系
   {Color.HIGHLIGHT}INFO REPLICATION{Color.RESET}  →  查看复制状态
   {Color.HIGHLIGHT}全量同步{Color.RESET}      →  从零开始的完整数据复制（RDB）
   {Color.HIGHLIGHT}增量同步{Color.RESET}      →  断线重连后只追差异（backlog）
   {Color.HIGHLIGHT}读写分离{Color.RESET}      →  写走主、读走从

{Color.DIM}但主从复制不能自动处理主节点故障——{Color.RESET}
{Color.DIM}下一章（s14 — Sentinel）让这一切自动化。{Color.RESET}
""")

    # 清理：如果有连接，清理演示用的 key
    if client is not None:
        try:
            cleanup_demo_keys(client, "demo:*")
        except Exception as e:
            print(f"  {Color.DIM}清理 demo keys 时出错（可忽略）: {e}{Color.RESET}")


if __name__ == "__main__":
    main()
