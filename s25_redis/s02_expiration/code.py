#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s02: 消失的墨水 — 让数据自动过期

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - EXPIRE / TTL / PERSIST 怎么配合使用？
  - SETEX 为什么比 SET + EXPIRE 更安全？
  - TTL=-1 和 TTL=-2 有什么区别？
  - Redis 怎么自动处理过期键（惰性 + 定期策略）？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s02_expiration/code.py
"""

import sys
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
    print(f"{Color.HEADER}  s02: 消失的墨水 — 让数据自动过期{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # 连接 Redis
    client = get_redis_client()

    # 清理残留
    cleanup_demo_keys(client, "demo:*")
    for key in ["captcha", "token", "session", "coupon", "watch"]:
        client.delete(key)

    # 确保黑板干净
    client.flushdb()

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: SET + EXPIRE — 用消失墨水写字
    # ═══════════════════════════════════════════════════════════
    print_step(1, "SET + EXPIRE — 用消失墨水写字")

    print_command('SET captcha "4382"', "先正常写入")
    client.set("captcha", "4382")
    show_blackboard(client, "SET captcha 之后")

    print_command("EXPIRE captcha 10", "给 captcha 加上消失墨水——10 秒后自动消失")
    result = client.expire("captcha", 10)
    print_result(result, "EXPIRE captcha 10")
    show_blackboard(client, "EXPIRE 之后 — 看到 TTL 倒计时了吗？")

    print_key_point(
        "EXPIRE 给已有 key 加上过期时间。\n"
        "    效果就像用「消失墨水」写字——到时间自动擦除。\n"
        "    当你调用 EXPIRE 时，Redis 开始倒计时。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: TTL — 看还剩多少秒消失
    # ═══════════════════════════════════════════════════════════
    print_step(2, "TTL — 看还剩多少秒消失")

    print_command("TTL captcha", "看看 captcha 还剩几秒消失")
    ttl = client.ttl("captcha")
    print_result(ttl, "TTL captcha")
    print(f"  → 还剩 {Color.HIGHLIGHT}{ttl}{Color.RESET} 秒消失")

    # 倒计时展示
    print_command("TTL captcha (每隔 1 秒看一次)", "观察倒计时递减")
    for i in range(5):
        ttl = client.ttl("captcha")
        if ttl <= 0:
            print(f"  → 第 {i + 1} 秒: {Color.ERROR}TTL = {ttl} — key 已消失！{Color.RESET}")
            break
        print(f"  → 第 {i + 1} 秒: TTL = {Color.HIGHLIGHT}{ttl}{Color.RESET}")
        time.sleep(1)

    show_blackboard(client, "倒计时后 — captcha 已经自动消失了？")

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: TTL 的三种返回值
    # ═══════════════════════════════════════════════════════════
    print_step(3, "TTL 的三种返回值 — -1 和 -2 的含义")

    # TTL = -1: 存在但未设过期
    client.set("permanent", "我永不过期")
    print_command("SET permanent '我永不过期'", "写入一个永久 key")
    print_command("TTL permanent", "看它的 TTL")
    ttl = client.ttl("permanent")
    print_result(f"{ttl} (key 存在，但没设过期)", "TTL permanent")
    print(f"  {Color.DIM}→ TTL = -1 表示 key 存在且永久保存{Color.RESET}")

    # TTL = -2: key 不存在
    print_command("TTL nonexistent", "看一个不存在的 key 的 TTL")
    ttl = client.ttl("nonexistent")
    print_result(f"{ttl} (key 不存在)", "TTL nonexistent")
    print(f"  {Color.DIM}→ TTL = -2 表示 key 不存在或已过期{Color.RESET}")

    print_key_point(
        "TTL 的三种情况:\n"
        "    TTL > 0  → 还剩 N 秒消失\n"
        "    TTL = -1 → key 存在，永久保存（没有设过期）\n"
        "    TTL = -2 → key 不存在或已过期被删除了"
    )

    show_blackboard(client, "当前黑板")

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: PERSIST — 取消过期，恢复成普通墨水
    # ═══════════════════════════════════════════════════════════
    print_step(4, "PERSIST — 取消过期，恢复成普通墨水")

    print_command('SETEX session "abc123" 30', "写一个 30 秒过期的 session")
    client.setex("session", 30, "abc123")
    print_command("TTL session", "确认它在倒计时")
    ttl = client.ttl("session")
    print_result(ttl, "TTL session")

    print_command("PERSIST session", "擦掉消失墨水——取消过期！")
    result = client.persist("session")
    print_result(result, "PERSIST session")

    print_command("TTL session", "确认 TTL 变成 -1")
    ttl = client.ttl("session")
    print_result(f"{ttl} (变为永久保存)", "TTL session")

    print_note("PERSIST 成功返回 1，如果 key 本来就没有过期返回 0")
    show_blackboard(client, "PERSIST 之后 — session 永不过期了")

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: EXPIREAT — 指定具体消失时间
    # ═══════════════════════════════════════════════════════════
    print_step(5, "EXPIREAT — 指定具体消失时间")

    # 让 coupon 在 30 秒后过期（用未来时间戳）
    future_ts = int(time.time()) + 30
    print_command(f'SET coupon "DISCOUNT50"')
    client.set("coupon", "DISCOUNT50")
    print_command(f"EXPIREAT coupon {future_ts}", f"让 coupon 在时间戳 {future_ts} 时过期（30 秒后）")
    result = client.expireat("coupon", future_ts)
    print_result(result, "EXPIREAT coupon")

    ttl = client.ttl("coupon")
    print_result(ttl, "TTL coupon (大约 30 秒)")

    print_note("EXPIREAT 接受 Unix 时间戳（秒级精度）。")
    print_note("适合「今晚 12 点整过期」「明天 8 点整过期」这类场景。")

    show_blackboard(client, "EXPIREAT 之后")

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: SETEX — 写 + 消失一步到位
    # ═══════════════════════════════════════════════════════════
    print_step(6, "SETEX — 写 + 消失一步到位")

    print_command('SETEX captcha 15 "7291"', "SET + EXPIRE 合二为一——15 秒后消失")
    client.setex("captcha", 15, "7291")
    show_blackboard(client, "SETEX captcha 15 '7291'")

    print_key_point(
        "SETEX 的优势:\n"
        "    1. 原子操作——不会出现 SET 成功但 EXPIRE 失败的中间状态\n"
        "    2. 省一次网络往返\n"
        "    \n"
        "    对于缓存和验证码场景，SETEX 是最佳选择。"
    )

    # 检查 SETEX 的 TTL
    print_command("TTL captcha", "确认 SETEX 自动设了过期")
    ttl = client.ttl("captcha")
    print_result(ttl, "TTL captcha")

    # ═══════════════════════════════════════════════════════════
    # 第 7 步: 演示「惰性删除」
    # ═══════════════════════════════════════════════════════════
    print_step(7, "惰性删除演示 — 过期 key 在 GET 时被删除")

    print_command('SETEX lazy_demo 3 "我很快会消失"', "设一个 3 秒过期的 key")
    client.setex("lazy_demo", 3, "我很快会消失")
    show_blackboard(client, "lazy_demo 刚写入")

    print(f"  {Color.DIM}等待 4 秒让 key 过期...{Color.RESET}")
    time.sleep(4)

    print_command("GET lazy_demo", "过期后再去读——惰性删除触发")
    result = client.get("lazy_demo")
    print_result(result, "GET lazy_demo")
    print(f"  → {Color.DIM}key 已过期，在被访问时被 Redis 惰性删除{Color.RESET}")
    print_note("惰性删除：当访问一个过期 key 时，Redis 顺手把它删了再返回 nil。")

    # ═══════════════════════════════════════════════════════════
    # 第 8 步: 批量不同过期时间的 key
    # ═══════════════════════════════════════════════════════════
    print_step(8, "批量不同过期时间的 key — 每行墨水消失速度不同")

    client.setex("cache:hot", 10, "热门数据（10 秒过期）")
    client.setex("cache:warm", 30, "温热数据（30 秒过期）")
    client.setex("cache:cold", 60, "冷数据（60 秒过期）")
    client.set("cache:perm", "永久数据（永不过期）")
    print(f"  {Color.SUCCESS}✅ 创建了 4 个不同过期时间的 key{Color.RESET}")

    show_blackboard(client, "相同结构、不同 TTL 的 key")

    print_command("TTL cache:hot / cache:warm / cache:cold / cache:perm")
    for key in ["cache:hot", "cache:warm", "cache:cold", "cache:perm"]:
        ttl = client.ttl(key)
        ttl_label = f"{ttl}s" if ttl > 0 else ("永久" if ttl == -1 else "已过期")
        print(f"  → {Color.YELLOW}{key:<20}{Color.RESET} TTL = {Color.HIGHLIGHT}{ttl_label}{Color.RESET}")

    print_note("看到区别了吗？每个 key 可以有自己的过期时间。")
    print_note("这就是为什么 Redis 能用于不同时效的数据缓存。")

    # ═══════════════════════════════════════════════════════════
    # 第 9 步: 清理
    # ═══════════════════════════════════════════════════════════
    print_step(9, "清理 — 擦掉黑板")

    flush_db(client)
    show_blackboard(client, "全部清理完毕")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 恭喜！你已经掌握了 Redis 的过期机制:{Color.RESET}

   {Color.HIGHLIGHT}EXPIRE{Color.RESET}    →  用消失墨水写字（设过期秒数）
   {Color.HIGHLIGHT}TTL{Color.RESET}       →  看还剩多少秒消失
   {Color.HIGHLIGHT}PERSIST{Color.RESET}   →  擦掉消失墨水（取消过期）
   {Color.HIGHLIGHT}EXPIREAT{Color.RESET}  →  指定具体消失时刻
   {Color.HIGHLIGHT}SETEX{Color.RESET}     →  写 + 消失一步到位

{Color.DIM}每个 key 可以独立控制「什么时候消失」——这就是缓存的基石。{Color.RESET}
""")

    cleanup_demo_keys(client, "demo:*")


if __name__ == "__main__":
    main()
