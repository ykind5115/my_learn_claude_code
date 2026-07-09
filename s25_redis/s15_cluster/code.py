#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s15: Cluster 集群 — 黑板分片

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - Redis Cluster 为什么需要哈希槽？
  - CRC16(key) % 16384 是怎么算的？
  - MOVED 和 ASK 有什么区别？
  - 集群故障转移和 Sentinel 有什么不同？
  - 多 key 操作跨槽了怎么办？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s15_cluster/code.py
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


# ═══════════════════════════════════════════════════════════
# CRC16 实现（Redis 实际使用的 CRC16 算法简化版）
# ═══════════════════════════════════════════════════════════

# CRC16 查找表（Redis 实际使用的 CRC16-CCITT 变体）
CRC16_TABLE = [
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7,
    0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF,
    0x1231, 0x0210, 0x3273, 0x2252, 0x52B5, 0x4294, 0x72F7, 0x62D6,
    0x9339, 0x8318, 0xB37B, 0xA35A, 0xD3BD, 0xC39C, 0xF3FF, 0xE3DE,
    0x2462, 0x3443, 0x0420, 0x1401, 0x64E6, 0x74C7, 0x44A4, 0x5485,
    0xA56A, 0xB54B, 0x8528, 0x9509, 0xE5EE, 0xF5CF, 0xC5AC, 0xD58D,
    0x3653, 0x2672, 0x1611, 0x0630, 0x76D7, 0x66F6, 0x5695, 0x46B4,
    0xB75B, 0xA77A, 0x9719, 0x8738, 0xF7DF, 0xE7FE, 0xD79D, 0xC7BC,
    0x48C4, 0x58E5, 0x6886, 0x78A7, 0x0840, 0x1861, 0x2802, 0x3823,
    0xC9CC, 0xD9ED, 0xE98E, 0xF9AF, 0x8948, 0x9969, 0xA90A, 0xB92B,
    0x5AF5, 0x4AD4, 0x7AB7, 0x6A96, 0x1A71, 0x0A50, 0x3A33, 0x2A12,
    0xDBFD, 0xCBDC, 0xFBBF, 0xEB9E, 0x9B79, 0x8B58, 0xBB3B, 0xAB1A,
    0x6CA6, 0x7C87, 0x4CE4, 0x5CC5, 0x2C22, 0x3C03, 0x0C60, 0x1C41,
    0xEDAE, 0xFD8F, 0xCDEC, 0xDDCD, 0xAD2A, 0xBD0B, 0x8D68, 0x9D49,
    0x7E97, 0x6EB6, 0x5ED5, 0x4EF4, 0x3E13, 0x2E32, 0x1E51, 0x0E70,
    0xFF9F, 0xEFBE, 0xDFDD, 0xCFFC, 0xBF1B, 0xAF3A, 0x9F59, 0x8F78,
    0x9188, 0x81A9, 0xB1CA, 0xA1EB, 0xD10C, 0xC12D, 0xF14E, 0xE16F,
    0x1080, 0x00A1, 0x30C2, 0x20E3, 0x5004, 0x4025, 0x7046, 0x6067,
    0x83B9, 0x9398, 0xA3FB, 0xB3DA, 0xC33D, 0xD31C, 0xE37F, 0xF35E,
    0x02B1, 0x1290, 0x22F3, 0x32D2, 0x4235, 0x5214, 0x6277, 0x7256,
    0xB5EA, 0xA5CB, 0x95A8, 0x8589, 0xF56E, 0xE54F, 0xD52C, 0xC50D,
    0x34E2, 0x24C3, 0x14A0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
    0xA7DB, 0xB7FA, 0x8799, 0x97B8, 0xE75F, 0xF77E, 0xC71D, 0xD73C,
    0x26D3, 0x36F2, 0x0691, 0x16B0, 0x6657, 0x7676, 0x4615, 0x5634,
    0xD94C, 0xC96D, 0xF90E, 0xE92F, 0x99C8, 0x89E9, 0xB98A, 0xA9AB,
    0x5844, 0x4865, 0x7806, 0x6827, 0x18C0, 0x08E1, 0x3882, 0x28A3,
    0xCB7D, 0xDB5C, 0xEB3F, 0xFB1E, 0x8BF9, 0x9BD8, 0xABBB, 0xBB9A,
    0x4A75, 0x5A54, 0x6A37, 0x7A16, 0x0AF1, 0x1AD0, 0x2AB3, 0x3A92,
    0xFD2E, 0xED0F, 0xDD6C, 0xCD4D, 0xBDAA, 0xAD8B, 0x9DE8, 0x8DC9,
    0x7C26, 0x6C07, 0x5C64, 0x4C45, 0x3CA2, 0x2C83, 0x1CE0, 0x0CC1,
    0xEF1F, 0xFF3E, 0xCF5D, 0xDF7C, 0xAF9B, 0xBFBA, 0x8FD9, 0x9FF8,
    0x6E17, 0x7E36, 0x4E55, 0x5E74, 0x2E93, 0x3EB2, 0x0ED1, 0x1EF0,
]


