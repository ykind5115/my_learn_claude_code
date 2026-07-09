#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s14: Sentinel 哨兵 — 自动故障转移

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - Sentinel 解决了什么核心问题？
  - SDOWN 和 ODOWN 有什么区别？
  - quorum 的作用是什么？应该设多少？
  - 故障转移的完整流程是什么？
  - 脑裂是什么？怎么预防？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s14_sentinel/code.py
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


def print_sentinel_architecture():
    """打印 Sentinel 架构图"""
    section("Sentinel 架构图解")
    print(f"""
{Color.YELLOW}                    ┌────────────────────────────────────┐
                    │          Sentinel 监控层              │
                    │  ┌──────────┐  ┌──────────┐  ┌──────┐ │
                    │  │ Sentinel1│  │ Sentinel2│  │  S3  │ │
                    │  │ (26379)  │  │ (26380)  │  │(26381)│ │
                    │  └────┬─────┘  └────┬─────┘  └──┬───┘ │
                    │       │    互相通信   │   投票     │     │
                    │       └──────┬───────┴───────────┘     │
                    └──────────────│─────────────────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          ▼                       ▼                       ▼
    ┌──────────┐           ┌──────────┐           ┌──────────┐
    │  主节点   │  REPLICAOF │  从节点1  │  REPLICAOF │  从节点2  │
    │ :6379    │ ←───────── │ :6380    │ ←───────── │ :6381    │
    │ (Master) │           │ (Replica)│           │ (Replica)│
    └──────────┘           └──────────┘           └──────────┘{Color.RESET}
""")

    print_key_point(
        "Sentinel = 哨兵进程，不是 Redis 主从的替代品。\n"
        "    Sentinel 是独立于 Redis 的监控进程，通过投票决策实现自动故障转移。"
    )


def print_sdown_odown_diagram():
    """打印主观/客观下线对比图"""
    section("SDOWN vs ODOWN — 两阶段故障检测")

    print(f"""
{Color.HIGHLIGHT}阶段一：主观下线 (SDOWN){Color.RESET}
{Color.YELLOW}
  Sentinel → PING → 主节点
      │                   1 秒一次 PING
      ├── PONG ← 正常
      ├── ... 等待 ...
      └── 超过 5 秒没收到 PONG → SDOWN
{Color.RESET}
""")

    print(f"""
{Color.HIGHLIGHT}阶段二：客观下线 (ODOWN){Color.RESET}
{Color.YELLOW}
  Sentinel A (SDOWN)
      │
      ├── SENTINEL is-master-down-by-addr → 询问 B 和 C
      │
      ├── Sentinel B: 「我也连不上」  → 同意
      ├── Sentinel C: 「我也连不上」  → 同意
      │
      └── 3 个 Sentinel 中 3 个同意 → 超半数 (≥2)
                              ↓
                          ODOWN ✅
                         开始故障转移{Color.RESET}
""")

    print_key_point(
        "两阶段设计的目的：防止误判。\n"
        "    如果某个 Sentinel 和主节点间的网络恰好断了，\n"
        "    但其他 Sentinel 还能连上——不会触发切换。"
    )


def print_failover_timeline():
    """打印故障转移时间线"""
    section("故障转移完整时间线")

    timeline = [
        ("T+0s", "主节点挂了（进程崩溃 / 停电 / 网络）"),
        ("T+5s", "Sentinel 发现超时 → SDOWN", Color.WARNING),
        ("T+6s", "Sentinel 询问同伴 → 确认 ODOWN", Color.WARNING),
        ("T+7s", "Raft 选举 Leader Sentinel", ""),
        ("T+8s", "Leader 选新主（priority → offset → runid）", ""),
        ("T+9s", "REPLICAOF NO ONE → 新主上线", Color.SUCCESS),
        ("T+10s", "REPLICAOF new-master → 从节点切换", ""),
        ("T+12s", "原主恢复 → 自动成为新主的从", ""),
        ("T+13s", "故障转移完成 ✅ 写入恢复", Color.SUCCESS),
    ]

    print(f"\n  {Color.HEADER}典型时间线（down-after-milliseconds=5000）：{Color.RESET}")
    for item in timeline:
        ts = item[0]
        desc = item[1]
        color = item[2] if len(item) > 2 else ""
        if color:
            print(f"    {Color.HIGHLIGHT}{ts}{Color.RESET}  {color}{desc}{Color.RESET}")
        else:
            print(f"    {Color.HIGHLIGHT}{ts}{Color.RESET}  {desc}")

    print("")
    print_note("整个过程自动化，通常 10~30 秒完成，无需人工介入。")
    print_note("相比人工切换（5~30 分钟），这是质的飞跃。")


