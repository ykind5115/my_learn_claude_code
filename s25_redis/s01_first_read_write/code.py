#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s01: 第一次读写 — 在黑板上写下第一行字

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - SET 和 GET 的本质是什么？
  - DEL 和 EXISTS 怎么用？
  - KEYS 为什么不能在生产环境随便用？
  - Redis 的「共享黑板」模型是怎么工作的？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s01_first_read_write/code.py
"""

import sys
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
)


def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s01: 第一次读写 — 在黑板上写下第一行字{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # 连接 Redis
    client = get_redis_client()

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: 连接 Redis — 站在黑板前
    # ═══════════════════════════════════════════════════════════
    print_step(1, "连接 Redis — 站在黑板前")

    print_command("redis.Redis(host='localhost', port=6379)", "连接到本地 Redis 服务")
    print_command("client.ping()", "轻敲一下黑板，确认 Redis 在线")
    result = client.ping()
    print_result(result, "PING")
    print(f"  {Color.SUCCESS}✅ 黑板连接成功！准备好了。{Color.RESET}")

    # 先确保黑板干净
    cleanup_demo_keys(client, "demo:*")
    # 也清理我们可能用到的测试 key
    for key in ["name", "age", "city", "language", "greeting", "counter"]:
        client.delete(key)

    show_blackboard(client, "初始状态 — 干干净净的黑板")

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: SET — 在黑板上写第一行字
    # ═══════════════════════════════════════════════════════════
    print_step(2, "SET — 在黑板上写第一行字")

    print_command('SET name "小明"', "在黑板的 name 这一行写上「小明」")
    result = client.set("name", "小明")
    print_result(result, "SET name")
    show_blackboard(client, "SET name 之后")

    print_key_point(
        "SET 不是「插入」，是「覆盖写」。\n"
        "    就像在黑板上写一行字——同一行写第二次，旧字就被新字盖住了。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: GET — 读黑板上写了什么
    # ═══════════════════════════════════════════════════════════
    print_step(3, "GET — 看看黑板上写了什么")

    print_command('GET name', "看黑板上 name 这一行的内容")
    result = client.get("name")
    print_result(result, "GET name")
    show_blackboard(client, "GET name — 读到了什么")

    # 试试获取不存在的 key
    print_command('GET nothing', "读一个不存在的 key")
    result = client.get("nothing")
    print_result(result, "GET nothing")
    print_note("不存在的 key 返回 (nil)，不是空字符串，也不是报错。")

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: SET 覆盖写 — 同一行，换一句话
    # ═══════════════════════════════════════════════════════════
    print_step(4, "SET 覆盖写 — 同一行，换一句话")

    print_command('SET name "小红"', "在 name 这一行覆盖写新内容")
    result = client.set("name", "小红")
    print_result(result, "SET name")
    show_blackboard(client, "SET name 覆盖后 — 旧值「小明」已被覆盖")

    print_key_point(
        "SET 是覆盖写——同一个 key 第二次 SET，旧值就丢了。\n"
        "    这在很多场景下有用（比如更新缓存），但也意味着要小心。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: 写多个 key — 黑板上有了更多内容
    # ═══════════════════════════════════════════════════════════
    print_step(5, "写多个 key — 黑板上有了更多内容")

    print_command('SET age "25"')
    client.set("age", "25")
    print_command('SET city "北京"')
    client.set("city", "北京")
    print_command('SET language "Python"')
    client.set("language", "Python")
    print_command('SET greeting "你好，Redis！"')
    client.set("greeting", "你好，Redis！")
    print(f"  {Color.SUCCESS}✅ 连续写了 4 个 key{Color.RESET}")
    show_blackboard(client, "写入多个 key 后")

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: KEYS — 扫视整个黑板
    # ═══════════════════════════════════════════════════════════
    print_step(6, "KEYS — 扫视整个黑板")

    print_command("KEYS *", "列出黑板上所有 key")
    keys = client.keys("*")
    print(f"  → {Color.HIGHLIGHT}{keys}{Color.RESET}")
    print_note(f"黑板上共有 {len(keys)} 个 key")

    # 匹配模式
    print_command("KEYS *e*", "匹配包含字母 e 的 key")
    matched = client.keys("*e*")
    print(f"  → {Color.HIGHLIGHT}{matched}{Color.RESET}")

    print_note("KEYS 支持通配符模式：* 匹配任意多个字符，? 匹配一个字符")
    print_note("⚠ 生产环境慎用 — key 数量大时会阻塞 Redis！")

    show_blackboard(client, "当前黑板全貌")

    # ═══════════════════════════════════════════════════════════
    # 第 7 步: EXISTS — 确认某行有没有字
    # ═══════════════════════════════════════════════════════════
    print_step(7, "EXISTS — 确认某行有没有字")

    print_command("EXISTS name", "确认 name 这个 key 是否存在")
    result = client.exists("name")
    print_result(result, "EXISTS name")
    print(f"  → {'存在 ✅' if result else '不存在 ❌'}")

    print_command("EXISTS nothing", "确认不存在的 key")
    result = client.exists("nothing")
    print_result(result, "EXISTS nothing")
    print(f"  → {'存在 ✅' if result else '不存在 ❌'}")

    print_note("EXISTS 返回 1 表示存在，0 表示不存在。")

    # ═══════════════════════════════════════════════════════════
    # 第 8 步: DEL — 擦掉某一行
    # ═══════════════════════════════════════════════════════════
    print_step(8, "DEL — 擦掉黑板上的一行")

    print_command("DEL city", "擦掉 city 这一行")
    result = client.delete("city")
    print_result(result, "DEL city (删除了几个 key)")
    show_blackboard(client, "DEL city 之后 — city 这一行消失了")

    # 一次删除多个
    print_command('DEL age language', "一次擦掉两行")
    result = client.delete("age", "language")
    print_result(result, "DEL age language (删除了几个 key)")
    show_blackboard(client, "DEL age language 之后 — 又少了两行")

    print_key_point(
        "DEL 返回删除了几个 key。\n"
        "    - 删除不存在的 key 返回 0，不会报错\n"
        "    - 一次可以删多个 key，减少网络往返"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 9 步: TYPE — 看什么笔写的
    # ═══════════════════════════════════════════════════════════
    print_step(9, "TYPE — 看某一行是用什么笔写的")

    print_command("TYPE name", "检查 name 的数据类型")
    result = client.type("name")
    print_result(result, "TYPE name")
    print_note("目前所有 key 都是 string 类型（String = 用马克笔写的）")

    print_command("TYPE nothing", "检查不存在的 key")
    result = client.type("nothing")
    print_result(result, "TYPE nothing")
    print_note("不存在的 key 返回 none，表示笔不在黑板上。")

    show_blackboard(client, "当前黑板状态")

    # ═══════════════════════════════════════════════════════════
    # 第 10 步: FLUSHDB — 擦掉整块黑板（带警告）
    # ═══════════════════════════════════════════════════════════
    print_step(10, "FLUSHDB — 擦掉整块黑板")

    print_command("FLUSHDB", "⚠ 清除当前数据库所有 key！")
    print_note("生产环境不要轻易用 FLUSHDB！这里只是演示。")

    from s25_redis.utils import flush_db
    flush_db(client)

    show_blackboard(client, "FLUSHDB 之后 — 黑板干干净净")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 恭喜！你已经掌握了 Redis 最基础的操作:{Color.RESET}

   {Color.HIGHLIGHT}SET{Color.RESET}      →  在黑板上写字（存 key-value）
   {Color.HIGHLIGHT}GET{Color.RESET}      →  看黑板上写了什么（查 key）
   {Color.HIGHLIGHT}DEL{Color.RESET}      →  擦掉一行（删 key）
   {Color.HIGHLIGHT}EXISTS{Color.RESET}   →  确认某行有没有字（判断存在）
   {Color.HIGHLIGHT}KEYS{Color.RESET}     →  扫视整个黑板（列出 key）
   {Color.HIGHLIGHT}TYPE{Color.RESET}     →  看是什么笔写的（查类型）
   {Color.HIGHLIGHT}FLUSHDB{Color.RESET}  →  擦掉整块黑板（清空）

{Color.DIM}这些是 Redis 的「呼吸」——往后每一章都建立在它们之上。{Color.RESET}
""")

    cleanup_demo_keys(client, "demo:*")


if __name__ == "__main__":
    main()