def crc16(data: bytes) -> int:
    """CRC16-CCITT 计算（Redis 实际使用的算法）"""
    crc = 0
    for byte in data:
        crc = ((crc << 8) & 0xFF00) ^ CRC16_TABLE[((crc >> 8) ^ byte) & 0xFF]
    return crc & 0xFFFF


def hash_slot(key: str) -> int:
    """计算 Redis Cluster 中 key 的哈希槽号。

    规则：
    1. 如果 key 包含 '{...}'，只计算 {} 内的内容（哈希标签）
    2. 否则计算整个 key
    """
    # 处理哈希标签：key 中 {tag} 部分
    start = key.find("{")
    if start >= 0:
        end = key.find("}", start + 1)
        if end > start + 1:
            # 只计算 {} 内的内容
            return crc16(key[start + 1:end].encode()) % 16384
    return crc16(key.encode()) % 16384


# ═══════════════════════════════════════════════════════════
# 演示函数
# ═══════════════════════════════════════════════════════════

def print_cluster_architecture():
    """打印 Cluster 架构图"""
    section("Cluster 架构图解")
    print(f"""
{Color.YELLOW}                       客户端
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ 节点 1    │  │ 节点 2    │  │ 节点 3    │
    │ :7000     │  │ :7001     │  │ :7002     │
    │           │  │           │  │           │
    │ 槽 0~5460 │  │ 槽 5461~ │  │ 槽 10923~│
    │           │  │ 10922    │  │ 16383    │
    │ 主 + 从    │  │ 主 + 从   │  │ 主 + 从    │
    └──────────┘  └──────────┘  └──────────┘{Color.RESET}
""")

    print_key_point(
        "Cluster 三大核心设计：\n"
        "    1. 分片：16384 个槽分散到各个节点\n"
        "    2. 自动发现：节点之间用 gossip 协议互相通信\n"
        "    3. 高可用：每个主节点可以有从节点"
    )


def print_hash_slot_calculation():
    """演示哈希槽计算过程"""
    section("哈希槽计算 — CRC16(key) % 16384")

    demo_keys = [
        "user:1001",
        "user:1002",
        "product:50",
        "session:a1bc",
        "order:20240101",
        "cache:homepage",
    ]

    print(f"\n  {Color.HEADER}计算各个 key 的槽号：{Color.RESET}")
    print(f"  {Color.DIM}{'key':<25} {'CRC16':<8} {'槽号':<8} 节点{Color.RESET}")
    print(f"  {Color.DIM}{'─' * 55}{Color.RESET}")

    for key in demo_keys:
        c = crc16(key.encode())
        slot = hash_slot(key)
        node = slot // 5461  # 模拟 3 节点分布
        print(f"  {Color.YELLOW}{key:<25}{Color.RESET} "
              f"{c:<8} {Color.HIGHLIGHT}{slot:<8}{Color.RESET} "
              f"节点 {node + 1}")

    print("")

    print_key_point(
        "槽号计算是确定性的——\n"
        "    同一个 key 永远算出同一个槽号。\n"
        "    这是 Redis Cluster 找到正确节点的前提。"
    )