def print_new_master_election():
    """打印选新主规则"""
    section("选新主规则")

    print(f"""
  {Color.HEADER}从节点候选列表：{Color.RESET}
{Color.YELLOW}
    从节点 A: priority=1, offset=10000, runid=aaa
    从节点 B: priority=2, offset=9800,  runid=bbb
    从节点 C: priority=1, offset=9900,  runid=ccc
{Color.RESET}
  {Color.CYAN}选举过程：{Color.RESET}
    第 1 步: 淘汰 priority=0 的（不参与选举）
    第 2 步: 按 priority 排序 → A(1) C(1) B(2)
    第 3 步: priority 相同 → 比 offset
             A(10000) > C(9900) → A 数据更新
    第 4 步: 选定 A 为新主节点 ✅
""")

    print_key_point(
        "选新主三原则（按顺序）：\n"
        "    1. slave_priority 越高越好（=数字越小优先级越高）\n"
        "    2. replication offset 越大越好（=数据越新）\n"
        "    3. runid 越小越好（=字典序越小）"
    )


def print_sentinel_config():
    """打印 sentinel.conf 配置详解"""
    section("sentinel.conf 配置详解")

    print(f"""
{Color.COMMAND}# sentinel.conf 完整示例{Color.RESET}
{Color.YELLOW}
# 监控 mymaster，IP 192.168.1.10:6379，至少 2 票判定 ODOWN
sentinel monitor mymaster 192.168.1.10 6379 2

# 5 秒无响应算主观下线
sentinel down-after-milliseconds mymaster 5000

# 故障转移超时 3 分钟
sentinel failover-timeout mymaster 180000

# 每次只让 1 个从节点同步新主
sentinel parallel-syncs mymaster 1

# 如果 Redis 有密码
# sentinel auth-pass mymaster YourPassword
{Color.RESET}
""")

    section("配置项说明")

    configs = [
        ("sentinel monitor", "监控的主节点名称、地址、端口、quorum",
         "最重要的是 quorum——决定需要几票才能判定 ODOWN"),
        ("down-after-milliseconds", "多少毫秒无响应算主观下线",
         "设太小 → 网络抖动就切换；设太大 → 发现故障慢"),
        ("failover-timeout", "故障转移超时",
         "从开始切换到完成的超时时间"),
        ("parallel-syncs", "同时同步的从节点数",
         "1 最安全，越大同步越快但主节点压力越大"),
    ]

    for name, desc, note in configs:
        print(f"  {Color.HIGHLIGHT}{name}{Color.RESET}")
        print(f"    {Color.DIM}作用: {desc}{Color.RESET}")
        print(f"    {Color.DIM}💡 {note}{Color.RESET}")
        print("")


def print_split_brain():
    """打印脑裂说明"""
    section("脑裂 (Split-Brain) 及预防")

    print(f"""
{Color.YELLOW}网络分区发生：

  分区 A                         分区 B
  ┌─────────────┐               ┌──────────────────┐
  │ 主节点 :6379  │               │ 从节点 1 :6380    │
  │ Sentinel1    │   断开了！     │ 从节点 2 :6381    │
  └─────────────┘               │ Sentinel2         │
                                │ Sentinel3         │
                                └──────────────────┘

  分区 B 中 2/3 判定主挂了
  → 把从节点 1 升为新主
  → 分区 A 的主还在写
  → 两个主共存 = 脑裂
  → 分区恢复后，分区 A 的数据丢失{Color.RESET}
""")

    print(f"  {Color.CYAN}预防方案：{Color.RESET}")
    print(f"    {Color.COMMAND}min-replicas-to-write 1{Color.RESET}")
    print(f"    {Color.COMMAND}min-replicas-max-lag 10{Color.RESET}")
    print("")
    print_note("意思是：主节点至少要有 1 个从节点在线且延迟 < 10 秒")
    print_note("否则主节点拒绝写入——防止脑裂期间的数据无限增长")
    print_note("这不是 100% 的保证，但能显著降低数据丢失量。")


