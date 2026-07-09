#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s16: Pipeline 与事务 — 批量操作与原子执行

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - Pipeline 为什么快？它解决了什么问题？
  - Pipeline 和事务有什么区别？
  - WATCH 乐观锁是怎么工作的？
  - Lua 脚本在 Redis 中扮演什么角色？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s16_pipeline_tx/code.py
"""

import sys
import time
from pathlib import Path

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
)


def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s16: Pipeline 与事务 — 批量操作与原子执行{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    client = get_redis_client()
    # 清理可能遗留的 key
    for key in ["counter", "stock", "pipeline_test", "tx_test",
                 "watch_test", "account:a", "account:b",
                 "lua_test", "mystock", "flag"]:
        client.delete(key)
    cleanup_demo_keys(client, "demo:*")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: Pipeline 性能对比
    # ═══════════════════════════════════════════════════════════
    print_step(1, "Pipeline vs 逐个发送 — 性能对比")

    print_note("模拟 100 次 SET 操作，对比 Pipeline 和逐个发送的耗时")

    N = 100

    # --- 逐个发送 ---
    section("逐个发送 100 个命令")

    start = time.perf_counter()
    for i in range(N):
        client.set(f"pipeline_test:{i}", f"value-{i}")
    end = time.perf_counter()
    sequential_time = end - start
    print(f"  逐个发送耗时: {Color.HIGHLIGHT}{sequential_time:.3f}s{Color.RESET}")

    # --- Pipeline ---
    section("Pipeline 批量发送 100 个命令")

    pipe = client.pipeline()
    start = time.perf_counter()
    for i in range(N):
        pipe.set(f"pipeline_test:{i}", f"value-{i}")
    pipe.execute()
    end = time.perf_counter()
    pipeline_time = end - start
    print(f"  Pipeline 耗时: {Color.HIGHLIGHT}{pipeline_time:.3f}s{Color.RESET}")

    speedup = sequential_time / pipeline_time if pipeline_time > 0 else 0
    print(f"\n  {Color.SUCCESS}🚀 Pipeline 快了约 {speedup:.1f} 倍！{Color.RESET}")
    print_note("Pipeline 减少的是网络往返次数，不是 Redis 执行命令的时间。")

    # --- Pipeline 结果顺序 ---
    section("Pipeline 返回结果顺序")

    print_note("Pipeline 的返回顺序和命令发送顺序一致")
    pipe = client.pipeline()
    pipe.set("demo:a", "first")
    pipe.get("demo:a")
    pipe.set("demo:b", "second")
    pipe.get("demo:b")
    results = pipe.execute()

    print(f"  命令顺序: SET a → GET a → SET b → GET b")
    print(f"  返回结果: {results}")
    print(f"  结果[0] (SET a): {results[0]}")
    print(f"  结果[1] (GET a): {results[1]}")
    print(f"  结果[2] (SET b): {results[2]}")
    print(f"  结果[3] (GET b): {results[3]}")

    print_key_point(
        "Pipeline 将所有命令打包一次发送，减少网络 RTT。\n"
        "    但 Pipeline 不是事务——命令之间可以被其他客户端的命令插入。\n"
        "    如果要求原子性（不被中断），要用 MULTI/EXEC 事务。"
    )

    show_blackboard(client, "Pipeline 写入后")

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: MULTI/EXEC 事务
    # ═══════════════════════════════════════════════════════════
    print_step(2, "MULTI/EXEC 事务 — 原子执行一组命令")

    print_note("事务 = 一组命令打包执行，中间不插入其他客户端的命令")

    section("开启事务，执行多个命令")

    # 使用 pipeline(transaction=True) 来模拟 MULTI/EXEC
    pipe = client.pipeline(transaction=True)
    pipe.multi()

    print_command("MULTI", "开启事务模式")
    pipe.set("tx_test", "事务的值")
    print_command('SET tx_test "事务的值"', "命令入队")
    pipe.incr("counter")
    print_command("INCR counter", "命令入队")
    pipe.set("flag", "done")
    print_command('SET flag "done"', "命令入队")

    print_command("EXEC", "执行事务 —— 所有命令一次性执行")
    results = pipe.execute()
    print(f"  事务结果: {results}")
    print(f"  → SET tx_test: {results[0]}")
    print(f"  → INCR counter: {results[1]}")
    print(f"  → SET flag: {results[2]}")

    show_blackboard(client, "事务执行后")

    print_key_point(
        "MULTI/EXEC 保证一组命令原子执行。\n"
        "    但 Redis 事务不支持回滚——如果某个命令失败，前面的不会撤销。"
    )

    # --- 事务不保证回滚 ---
    section("演示：事务不保证回滚")

    pipe = client.pipeline(transaction=True)
    pipe.multi()
    pipe.set("tx_test", "新值")       # 这个会成功
    pipe.incr("tx_test")              # 错误！tx_test 不是整数，但 INCR 会失败
    pipe.set("tx_test", "最终值")     # 这个不会执行

    print_command('SET tx_test "新值"', "✅ 会成功")
    print_command("INCR tx_test", "❌ 会失败（字符串不能 INCR）")
    print_command('SET tx_test "最终值"', "❓ 这个还会执行吗？")
    results = pipe.execute()
    print(f"  事务结果: {results}")
    print(f"  → SET tx_test '新值': {results[0]}")
    print(f"  → INCR tx_test: {results[1]}  ← 失败，但前面的 SET 没有回滚！")

    # 查看实际值
    val = client.get("tx_test")
    print(f"\n  tx_test 的值 = \"{val}\"")
    print_note("INCR 失败后，前面的 SET 并没有回滚！和 MySQL 事务不一样。")

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: WATCH 乐观锁
    # ═══════════════════════════════════════════════════════════
    print_step(3, "WATCH 乐观锁 — 监视 key 的变化")

    client.set("stock", 10)
    print_command('SET stock 10', "初始化库存为 10")
    show_blackboard(client, "初始化 stock")

    section("WATCH + 事务：模拟乐观锁")

    # 模拟第一个客户端（你）
    c1 = get_redis_client()

    print_note("第一步：WATCH stock，监视库存变化")
    c1.watch("stock")
    current_stock = int(c1.get("stock"))
    print(f"  当前库存: {current_stock}")
    print(f"  准备扣减 1 件商品...")

    # 模拟第二个客户端（其他人）修改了 stock
    section("⚡ 另一个客户端修改了 stock！")
    print_command("SET stock 5", "其他人把库存改成 5")
    client.set("stock", 5)   # 从主客户端修改
    print(f"  stock 被改为: {client.get('stock')}")

    section("执行事务 — WATCH 检测到变化")

    # 执行事务（c1 已经 WATCH 了 stock）
    pipe = c1.pipeline(transaction=True)
    pipe.multi()
    new_stock = current_stock - 1
    pipe.set("stock", new_stock)
    print_command(f"MULTI → SET stock {new_stock} → EXEC", "执行事务")
    result = pipe.execute()
    print(f"  EXEC 结果: {result}")

    if result is None or result == ():
        print(f"\n  {Color.WARNING}⚠ 事务被放弃！{Color.RESET}")
        print(f"  因为 stock 被其他人修改了，WATCH 发现变化，拒绝执行事务。")
    else:
        print(f"\n  {Color.SUCCESS}✅ 事务成功执行！stock = {client.get('stock')}{Color.RESET}")

    show_blackboard(client, "WATCH 实验后")

    print_key_point(
        "WATCH 是乐观锁（Optimistic Lock）：\n"
        "    - 如果你 WATCH 的 key 在事务执行前被修改\n"
        "    - 你的 EXEC 会返回 nil，事务被放弃\n"
        "    - 你需要重试整个操作（重新 WATCH → GET → MULTI → EXEC）"
    )

    c1.close()

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: Lua 脚本示例
    # ═══════════════════════════════════════════════════════════
    print_step(4, "Lua 脚本 — 在 Redis 内部执行逻辑")

    client.set("lua_test", "hello")

    section("简单 Lua 脚本：返回传入的参数")

    script = "return {KEYS[1], ARGV[1], ARGV[2]}"
    print_command(f'EVAL "{script}" 1 mykey arg1 arg2')
    result = client.eval(script, 1, "mykey", "arg1", "arg2")
    print(f"  结果: {result}")
    print_note("Lua 脚本可以访问 KEYS 和 ARGV 两个数组")

    section("实用 Lua 脚本：检查并更新")

    script = """
        local val = redis.call('GET', KEYS[1])
        if val == false then
            redis.call('SET', KEYS[1], ARGV[1])
            return 'SET_' .. ARGV[1]
        else
            return 'EXISTS_' .. val
        end
    """

    print_command(f"EVAL <check_and_set_script> 1 lua_test new_val", "检查-设置脚本")
    result = client.eval(script, 1, "lua_test", "world")
    print(f"  lua_test 已存在（值为 'hello'），所以返回: {result}")

    # 不存在的 key
    result = client.eval(script, 1, "lua_new_key", "第一次写入")
    print(f"  lua_new_key 不存在，所以创建并返回: {result}")

    show_blackboard(client, "Lua 脚本执行后")

    section("原子 INCR 用 Lua 实现")

    client.set("mystock", 5)
    incr_script = """
        local stock = redis.call('GET', KEYS[1])
        if stock == false then
            return -1
        end
        local new_stock = tonumber(stock) - tonumber(ARGV[1])
        if new_stock < 0 then
            return -2
        end
        redis.call('SET', KEYS[1], new_stock)
        return new_stock
    """

    print_command("EVAL <减库存脚本> 1 mystock 2", "原子减库存 2")
    result = client.eval(incr_script, 1, "mystock", "2")
    print(f"  扣减后库存: {result}")
    print(f"  实际值: {client.get('mystock')}")

    print_command("EVAL <减库存脚本> 1 mystock 10", "尝试扣减 10（超过剩余库存）")
    result = client.eval(incr_script, 1, "mystock", "10")
    print(f"  结果: {result} （-2 表示库存不足）")
    print(f"  库存未改变: {client.get('mystock')}")

    print_key_point(
        "Lua 脚本在 Redis 内部原子执行：\n"
        "    - 支持 if/else、循环等复杂逻辑\n"
        "    - 脚本执行期间不会被其他命令中断\n"
        "    - 适合实现 CAS（Compare-And-Swap）等操作\n"
        "    - 但脚本要尽量短——长时间脚本会阻塞 Redis！"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: DISCARD — 放弃事务
    # ═══════════════════════════════════════════════════════════
    print_step(5, "DISCARD — 放弃事务")

    print_note("如果开启了事务但改变主意了，可以用 DISCARD 取消")

    pipe = client.pipeline(transaction=True)
    pipe.multi()
    pipe.set("discard_test", "这个值不会被写入")
    pipe.incr("counter")
    print_command("MULTI → SET... INCR...", "开启事务并排入两个命令")
    pipe.reset()  # 相当于 DISCARD
    print_command("DISCARD (pipe.reset())", "放弃事务！")

    val = client.get("discard_test")
    print(f"  discard_test 的值: {val}")
    print_note("DISCARD 后，事务队列中的命令全部丢弃，不执行。")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 恭喜！你掌握了 Pipeline、事务、WATCH 和 Lua 脚本:{Color.RESET}

   {Color.HIGHLIGHT}Pipeline{Color.RESET}    →  批量发送，减少网络 RTT（不保证原子）
   {Color.HIGHLIGHT}MULTI/EXEC{Color.RESET}  →  一组命令原子执行（不支持回滚）
   {Color.HIGHLIGHT}WATCH{Color.RESET}       →  乐观锁，被改过就不执行事务
   {Color.HIGHLIGHT}DISCARD{Color.RESET}     →  放弃事务队列中的命令
   {Color.HIGHLIGHT}Lua 脚本{Color.RESET}    →  在 Redis 内部执行复杂原子逻辑

{Color.DIM}Pipeline 解决的是网络问题，事务解决的是并发问题。{Color.RESET}
""")

    cleanup_demo_keys(client, "pipeline_test:*")
    for key in ["demo:a", "demo:b", "tx_test", "counter", "flag",
                 "stock", "lua_test", "lua_new_key", "mystock",
                 "discard_test", "account:a", "account:b"]:
        client.delete(key)


if __name__ == "__main__":
    main()