def print_hash_tag_demo():
    """演示哈希标签的效果"""
    section("哈希标签 — {} 让多个 key 进入同一槽")

    print(f"""
  {Color.HEADER}没有哈希标签：{Color.RESET}{Color.YELLOW}
    user:1001:profile         槽 {hash_slot("user:1001:profile")}
    user:1001:orders          槽 {hash_slot("user:1001:orders")}
    user:1001:cart            槽 {hash_slot("user:1001:cart")}
    → 三个 key 在不同槽！不能一起操作{Color.RESET}

  {Color.HEADER}使用哈希标签：{Color.RESET}{Color.YELLOW}
    user:{{1001}}:profile     槽 {hash_slot("user:{1001}:profile")}
    user:{{1001}}:orders      槽 {hash_slot("user:{1001}:orders")}
    user:{{1001}}:cart        槽 {hash_slot("user:{1001}:cart")}
    → 三个 key 在同一槽！可以一起操作 ✅{Color.RESET}
""")

    print_note("哈希标签：CRC16 只计算 {} 内的内容，不计算整个 key。")
    print_note("这样不同 key 只要 {} 部分相同，就在同一槽。")


def print_moved_diagram():
    """打印 MOVED 重定向流程图"""
    section("MOVED 重定向")

    print(f"""
{Color.YELLOW}  客户端                      节点 1                       节点 2
    │                          │                          │
    │── GET user:1001 ────────→│                          │
    │                          │  CRC16("user:1001")      │
    │                          │  = 7234                  │
    │                          │  槽 7234 不在我这         │
    │←── MOVED 7234 :7001 ────│                          │
    │                          │                          │
    │  更新本地缓存             │                          │
    │  槽 7234 → 节点 2        │                          │
    │                          │                          │
    │── GET user:1001 ──────────────────────────────────→│
    │←── "小明" ─────────────────────────────────────────│
    │                          │                          │{Color.RESET}
""")

    print_key_point(
        "MOVED = 「这个槽已经完全归另一个节点管了」\n"
        "    客户端应更新本地槽位映射表，下次直接去新节点。\n"
        "    这是永久性的重定向——槽已经确定归属。"
    )


def print_ask_diagram():
    """打印 ASK 重定向流程图"""
    section("ASK 重定向（槽迁移中）")

    print(f"""
{Color.YELLOW}  客户端                      节点 3 (迁入中)              节点 2 (迁出中)
    │                          │                          │
    │── GET user:1001 ────────→│                          │
    │                          │  槽 7234 是我的了         │
    │                          │  但数据可能还在节点 2     │
    │←── ASK 7234 :7002 ──────│                          │
    │                          │                          │
    │── ASKING ────────────────│                          │
    │←── OK ──────────────────│                          │
    │                          │                          │
    │── GET user:1001 ──────────────────────────────────→│
    │←── "小明" ─────────────────────────────────────────│
    │                          │                          │{Color.RESET}
""")

    print_note("ASK ≠ MOVED。ASK 是临时状态——槽正在迁移中。")
    print_note("客户端必须先发 ASKING 命令获得临时访问权，再去旧节点读。")


def print_cluster_commands():
    """打印 Cluster 命令"""
    section("Cluster 常用命令")

    print(f"""
{Color.COMMAND}  CLUSTER INFO{Color.RESET}
    → 查看集群状态（集群大小、槽分配、故障节点等）

{Color.COMMAND}  CLUSTER NODES{Color.RESET}
    → 查看所有节点的 ID、IP、角色、槽范围

{Color.COMMAND}  CLUSTER SLOTS{Color.RESET}
    → 查看槽位到节点的映射关系

{Color.COMMAND}  CLUSTER KEYSLOT user:1001{Color.RESET}
    → 查看指定 key 的槽号

{Color.COMMAND}  CLUSTER COUNTKEYSINSLOT 7234{Color.RESET}
    → 查看指定槽中有多少个 key

{Color.COMMAND}  CLUSTER GETKEYSINSLOT 7234 10{Color.RESET}
    → 获取指定槽中的前 N 个 key

{Color.COMMAND}  CLUSTER MEET 192.168.1.4 6379{Color.RESET}
    → 邀请一个新节点加入集群
""")