def print_sentinel_commands():
    """打印 Sentinel 命令演示"""
    section("Sentinel 命令")

    print(f"""
  {Color.HEADER}常用 Sentinel 命令：{Color.RESET}

{Color.COMMAND}  SENTINEL masters{Color.RESET}
    → 列出所有被监控的主节点及状态

{Color.COMMAND}  SENTINEL master mymaster{Color.RESET}
    → 查看指定主节点的详细信息

{Color.COMMAND}  SENTINEL slaves mymaster{Color.RESET}
    → 查看指定主节点的所有从节点

{Color.COMMAND}  SENTINEL get-master-addr-by-name mymaster{Color.RESET}
    → 获取当前主节点的 IP 和端口（客户端最常用的命令！）

{Color.COMMAND}  SENTINEL failover mymaster{Color.RESET}
    → 手动触发故障转移（测试用）

{Color.COMMAND}  SENTINEL monitor mymaster 192.168.1.10 6379 2{Color.RESET}
    → 动态添加一个监控项

{Color.COMMAND}  SENTINEL remove mymaster{Color.RESET}
    → 移除监控项
""")


def print_sentinel_client_code():
    """打印 Sentinel 客户端代码示例"""
    section("客户端通过 Sentinel 连接 Redis")

    code = '''
from redis.sentinel import Sentinel

# 连接所有 Sentinel（只连一个也可以，它会告诉你其他的）
sentinel = Sentinel([
    ('192.168.1.1', 26379),
    ('192.168.1.2', 26379),
    ('192.168.1.3', 26379),
], socket_timeout=0.1)

# Sentinel 自动返回当前主节点地址
# 故障转移后，它自动返回新主节点地址
master = sentinel.master_for('mymaster')
slave = sentinel.slave_for('mymaster')

# 写走主
master.set('foo', 'bar')

# 读走从
value = slave.get('foo')
'''

    print(f"  {Color.COMMAND}Python 代码示例：{Color.RESET}")
    # 缩进处理代码块
    for line in code.strip().split("\n"):
        print(f"  {Color.DIM}{line}{Color.RESET}")
    print("")

    print_key_point(
        "Sentinel-aware 客户端的好处：\n"
        "    「客户端不需要知道主节点地址——问 Sentinel 就行。」\n"
        "    故障转移后，Sentinel 返回新主地址，客户端自动切换。"
    )


