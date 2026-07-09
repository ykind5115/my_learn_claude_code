#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s03: 计数器与原子操作 — 只有一个人能在同一个位置写字

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - INCR 为什么比 GET + SET 安全？
  - Redis 的单线程模型如何保证原子性？
  - SETNX 在什么场景下使用？
  - 怎么用 SET NX EX 实现一个简陋的分布式锁？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s03_counter_atomic/code.py
"""

import sys
import threading
import time
from pathlib import Path

# 确保项目根目录在 sys.path 中，以便导入 utils
_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from s25_redis.utils import (
    Color,
    get_redis_client,
    show_blackboard,
    print_step,
    print_command,
    print_note,
    print_key_point,
    print_result,
    cleanup_demo_keys,
    section,
    flush_db,
)


def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s03: 计数器与原子操作{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # 连接 Redis
    client = get_redis_client()

    # 清理残留
    cleanup_demo_keys(client, "demo:*")
    for key in ["counter", "score", "price", "lock", "visits",
                 "flag", "page_views", "atomic_demo", "non_atomic_demo"]:
        client.delete(key)
    client.flushdb()

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: INCR — 原子加 1
    # ═══════════════════════════════════════════════════════════
    print_step(1, "INCR — 原子加 1")

    print_command("SET visits '0'", "初始化计数器")
    client.set("visits", "0")
    show_blackboard(client, "初始化后")

    print_command("INCR visits", "原子加 1")
    result = client.incr("visits")
    print_result(result, "INCR visits")
    show_blackboard(client, "INCR 一次后")

    print_command("INCR visits (连续 3 次)")
    for i in range(3):
        result = client.incr("visits")
        print(f"  → 第 {i + 1} 次 INCR: {Color.HIGHLIGHT}{result}{Color.RESET}")
    show_blackboard(client, "INCR 4 次后")

    print_key_point(
        "INCR 一步完成「读 → 加 1 → 写回」三件事。\n"
        "    不会出现两个请求同时读到 0 的情况——因为命令是串行执行的。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: INCR 自动创建 key
    # ═══════════════════════════════════════════════════════════
    print_step(2, "INCR 自动创建 key — 不需要先 SET")

    print_command("INCR new_counter", "对一个不存在的 key 执行 INCR")
    result = client.incr("new_counter")
    print_result(result, "INCR new_counter")
    print_note("INCR 自动创建了 key，默认从 0 开始加 1。")

    show_blackboard(client, "自动创建的 key")

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: DECR — 原子减 1
    # ═══════════════════════════════════════════════════════════
    print_step(3, "DECR — 原子减 1")

    print_command("DECR visits", "原子减 1")
    result = client.decr("visits")
    print_result(result, "DECR visits")
    show_blackboard(client, "DECR 一次后")

    # 减到负数
    print_command("DECR visits (连续 5 次减到负数)")
    for i in range(5):
        result = client.decr("visits")
    print(f"  → 最终值: {Color.HIGHLIGHT}{result}{Color.RESET}")
    print_note("Redis 允许计数器减到负数——没有「不能低于 0」的限制。")

    show_blackboard(client, "DECR 到负数")

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: INCRBY — 加任意数值
    # ═══════════════════════════════════════════════════════════
    print_step(4, "INCRBY / DECRBY — 加/减任意数值")

    print_command("SET score '100'", "初始化分数")
    client.set("score", "100")

    print_command("INCRBY score 50", "加 50 分")
    result = client.incrby("score", 50)
    print_result(result, "INCRBY score 50")

    print_command("INCRBY score -30", "加负数 = 减 30")
    result = client.incrby("score", -30)
    print_result(result, "INCRBY score -30")

    show_blackboard(client, "INCRBY 操作后")

    print_key_point(
        "INCRBY 比连续调 50 次 INCR 高效多了——一次网络往返。\n"
        "    传负数进去，INCRBY 就变成了 DECRBY。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: INCRBYFLOAT — 浮点数增量
    # ═══════════════════════════════════════════════════════════
    print_step(5, "INCRBYFLOAT — 浮点数增量")

    print_command("SET price '99.9'", "初始化价格")
    client.set("price", "99.9")

    print_command("INCRBYFLOAT price 0.1", "加 0.1 元")
    result = client.incrbyfloat("price", 0.1)
    print_result(result, "INCRBYFLOAT price 0.1")

    print_command("INCRBYFLOAT price -9.99", "减 9.99 元")
    result = client.incrbyfloat("price", -9.99)
    print_result(result, "INCRBYFLOAT price -9.99")

    print_note("INCRBYFLOAT 返回的是字符串（不是浮点数）。")
    print_note("金融场景建议用整数存「分」——避免浮点精度问题。")

    show_blackboard(client, "浮点数操作后")

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: SETNX — 不存在才写
    # ═══════════════════════════════════════════════════════════
    print_step(6, "SETNX — 不存在才写（首次写入保护）")

    print_command("SETNX flag 'first'", "第一次尝试写入")
    result = client.setnx("flag", "first")
    print_result(result, "SETNX flag (1=成功, 0=失败)")
    show_blackboard(client, "SETNX 首次写入后")

    print_command("SETNX flag 'second'", "第二次尝试——key 已经存在了")
    result = client.setnx("flag", "second")
    print_result(result, "SETNX flag (1=成功, 0=失败)")
    show_blackboard(client, "SETNX 第二次——什么也没变")

    print_key_point(
        "SETNX 就像「只有第一个人能在这个位置写字」。\n"
        "    第一个 SETNX 成功写入，后续的 SETNX 什么也不做。\n"
        "    这是分布式锁的基础（s09 展开）。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 7 步: GETSET — 写新值，返回旧值
    # ═══════════════════════════════════════════════════════════
    print_step(7, "GETSET — 写新值，返回旧值")

    print_command("GETSET visits '100'", "把 visits 改写为 100，同时返回旧值")
    result = client.getset("visits", "100")
    print_result(result, "GETSET visits (返回旧值)")
    show_blackboard(client, "GETSET 之后")

    print_note("GETSET 原子地完成「读旧值 + 写新值」两件事。")
    print_note("常用于计数器重置（比如每天凌晨归零但记录前一天的值）")

    # ═══════════════════════════════════════════════════════════
    # 第 8 步: SET NX EX — 带过期的首次写入
    # ═══════════════════════════════════════════════════════════
    print_step(8, "SET NX EX — 带过期的首次写入（分布式锁雏形）")

    print_command('SET lock "locked" NX EX 10', "原子：不存在才写 + 10 秒过期")
    result = client.set("lock", "locked", nx=True, ex=10)
    print_result(result, "SET lock NX EX 10")
    show_blackboard(client, "成功获取锁！可以看到 TTL 在倒计时")

    print_command('SET lock "locked" NX EX 10', "再次尝试获取同一个锁——应该失败")
    result = client.set("lock", "locked", nx=True, ex=10)
    print_result(result, "SET lock (第二次)")
    print(f"  → {Color.WARNING}锁已被占用，获取失败{Color.RESET}")
    print_note("这正是分布式锁的核心——同一时刻只有一个客户端能拿到锁。")

    ttl = client.ttl("lock")
    print(f"  → TTL = {ttl}s，锁会自动释放")

    show_blackboard(client, "锁状态")

    # ═══════════════════════════════════════════════════════════
    # 第 9 步: 并发对比演示 — INCR vs GET+SET
    # ═══════════════════════════════════════════════════════════
    print_step(9, "并发对比演示 — INCR 原子 vs GET+SET 非原子")

    # 重置两个计数器
    client.set("atomic_demo", "0")
    client.set("non_atomic_demo", "0")
    print(f"  {Color.DIM}初始化两个计数器为 0{Color.RESET}")

    NUM_THREADS = 10
    INCREMENTS_PER_THREAD = 100

    def atomic_worker():
        """使用 INCR（原子操作）"""
        for _ in range(INCREMENTS_PER_THREAD):
            client.incr("atomic_demo")

    def non_atomic_worker():
        """使用 GET + SET（非原子操作）"""
        for _ in range(INCREMENTS_PER_THREAD):
            # 模拟并发竞争——每次都重新读、算、写
            val = int(client.get("non_atomic_demo"))
            client.set("non_atomic_demo", str(val + 1))

    # 启动原子操作线程
    print(f"\n  {Color.INFO}启动 {NUM_THREADS} 个线程，每个 INCR 100 次...{Color.RESET}")
    threads = []
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=atomic_worker)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    result = client.get("atomic_demo")
    expected = NUM_THREADS * INCREMENTS_PER_THREAD
    print(f"\n  → 原子 INCR 结果: {Color.HIGHLIGHT}{result}{Color.RESET}"
          f"  (期望: {expected}, {'✅ 正确' if int(result) == expected else '❌ 错误'})")

    # 启动非原子操作线程
    print(f"\n  {Color.INFO}启动 {NUM_THREADS} 个线程，每个 GET+SET 100 次...{Color.RESET}")
    threads = []
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=non_atomic_worker)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    result = client.get("non_atomic_demo")
    print(f"\n  → 非原子 GET+SET 结果: {Color.HIGHLIGHT}{result}{Color.RESET}"
          f"  (期望: {expected}, {'✅ 正确' if int(result) == expected else '❌ 丢失数据！'})")

    print()
    print_key_point(
        "INCR 是原子操作——即使 10 个线程同时跑，结果也完全正确。\n"
        "    GET + SET 是非原子操作——并发时数据丢失！\n"
        "    这就是「原子性」的价值——一个命令搞定，不会有中间状态。"
    )

    show_blackboard(client, "并发对比结果")

    # ═══════════════════════════════════════════════════════════
    # 第 10 步: 清理
    # ═══════════════════════════════════════════════════════════
    print_step(10, "清理 — 擦掉黑板")

    flush_db(client)
    show_blackboard(client, "全部清理完毕")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 恭喜！你已经掌握了 Redis 的计数器和原子操作:{Color.RESET}

   {Color.HIGHLIGHT}INCR{Color.RESET}        →  原子加 1（并发安全的计数器）
   {Color.HIGHLIGHT}DECR{Color.RESET}        →  原子减 1
   {Color.HIGHLIGHT}INCRBY{Color.RESET}      →  加任意数值
   {Color.HIGHLIGHT}INCRBYFLOAT{Color.RESET} →  加浮点数
   {Color.HIGHLIGHT}SETNX{Color.RESET}       →  不存在才写（首次写入保护）
   {Color.HIGHLIGHT}GETSET{Color.RESET}      →  写新值，返回旧值
   {Color.HIGHLIGHT}SET NX EX{Color.RESET}   →  带过期的首次写入（分布式锁基石）

{Color.DIM}原子性 = 一个命令内不可分割。Redis 单线程模型让这变得极其简单。{Color.RESET}
""")

    cleanup_demo_keys(client, "demo:*")


if __name__ == "__main__":
    main()
