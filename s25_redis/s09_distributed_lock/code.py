#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s09: 分布式锁 — 黑板上写"使用中"

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - 分布式锁解决了什么问题？
  - SETNX 有什么缺陷？为什么需要 SET NX PX？
  - 为什么释放锁需要 Lua 脚本？
  - 看门狗 Watchdog 是什么？解决了什么问题？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s09_distributed_lock/code.py
"""

import sys
import time
import uuid
import threading
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from s25_redis.utils import (
    Color, get_redis_client,
    show_blackboard, print_step, print_command,
    print_note, print_key_point, print_result,
    section, cleanup_demo_keys,
)


# ═══════════════════════════════════════════════════════════════
# Lua 脚本：安全释放锁
# ═══════════════════════════════════════════════════════════════

# 只有 value 匹配时才 DEL — 防止误删别人的锁
SAFE_UNLOCK_SCRIPT = """
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
"""


# ═══════════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════════

def safe_release(client, lock_key, lock_value):
    """使用 Lua 脚本安全释放锁"""
    return client.eval(SAFE_UNLOCK_SCRIPT, 1, lock_key, lock_value)


def simulate_client(
    client_num: int,
    lock_key: str,
    lock_value: str,
    use_px: bool,
    use_safe_release: bool,
    sleep_time: float = 0.5,
    lock_ttl: int = 3,
):
    """
    模拟一个客户端尝试加锁并执行任务。

    参数:
        client_num: 客户端编号
        lock_key: 锁的 key
        lock_value: 锁的 value（唯一标识）
        use_px: 是否使用过期时间
        use_safe_release: 是否使用 Lua 脚本安全释放
        sleep_time: 模拟业务执行时间
        lock_ttl: 锁过期时间（秒）
    """
    client = get_redis_client()

    if use_px:
        locked = client.set(lock_key, lock_value, nx=True, ex=lock_ttl)
    else:
        locked = bool(client.setnx(lock_key, lock_value))

    if locked:
        print(f"  {Color.SUCCESS}[客户端 {client_num}] 拿到锁！开始处理业务...{Color.RESET}")
        time.sleep(sleep_time)

        if use_safe_release:
            result = safe_release(client, lock_key, lock_value)
            if result:
                print(f"  {Color.SUCCESS}[客户端 {client_num}] 安全释放锁 ✅{Color.RESET}")
            else:
                print(f"  {Color.WARNING}[客户端 {client_num}] 锁已被他人释放或过期{Color.RESET}")
        else:
            client.delete(lock_key)
            print(f"  {Color.WARNING}[客户端 {client_num}] 直接 DEL 释放锁{Color.RESET}")

        return True
    else:
        print(f"  {Color.DIM}[客户端 {client_num}] 没拿到锁，等待中...{Color.RESET}")
        return False


# ═══════════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════════

def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s09: 分布式锁 — 在共享黑板上写「使用中」{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    client = get_redis_client()
    client.flushdb()

    lock_key = "demo:lock:order:1001"

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: 什么是分布式锁
    # ═══════════════════════════════════════════════════════════
    print_step(1, "什么是分布式锁？")

    print_note("想象三个人共用一个资源（比如编辑同一个订单）")
    print_note("没有锁 → 三个人同时操作 → 数据混乱")
    print_note("有锁 → 谁先抢到谁操作 → 其他人排队等待")

    print_command("在黑板上写 '使用中' = 加锁", "")
    print_command("擦掉 '使用中' = 释放锁", "")
    print_command("看到 '使用中' = 等待", "")

    print(f"""
  {Color.BOARD}┌──────────────────────────────────────┐{Color.RESET}
  {Color.BOARD}│  共享黑板                            │{Color.RESET}
  {Color.BOARD}│  {Color.RESET}{Color.HIGHLIGHT}lock:order:1001 = "server-a"     {Color.RESET}{Color.BOARD}│{Color.RESET}
  {Color.BOARD}│  ┌──────────────────┐               │{Color.RESET}
  {Color.BOARD}│  │  👤 服务器 A 在用 │               │{Color.RESET}
  {Color.BOARD}│  └──────────────────┘               │{Color.RESET}
  {Color.BOARD}│                                      │{Color.RESET}
  {Color.BOARD}│  服务器 B → 看到"使用中"→ 等待       │{Color.RESET}
  {Color.BOARD}│  服务器 C → 看到"使用中"→ 等待       │{Color.RESET}
  {Color.BOARD}└──────────────────────────────────────┘{Color.RESET}