def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s14: Sentinel 哨兵 — 自动故障转移{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: 了解 Sentinel 架构
    # ═══════════════════════════════════════════════════════════
    print_step(1, "Sentinel 架构 — 谁在监控谁？")

    print_sentinel_architecture()

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: 连接 Redis — 检查是否能连通 Sentinel
    # ═══════════════════════════════════════════════════════════
    print_step(2, "尝试连接 Redis — 检查环境")

    client = None
    try:
        client = get_redis_client()
    except SystemExit:
        pass  # Redis 不可用，降级到纯概念模式

    if client is not None:
        print(f"  {Color.SUCCESS}✅ Redis 已连接{Color.RESET}")

        # 尝试 Sentinel 命令（如果不支持也不影响演示）
        section("尝试 Sentinel 命令")
        try:
            print_command("SENTINEL masters", "列出被监控的主节点")
            result = client.execute_command("SENTINEL", "MASTERS")
            if result:
                print(f"  → {Color.SUCCESS}{result}{Color.RESET}")
            else:
                print(f"  → {Color.DIM}(无被监控的主节点){Color.RESET}")
        except Exception as e:
            print(f"  → {Color.DIM}SENTINEL 命令不可用: {e}{Color.RESET}")
            print(f"  → {Color.DIM}这是正常的——当前 Redis 实例不是 Sentinel 模式{Color.RESET}")

        # 检查是否有哨兵配置
        try:
            sentinels = client.info("sentinel")
            print(f"  → Sentinel 信息: {Color.DIM}{sentinels}{Color.RESET}")
        except Exception:
            print(f"  → {Color.DIM}当前实例没有 Sentinel 信息{Color.RESET}")
    else:
        print(f"  {Color.WARNING}⚠ 无法连接到 Redis，将以纯概念模式运行{Color.RESET}")
        print(f"  {Color.DIM}  命令演示和输出将使用模拟数据{Color.RESET}\n")

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: SDOWN vs ODOWN
    # ═══════════════════════════════════════════════════════════
    print_step(3, "故障检测 — SDOWN 和 ODOWN")

    print_sdown_odown_diagram()

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: 故障转移流程
    # ═══════════════════════════════════════════════════════════
    print_step(4, "故障转移 — 从检测到恢复的完整时间线")

    print_failover_timeline()
    print_new_master_election()

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: Sentinel 配置详解
    # ═══════════════════════════════════════════════════════════
    print_step(5, "Sentinel 配置 — sentinel.conf")

    print_sentinel_config()

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: Sentinel 命令
    # ═══════════════════════════════════════════════════════════
    print_step(6, "Sentinel 命令 — 如何监控和操作")

    print_sentinel_commands()
    print_sentinel_client_code()

    # ═══════════════════════════════════════════════════════════
    # 第 7 步: 常见问题
    # ═══════════════════════════════════════════════════════════
    print_step(7, "常见问题 — 脑裂和配置陷阱")

    print_split_brain()

    # 其他常见错误
    section("更多常见错误")

    print(f"""
  {Color.ERROR}❌ Sentinel 数量为偶数{Color.RESET}
    {Color.DIM}2 个 Sentinel → 网络分区后各 1 票，永远打平{Color.RESET}
    {Color.DIM}4 个 Sentinel → 挂 1 个剩下 3 个是奇数，还行，但浪费资源{Color.RESET}
    {Color.DIM}推荐：3 个或 5 个{Color.RESET}

  {Color.ERROR}❌ quorum 设得太大{Color.RESET}
    {Color.DIM}5 个 Sentinel → quorum=5 → 任何 1 个挂了都无法凑齐{Color.RESET}
    {Color.DIM}推荐：quorum = N/2 + 1{Color.RESET}

  {Color.ERROR}❌ 客户端硬编码主节点 IP{Color.RESET}
    {Color.DIM}故障转移后主节点地址变了，客户端不知道{Color.RESET}
    {Color.DIM}推荐：使用 Sentinel-aware 客户端或 DNS{Color.RESET}
""")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 恭喜！你已经理解了 Redis Sentinel 的核心概念:{Color.RESET}

   {Color.HIGHLIGHT}Sentinel 架构{Color.RESET}  →  独立监控进程，投票决策
   {Color.HIGHLIGHT}SDOWN{Color.RESET}         →  单个 Sentinel 主观判断
   {Color.HIGHLIGHT}ODOWN{Color.RESET}         →  多数 Sentinel 确认故障
   {Color.HIGHLIGHT}quorum{Color.RESET}        →  判定故障所需最少票数
   {Color.HIGHLIGHT}故障转移{Color.RESET}      →  选新主 → 切换从 → 通知客户端
   {Color.HIGHLIGHT}脑裂{Color.RESET}          →  网络分区导致双主，用 min-replicas 预防

{Color.DIM}Sentinel 解决了「主节点挂了谁来自动切换」的问题。{Color.RESET}
{Color.DIM}下一章（s15 — Cluster）解决「一块黑板装不下」的问题。{Color.RESET}
""")

    # 清理
    if client is not None:
        try:
            cleanup_demo_keys(client, "demo:*")
        except Exception as e:
            print(f"  {Color.DIM}清理 demo keys 时出错（可忽略）: {e}{Color.RESET}")


if __name__ == "__main__":
    main()