def print_reshard_process():
    """打印扩容/缩容槽迁移过程"""
    section("槽迁移流程 — 扩容/缩容")

    print(f"""
{Color.YELLOW}  迁移前:
    节点 2: 负责槽 5461~10922，数据完整

  迁移中:
    CLUSTER SETSLOT 7234 MIGRATING node2-id
      → 节点 2 标记：槽 7234 正在迁出

    CLUSTER SETSLOT 7234 IMPORTING node3-id
      → 节点 3 标记：槽 7234 正在迁入

    客户端访问槽 7234 期间：
      → 去节点 2 → 正常返回（数据还在节点 2）
      → 去节点 3 → ASK 重定向到节点 2

    MIGRATE 命令迁移数据：
      → 将 key 从节点 2 搬到节点 3

  迁移完成:
    CLUSTER SETSLOT 7234 NODE node3-id
      → 槽归属正式切换
      → 所有后续操作直接去节点 3{Color.RESET}
""")

    print_key_point(
        "槽迁移是在线操作——不影响集群整体可用性。\n"
        "    迁移中的 key 处于「半迁移」状态：\n"
        "      - 旧节点有数据 → 直接返回\n"
        "      - 旧节点没数据了 → 返回 ASK 让客户端去新节点\n"
        "    迁移完成后，所有操作走新节点。"
    )


def print_cluster_vs_sentinel():
    """打印 Cluster 和 Sentinel 的对比"""
    section("Cluster vs Sentinel — 怎么选？")

    print(f"""
{Color.YELLOW}  ┌─────────────────────┬──────────────────────┐
  │     Cluster          │      Sentinel         │
  ├─────────────────────┼──────────────────────┤
  │ 自动分片             │ 不分片，所有节点存全部 │
  │ 支持 1000 节点       │ 通常 1 主 N 从        │
  │ 内置高可用           │ 需要额外 Sentinel 进程 │
  │ 客户端需支持 Cluster  │ 客户端支持更简单       │
  │ 槽迁移在线           │ 扩容需要迁移到更大机器  │
  │ 部署配置复杂          │ 部署配置简单           │
  │ 适合大数据量          │ 适合小数据量+高可用     │
  └─────────────────────┴──────────────────────┘{Color.RESET}
""")

    print_note("数据量 < 单机内存 → Sentinel（简单、可靠）")
    print_note("数据量 > 单机内存 → Cluster（分片、扩展）")


def print_common_mistakes():
    """打印常见错误"""
    section("常见错误")

    errors = [
        ("多 key 操作跨槽",
         "MGET user:1001 user:1002 可能在不同槽。\n"
         "    用哈希标签 {tag} 让相关 key 进入同一槽。"),
        ("客户端不支持 Cluster 模式",
         "老旧的 Redis 客户端不处理 MOVED 重定向。\n"
         "    使用 redis-py-cluster 或 Lettuce 等 Cluster-aware 客户端。"),
        ("槽分配不均",
         "有些节点槽太多 → 负载高。\n"
         "    用 redis-cli --cluster rebalance 重新分配。"),
        ("所有节点在同一台物理机",
         "物理机挂了 → 整个集群不可用。\n"
         "    分布到多台物理机，利用从节点做容灾。"),
    ]

    for title, desc in errors:
        print(f"  {Color.ERROR}❌ {title}{Color.RESET}")
        for line in desc.split("\n"):
            print(f"    {Color.DIM}{line}{Color.RESET}")
        print("")


def try_cluster_commands(client):
    """尝试连接 Redis 并运行 Cluster 命令（如果支持）"""
    section("尝试 Cluster 命令")

    cluster_enabled = False
    try:
        info = client.info("server")
        cluster_mode = info.get("cluster_enabled", "unknown")
        print(f"  Cluster 模式: {Color.YELLOW}{cluster_mode}{Color.RESET}")
    except Exception:
        pass

    try:
        print_command("CLUSTER INFO", "查看集群信息")
        result = client.execute_command("CLUSTER", "INFO")
        if result:
            print(f"  → {result}")
        else:
            print(f"  → {Color.DIM}(空){Color.RESET}")
    except Exception as e:
        err_msg = str(e)
        print(f"  → {Color.DIM}{err_msg}{Color.RESET}")

        if "not enabled" in err_msg.lower() or "not clustered" in err_msg.lower():
            cluster_enabled = False
            print(f"  → {Color.DIM}(这是正常的——当前 Redis 实例不是集群模式){Color.RESET}")

    # KEYSLOT 命令通常在任何 Redis 上都可用（即使不是集群模式）
    try:
        section("CLUSTER KEYSLOT 演示")
        test_keys = ["user:1001", "product:50", "user:{1001}:profile"]
        for key in test_keys:
            print_command(f'CLUSTER KEYSLOT {key}')
            result = client.execute_command("CLUSTER", "KEYSLOT", key)
            print(f"  → key '{Color.YELLOW}{key}{Color.RESET}' 的槽号: {Color.HIGHLIGHT}{result}{Color.RESET}")
    except Exception as e:
        print(f"  → {Color.DIM}KEYSLOT 命令不可用: {e}{Color.RESET}")