""")

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: 第一代 — SETNX（无过期时间）
    # ═══════════════════════════════════════════════════════════
    print_step(2, "第一代：SETNX — 最简单但会死锁")

    lock_value_a = str(uuid.uuid4())

    print_command(f"SETNX {lock_key} '{lock_value_a}'", "客户端 A 尝试加锁")
    result = client.setnx(lock_key, lock_value_a)
    print_result(bool(result), "加锁结果")
    show_blackboard(client, "客户端 A 拿到了锁", lock_key)

    print_command(f"SETNX {lock_key} 'another-value'", "客户端 B 尝试加锁")
    result = client.setnx(lock_key, "another-value")
    print_result(bool(result), "加锁结果")
    print_note("客户端 B 拿不到锁 — 这是对的")

    show_blackboard(client, "客户端 B 被拒 — 锁已被 A 持有", lock_key)

    print_note("但问题来了：如果客户端 A 拿到锁后崩溃了...")
    print_note("这个锁永远留在 Redis 上 — 其他客户端永远拿不到！")
    print(f"  {Color.ERROR}这叫「死锁」— 锁永远不释放{Color.RESET}")

    print_key_point(
        "SETNX 的问题：\n"
        "    SETNX 成功 → 服务器崩溃 → 锁永远留在 Redis 上\n"
        "    → 所有其他服务器都被永久锁在外面\n"
        "    解决：加锁时必须设置过期时间"
    )

    # 清理
    client.delete(lock_key)

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: 第二代 — SET NX PX（原子加锁 + 过期）
    # ═══════════════════════════════════════════════════════════
    print_step(3, "第二代：SET NX PX — 原子加锁 + 过期时间")

    lock_value_c = str(uuid.uuid4())

    print_command(f"SET {lock_key} '{lock_value_c}' NX EX 5",
                  "原子操作：加锁 + 设过期时间 5 秒")
    result = client.set(lock_key, lock_value_c, nx=True, ex=5)
    print_result("OK" if result else "失败", "加锁结果")
    show_blackboard(client, f"锁已设置（TTL: 5 秒）", lock_key)

    print_note("即使客户端 C 崩溃了，5 秒后锁自动释放")

    print_command("等待 6 秒...", "模拟锁过期")
    time.sleep(6)
    show_blackboard(client, "锁已自动过期 — 黑板上没有了", lock_key)

    print_note("现在其他客户端可以拿到锁了")

    lock_value_d = str(uuid.uuid4())
    result = client.set(lock_key, lock_value_d, nx=True, ex=5)
    print_result("OK" if result else "失败", "新客户端加锁")
    show_blackboard(client, "新客户端拿到了锁", lock_key)

    print_key_point(
        "SET NX PX 的好处：\n"
        "    ① NX = key 不存在时才设置（互斥性）\n"
        "    ② EX/PX = 设置过期时间（防止死锁）\n"
        "    ③ 一条命令完成（原子性，没有中间状态）\n"
        "    \n"
        "    千万不要分两步做：SETNX + EXPIRE！\n"
        "    因为两步之间可能崩溃 → 死锁！"
    )

    client.delete(lock_key)

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: 释放锁的坑 — 误删别人的锁
    # ═══════════════════════════════════════════════════════════
    print_step(4, "释放锁的坑 — 可能删掉别人的锁")

    print_note("场景：客户端 A 的锁过期了，客户端 B 拿到了锁")
    print_note("客户端 A 执行完业务后，如果直接 DEL...")

    lock_value_e = "client_e_lock"
    lock_value_f = "client_f_lock"

    # 模拟客户端 A 加锁
    client.set(lock_key, lock_value_e, nx=True, ex=3)
    print_command(f"SET {lock_key} '{lock_value_e}' NX EX 3", "客户端 E 加锁（3 秒过期）")
    show_blackboard(client, "客户端 E 持有锁", lock_key)

    print_note("客户端 E 的业务执行了 4 秒... 锁过期了")
    time.sleep(4)

    # 客户端 F 拿到锁
    client.set(lock_key, lock_value_f, nx=True, ex=5)
    print_command(f"SET {lock_key} '{lock_value_f}' NX EX 5", "锁已过期 → 客户端 F 拿到了锁")
    show_blackboard(client, "客户端 F 现在持有锁", lock_key)

    # 客户端 E 执行完了，想释放锁...
    print_note("客户端 E 执行完了，执行 DEL...")
    print_command(f"DEL {lock_key}", "客户端 E 释放锁")
    client.delete(lock_key)
    show_blackboard(client, "灾难！锁被 E 删掉了，F 的锁没了！", lock_key)

    print(f"  {Color.ERROR}⚠ 客户端 E 把客户端 F 的锁误删了！{Color.RESET}")
    print_note("客户端 F 还在处理订单，锁却没了 → 其他客户端也能处理同一订单了")

    print_step(4.1, "解决方案：Lua 脚本安全释放锁")

    client.delete(lock_key)

    # 重新演示：客户端 G 加锁
    lock_value_g = "client_g_lock_" + str(uuid.uuid4())
    client.set(lock_key, lock_value_g, nx=True, ex=3)
    show_blackboard(client, "客户端 G 持有锁（带唯一标识）", lock_key)

    time.sleep(4)  # 锁过期

    lock_value_h = "client_h_lock_" + str(uuid.uuid4())
    client.set(lock_key, lock_value_h, nx=True, ex=5)

    print_note("客户端 G 用 Lua 脚本释放锁...")
    result = safe_release(client, lock_key, lock_value_g)
    if result:
        print(f"  {Color.SUCCESS}锁被释放{Color.RESET}")
    else:
        print(f"  {Color.WARNING}Lua 脚本发现 value 不匹配 — 拒绝释放！{Color.RESET}")
        print(f"  {Color.SUCCESS}锁还在，客户端 H 的锁没有被误删 ✅{Color.RESET}")

    show_blackboard(client, "锁完好无损 — Lua 脚本保护了 H 的锁", lock_key)

    # 客户端 H 自己的释放
    result = safe_release(client, lock_key, lock_value_h)
    print_result(bool(result), "客户端 H 自己的释放")
    show_blackboard(client, "H 正常释放锁 — 黑板上清空了", lock_key)

    print_key_point(
        "安全释放锁的 Lua 脚本逻辑：\n"
        "    if redis.call('GET', KEYS[1]) == ARGV[1] then\n"
        "        return redis.call('DEL', KEYS[1])\n"
        "    else\n"
        "        return 0\n"
        "    end\n"
        "    \n"
        "    先校验 value（是不是自己的锁）→ 再 DEL\n"
        "    Lua 脚本保证这两个操作原子执行，不会被其他命令打断"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: 模拟高并发竞争锁
    # ═══════════════════════════════════════════════════════════
    print_step(5, "模拟高并发 — 多个客户端竞争同一把锁")

    lock_key = "demo:lock:resource"
    client.delete(lock_key)

    print_note("5 个客户端同时竞争同一把锁")
    print_note("使用 SET NX PX + Lua 安全释放")

    threads = []
    results = {}

    def competitive_lock(client_id: int):
        """并发竞争锁"""
        value = f"client_{client_id}_{uuid.uuid4().hex[:8]}"
        locked = client.set(lock_key, value, nx=True, ex=3)
        if locked:
            print(f"  {Color.SUCCESS}[线程 {client_id}] 🏆 拿到了锁！{Color.RESET}")
            time.sleep(0.3)  # 模拟业务处理
            safe_release(client, lock_key, value)
            results[client_id] = True
        else:
            print(f"  {Color.DIM}[线程 {client_id}] 没抢到锁，等待下次{Color.RESET}")
            results[client_id] = False

    for i in range(5):
        t = threading.Thread(target=competitive_lock, args=(i,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    winners = [k for k, v in results.items() if v]
    print(f"\n  {Color.HIGHLIGHT}结果：{len(winners)} 个客户端成功拿到了锁（一次一个）{Color.RESET}")
    print_note("每次只有一个客户端能拿到锁 — 这就是互斥性")

    print_key_point(
        "分布式锁的核心要求：\n"
        "    ① 互斥性 — 同一时刻只有一个人能拿到锁\n"
        "    ② 安全性 — 不会死锁（有超时机制）\n"
        "    ③ 可用性 — 大多数情况下都能拿到锁\n"
        "    ④ 释放安全性 — 只能释放自己的锁"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: 看门狗概念演示
    # ═══════════════════════════════════════════════════════════
    print_step(6, "看门狗 (Watchdog) — 自动续期")

    print_note("场景：锁设了 5 秒过期，但业务可能超过 5 秒")
    print_note("看门狗线程每隔一段时间检查并续期")

    watchdog_key = "demo:lock:watchdog"
    watchdog_value = "watchdog_demo"
    watchdog_running = True

    def watchdog_worker():
        """看门狗线程：每 2 秒续期一次"""
        wc = get_redis_client()
        while watchdog_running:
            ttl = wc.ttl(watchdog_key)
            if ttl > 0 and ttl < 3:  # TTL 小于 3 秒时续期
                wc.expire(watchdog_key, 5)
                print(f"  {Color.HIGHLIGHT}[看门狗] 续期成功！TTL 重置为 5 秒{Color.RESET}")
            elif ttl > 0:
                print(f"  {Color.DIM}[看门狗] TTL 还剩 {ttl}s，不需要续期{Color.RESET}")
            else:
                print(f"  {Color.WARNING}[看门狗] 锁已过期（或已被释放）{Color.RESET}")
                break
            time.sleep(2)

    # 加锁
    client.set(watchdog_key, watchdog_value, nx=True, ex=5)
    show_blackboard(client, "加锁成功，TTL = 5 秒", watchdog_key)

    # 启动看门狗
    wd_thread = threading.Thread(target=watchdog_worker, daemon=True)
    wd_thread.start()

    print_note("模拟业务执行 8 秒（超过锁的 5 秒 TTL）")
    for second in range(8):
        time.sleep(1)
        print(f"  {Color.DIM}业务执行中... {second + 1}/8 秒{Color.RESET}")

    # 停止看门狗
    watchdog_running = False
    wd_thread.join(timeout=1)

    print_note("业务执行完毕，释放锁")
    safe_release(client, watchdog_key, watchdog_value)
    show_blackboard(client, "锁已释放", watchdog_key)

    print_note("如果没有看门狗 → 第 5 秒锁就过期了 → 其他进程抢到锁 → 数据混乱")
    print_note("看门狗 = 在业务运行期间不断续期，保证锁不会提前过期")

    print_key_point(
        "看门狗的作用：\n"
        "    业务可能比预期的慢 → 锁提前过期 → 并发问题\n"
        "    看门狗在后台不断检查 TTL，发现快过期了就续期\n"
        "    如果服务器挂了 → 看门狗线程也挂了 → 不再续期 → 锁自然过期\n"
        "    \n"
        "    Redisson (Java) 内置看门狗，叫 'watchdog'\n"
        "    一般每 10 秒检查一次，续期到 30 秒"
    )

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 你掌握了分布式锁的进化之路！{Color.RESET}

   {Color.HIGHLIGHT}SETNX{Color.RESET}          →  第一代加锁 — 会死锁 ❌
   {Color.HIGHLIGHT}SET NX PX{Color.RESET}      →  第二代 — 原子加锁 + 过期 ✅
   {Color.HIGHLIGHT}Lua 脚本释放{Color.RESET}   →  安全释放，不误删别人的锁
   {Color.HIGHLIGHT}看门狗{Color.RESET}         →  自动续期，防止业务没做完锁过期
   {Color.HIGHLIGHT}Redlock{Color.RESET}        →  多节点场景的锁算法

{Color.DIM}核心原则：加锁要原子（SET NX PX），释放要校验（Lua 脚本），长时间任务要看门狗。{Color.RESET}
""")

    cleanup_demo_keys(client, "demo:*")
    client.flushdb()


if __name__ == "__main__":
    main()
