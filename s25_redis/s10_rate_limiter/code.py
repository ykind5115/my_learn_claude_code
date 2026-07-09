#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s10: 限流与滑动窗口 — 黑板上画计数器

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - 固定窗口有什么问题？什么是边界尖峰？
  - 滑动窗口怎么用 ZSET 实现？
  - 令牌桶和固定窗口/滑动窗口有什么不同？
  - 三种限流方案各适用于什么场景？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s10_rate_limiter/code.py
"""

import sys
import time
import math
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from s25_redis.utils import (
    Color, get_redis_client,
    show_blackboard, print_step, print_command,
    print_note, print_key_point, print_result,
    section, cleanup_demo_keys,
)


def print_rate_result(allowed: bool, request_id: int, detail: str = ""):
    """打印限流结果"""
    if allowed:
        print(f"  {Color.SUCCESS}  ✅ 请求 #{request_id} → 允许{Color.RESET} {detail}")
    else:
        print(f"  {Color.ERROR}  ❌ 请求 #{request_id} → 拒绝{Color.RESET} {detail}")


# ═══════════════════════════════════════════════════════════════
# 方案 1：固定窗口限流
# ═══════════════════════════════════════════════════════════════

def fixed_window_check(client, user_id: str, max_req: int = 5, window_sec: int = 10) -> bool:
    """
    固定窗口限流 — 使用 INCR + EXPIRE。

    窗口 key = rate:fixed:{user_id}:{当前时间窗口}
    实现简单，但有边界尖峰问题。
    """
    window = int(time.time() / window_sec)
    key = f"demo:rate:fixed:{user_id}:{window}"

    count = client.incr(key)
    if count == 1:
        client.expire(key, window_sec + 2)

    return count <= max_req


# ═══════════════════════════════════════════════════════════════
# 方案 2：滑动窗口限流
# ═══════════════════════════════════════════════════════════════

def sliding_window_check(client, user_id: str, max_req: int = 5, window_sec: int = 10) -> bool:
    """
    滑动窗口限流 — 使用 ZSET 记录每个请求的时间戳。

    每次请求：
      1. ZREMRANGEBYSCORE 移除窗口外的时间戳
      2. ZADD 添加当前请求
      3. ZCARD 统计窗口内请求数

    精准但内存开销大（每个请求都在 ZSET 中占一个元素）。
    """
    key = f"demo:rate:sliding:{user_id}"
    now = time.time()
    window_start = now - window_sec

    pipe = client.pipeline()

    # 移除窗口外的时间戳
    pipe.zremrangebyscore(key, 0, window_start)

    # 添加当前请求（member = 时间戳字符串，score = 时间戳）
    pipe.zadd(key, {str(now): now})

    # 设置过期时间
    pipe.expire(key, window_sec + 10)

    # 统计窗口内请求数
    pipe.zcard(key)

    results = pipe.execute()
    count = results[-1]

    return count <= max_req


# ═══════════════════════════════════════════════════════════════
# 方案 3：令牌桶限流
# ═══════════════════════════════════════════════════════════════

def token_bucket_check(client, user_id: str, capacity: int = 5, refill_rate: float = 0.5) -> bool:
    """
    令牌桶限流 — 使用 Hash 存储令牌数和上次补充时间。

    不真的"放令牌"，而是通过时间差计算新增了多少令牌：
      new_tokens = min(capacity, old_tokens + (now - last_time) * refill_rate)
    """
    key = f"demo:rate:token:{user_id}"
    now = time.time()

    data = client.hgetall(key)
    if not data:
        # 第一次请求 — 初始化
        tokens = capacity - 1
        client.hset(key, "tokens", tokens)
        client.hset(key, "last_refill", now)
        client.expire(key, 30)
        return True

    last_tokens = float(data.get(b"tokens", capacity))
    last_time = float(data.get(b"last_refill", now))

    # 计算应该补充多少令牌
    delta = now - last_time
    new_tokens = min(capacity, last_tokens + delta * refill_rate)

    if new_tokens >= 1:
        client.hset(key, "tokens", new_tokens - 1)
        client.hset(key, "last_refill", now)
        return True
    else:
        client.hset(key, "tokens", 0)
        client.hset(key, "last_refill", now)
        return False


# ═══════════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════════

def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s10: 限流与滑动窗口 — 黑板上画计数器{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    client = get_redis_client()
    client.flushdb()

    user = "zhangsan"

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: 固定窗口限流
    # ═══════════════════════════════════════════════════════════
    print_step(1, "固定窗口限流 — INCR + EXPIRE")

    window = int(time.time() / 10)
    print_note(f"上限 5 次 / 10 秒")
    print_note(f"当前窗口: {window}")

    for i in range(1, 8):
        allowed = fixed_window_check(client, user, max_req=5, window_sec=10)
        detail = f"(key=demo:rate:fixed:{user}:{int(time.time() / 10)})"
        print_rate_result(allowed, i, detail)
        time.sleep(0.1)

    show_blackboard(client, "固定窗口计数器状态", "demo:rate:fixed:*")

    print_key_point(
        "固定窗口的工作方式：\n"
        "    key = rate:limit:user:<时间窗口编号>\n"
        "    INCR 递增 → 达到上限则拒绝\n"
        "    第一次 INCR 时设置 EXPIRE\n"
        "    \n"
        "    优点：实现极其简单，内存开销极低\n"
        "    缺点：有边界尖峰问题（见下一步）"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: 边界尖峰演示
    # ═══════════════════════════════════════════════════════════
    print_step(2, "固定窗口的边界尖峰问题")

    print_note("场景：窗口每 5 秒切换，上限 3 次/窗口")
    print_note("如果所有请求集中在窗口切换的瞬间...")

    # 等待靠近窗口边界
    now = time.time()
    window_size = 5
    current_window = int(now / window_size)
    next_window_start = (current_window + 1) * window_size
    wait_time = max(0, next_window_start - now - 0.1)

    if wait_time > 0:
        print_note(f"等待窗口边界... ({wait_time:.1f} 秒后边界)")
        time.sleep(wait_time)

    # 在边界附近快速发 6 个请求
    print_note("边界处快速发送 6 个请求...")
    for i in range(1, 7):
        allowed = fixed_window_check(client, "burst_user", max_req=3, window_sec=5)
        w = int(time.time() / 5)
        detail = f"(窗口={w})"
        print_rate_result(allowed, i, detail)
        time.sleep(0.05)

    print_note("6 个请求通过了！因为它们在两个窗口之间分布...")
    print_note("窗口 1 的 3 次 + 窗口 2 的 3 次 = 6 次")
    print_note("但实际时间间隔只有 0.3 秒 — 瞬时 QPS 远超限制！")

    print_key_point(
        "边界尖峰 (Boundary Burst)：\n"
        "    固定窗口在窗口切换的瞬间，可以通过「双倍」的流量\n"
        "    因为窗口 1 的额度 + 窗口 2 的额度在瞬间可用\n"
        "    \n"
        "    虽然不是大问题（长期平均仍是上限），\n"
        "    但对某些场景（如秒杀、抢票）可能造成冲击"
    )

    cleanup_demo_keys(client, "demo:rate:fixed:*")

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: 滑动窗口限流
    # ═══════════════════════════════════════════════════════════
    print_step(3, "滑动窗口限流 — ZSET + 时间戳")

    print_note("上限 5 次 / 10 秒")
    print_note("每个请求在 ZSET 中记录时间戳")

    for i in range(1, 8):
        allowed = sliding_window_check(client, user, max_req=5, window_sec=10)
        now = time.time()
        print_rate_result(allowed, i, "")
        time.sleep(0.3)

    show_blackboard(client, "滑动窗口 ZSET 状态", "demo:rate:sliding:*")

    print_note("观察 ZSET 中的 members — 每个 member 是一个请求的时间戳")
    key = f"demo:rate:sliding:{user}"
    members = client.zrange(key, 0, -1, withscores=True)
    for member, score in members:
        print(f"    {Color.DIM}请求时间: {time.strftime('%H:%M:%S', time.localtime(score))}{Color.RESET}")

    print_key_point(
        "滑动窗口 vs 固定窗口：\n"
        "    滑动窗口不存在边界尖峰问题\n"
        "    窗口始终是「当前时间往前推 N 秒」，而不是整分钟/整秒\n"
        "    \n"
        "    代价：每个请求都在 ZSET 中占一个元素\n"
        "    高并发时可以考虑按秒聚合优化"
    )

    cleanup_demo_keys(client, "demo:rate:sliding:*")

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: 滑动窗口边界测试 — 验证无边界尖峰
    # ═══════════════════════════════════════════════════════════
    print_step(4, "验证：滑动窗口无边界尖峰")

    print_note("同样在边界附近快速发请求，观察滑动窗口的行为")

    # 等待窗口边界
    now = time.time()
    window_size = 5
    current_window = int(now / window_size)
    next_window_start = (current_window + 1) * window_size
    wait_time = max(0, next_window_start - now - 0.1)

    if wait_time > 0:
        print_note(f"等待窗口边界... ({wait_time:.1f} 秒后)")
        time.sleep(wait_time)

    for i in range(1, 7):
        allowed = sliding_window_check(client, "burst_user_sliding", max_req=3, window_sec=5)
        print_rate_result(allowed, i, "")
        time.sleep(0.05)

    print_note("滑动窗口始终以「当前时间往前推 N 秒」为单位")
    print_note("不管窗口边界在哪，都是最近 N 秒内的请求数")
    print_note("边界尖峰问题自然消失 ✅")

    cleanup_demo_keys(client, "demo:rate:sliding:*")

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: 令牌桶限流
    # ═══════════════════════════════════════════════════════════
    print_step(5, "令牌桶限流 — 匀速放令牌")

    print_note("容量 5，每秒补充 0.5 个令牌（每 2 秒 1 个）")

    for i in range(1, 10):
        allowed = token_bucket_check(client, user, capacity=5, refill_rate=0.5)
        print_rate_result(allowed, i, "")
        time.sleep(0.3)

    show_blackboard(client, "令牌桶状态", "demo:rate:token:*")

    # 查看令牌桶的详细状态
    key = f"demo:rate:token:{user}"
    data = client.hgetall(key)
    if data:
        tokens = float(data.get(b"tokens", 0))
        last = float(data.get(b"last_refill", 0))
        print(f"\n  {Color.DIM}令牌桶详情:{Color.RESET}")
        print(f"    {Color.YELLOW}剩余令牌: {tokens:.2f}{Color.RESET}")
        print(f"    {Color.YELLOW}上次补充: {time.strftime('%H:%M:%S', time.localtime(last))}{Color.RESET}")

    print_note("前 5 个请求立即通过（桶是满的）")
    print_note("之后请求被拒绝，直到有新令牌补充")

    # 展示令牌桶的"积攒"特性
    print_step(5.1, "令牌桶的突发能力")

    cleanup_demo_keys(client, "demo:rate:token:*")

    print_note("等待 6 秒，让桶重新蓄满（每秒 1 个，容量 5）")
    for i in range(6, 0, -1):
        time.sleep(1)
        print(f"  {Color.DIM}蓄力中... {i} 秒后满{Color.RESET}")

    print_note("桶蓄满了！现在瞬间发送 8 个请求...")
    for i in range(1, 9):
        allowed = token_bucket_check(client, "burst_test", capacity=5, refill_rate=1.0)
        print_rate_result(allowed, i, "")
        time.sleep(0.05)

    print_note("前 5 个请求通过（桶里的令牌），后 3 个被拒绝")
    print_note("这就是令牌桶的「允许突发」特性")

    print_key_point(
        "三种限流方案对比：\n"
        "    固定窗口  → 简单粗暴，有边界尖峰\n"
        "    滑动窗口  → 精准限流，内存开销大\n"
        "    令牌桶    → 匀速放行，允许突发\n"
        "    \n"
        "    选型建议：\n"
        "    - 大部分 API 限流 → 固定窗口就够了\n"
        "    - 需要精确控制   → 滑动窗口\n"
        "    - 需要流量整形   → 令牌桶"
    )

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 你掌握了三种 Redis 限流方案！{Color.RESET}

   {Color.HIGHLIGHT}固定窗口{Color.RESET}    →  INCR + EXPIRE，最简单，有边界尖峰
   {Color.HIGHLIGHT}滑动窗口{Color.RESET}   →  ZSET + 时间戳，无边界尖峰，更精准
   {Color.HIGHLIGHT}令牌桶{Color.RESET}     →  Hash + 时间差计算，允许突发

{Color.DIM}关键记忆：固定窗口容易有边界尖峰，滑动窗口总能精确统计最近 N 秒的请求数。{Color.RESET}
""")

    cleanup_demo_keys(client, "demo:rate:*")
    client.flushdb()


if __name__ == "__main__":
    main()