def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s15: Cluster 集群 — 黑板分片{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: Cluster 架构
    # ═══════════════════════════════════════════════════════════
    print_step(1, "Cluster 架构 — 16384 块拼图")

    print_cluster_architecture()

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: 连接 Redis 尝试运行集群命令
    # ═══════════════════════════════════════════════════════════
    print_step(2, "连接 Redis — 检查集群模式")

    client = None
    try:
        client = get_redis_client()
    except SystemExit:
        pass  # Redis 不可用，降级到纯概念模式

    if client is not None:
        print(f"  {Color.SUCCESS}✅ Redis 已连接{Color.RESET}")
        try_cluster_commands(client)
    else:
        print(f"  {Color.WARNING}⚠ 无法连接到 Redis，将以纯概念模式运行{Color.RESET}")
        print(f"  {Color.DIM}  命令演示将使用模拟输出{Color.RESET}\n")

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: 哈希槽计算
    # ═══════════════════════════════════════════════════════════
    print_step(3, "哈希槽 — CRC16(key) % 16384")

    print_hash_slot_calculation()
    print_hash_tag_demo()

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: MOVED 和 ASK 重定向
    # ═══════════════════════════════════════════════════════════
    print_step(4, "MOVED vs ASK — 客户端如何找到正确节点")

    print_moved_diagram()
    print_ask_diagram()

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: 集群命令
    # ═══════════════════════════════════════════════════════════
    print_step(5, "集群命令 — 查看和管理集群")

    print_cluster_commands()

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: 槽迁移
    # ═══════════════════════════════════════════════════════════
    print_step(6, "扩容/缩容 — 在线槽迁移")

    print_reshard_process()

    # ═══════════════════════════════════════════════════════════
    # 第 7 步: Cluster vs Sentinel
    # ═══════════════════════════════════════════════════════════
    print_step(7, "Cluster vs Sentinel — 怎么选？")

    print_cluster_vs_sentinel()

    # ═══════════════════════════════════════════════════════════
    # 第 8 步: 常见错误
    # ═══════════════════════════════════════════════════════════
    print_step(8, "常见错误 — 避免踩坑")

    print_common_mistakes()

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 恭喜！你已经理解了 Redis Cluster 的核心概念:{Color.RESET}

   {Color.HIGHLIGHT}16384 个槽{Color.RESET}     →  分片的基本单位
   {Color.HIGHLIGHT}CRC16(key)%16384{Color.RESET}  →  决定 key 归属哪个槽
   {Color.HIGHLIGHT}MOVED{Color.RESET}         →  槽已确定换节点了
   {Color.HIGHLIGHT}ASK{Color.RESET}           →  槽正在迁移中
   {Color.HIGHLIGHT}哈希标签{Color.RESET}      →  {tag} 让多 key 进同一槽
   {Color.HIGHLIGHT}槽迁移{Color.RESET}        →  在线扩容/缩容

{Color.DIM}三章学完——主从复制、Sentinel、Cluster——{Color.RESET}
{Color.DIM}你已经掌握了 Redis 高可用和分布式架构的核心。{Color.RESET}
""")

    # 清理
    if client is not None:
        try:
            cleanup_demo_keys(client, "demo:*")
        except Exception as e:
            print(f"  {Color.DIM}清理 demo keys 时出错（可忽略）: {e}{Color.RESET}")


if __name__ == "__main__":
    main()
