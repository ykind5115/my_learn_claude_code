#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s05: Hash — 对象存储（黑板上的表格）

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - Hash 和 String 的区别是什么？什么时候该用 Hash？
  - HGETALL 和 HMGET 的区别是什么？
  - HINCRBY 能解决什么问题？
  - Hash 为什么比多个 String key 更省内存？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s05_hash/code.py
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
    flush_db,
)


def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s05: Hash — 对象存储（黑板上的表格）{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # 连接 Redis
    client = get_redis_client()

    # 清理残留
    cleanup_demo_keys(client, "demo:*")
    client.flushdb()

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: HSET — 在表格里写入字段
    # ═══════════════════════════════════════════════════════════
    print_step(1, "HSET — 在表格里写入字段")

    print_command('HSET user:1001 name "张三"', "在 user:1001 表格的 name 行写入「张三」")
    result = client.hset("user:1001", "name", "张三")
    print_result(result, "HSET user:1001 name (1=新增, 0=更新)")
    show_blackboard(client, "写入 name 字段后")

    print_command('HSET user:1001 age "28"', "在 user:1001 表格的 age 行写入「28」")
    result = client.hset("user:1001", "age", "28")
    print_result(result, "HSET user:1001 age")

    print_command('HSET user:1001 city "北京"', "在 user:1001 表格的 city 行写入「北京」")
    result = client.hset("user:1001", "city", "北京")
    print_result(result, "HSET user:1001 city")

    show_blackboard(client, "写入 3 个字段后 — user:1001 有了完整信息")

    print_key_point(
        "Hash = 一个 key 对应一张表格。\n"
        "    HSET 在表格的某一「行」（field）写入「值」（value）。\n"
        "    相比多个 String key，Hash 把所有字段放在同一个 key 下，管理更方便。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: HGET — 读一个字段
    # ═══════════════════════════════════════════════════════════
    print_step(2, "HGET — 读表格中的某个字段")

    print_command("HGET user:1001 name", "读 name 字段")
    result = client.hget("user:1001", "name")
    print_result(result, "HGET user:1001 name")

    print_command("HGET user:1001 age", "读 age 字段")
    result = client.hget("user:1001", "age")
    print_result(result, "HGET user:1001 age")

    print_command("HGET user:1001 email", "读不存在的字段")
    result = client.hget("user:1001", "email")
    print_result(result, "HGET user:1001 email (不存在的字段)")
    print_note("不存在的 field 返回 nil，不是报错。")

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: HGETALL — 读整个表格
    # ═══════════════════════════════════════════════════════════
    print_step(3, "HGETALL — 读整个表格（所有字段）")

    print_command("HGETALL user:1001", "一次读取所有字段")
    result = client.hgetall("user:1001")
    print_result(result, "HGETALL user:1001")
    print_note("Python 客户端会自动将 HGETALL 结果转为 dict。")

    print_key_point(
        "HGETALL = 一次读取 Hash 的所有字段。\n"
        "    但要注意：如果一个 Hash 有大量字段（比如几十万），\n"
        "    HGETALL 会返回大量数据，可能造成网络阻塞。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: HSET 覆盖更新字段
    # ═══════════════════════════════════════════════════════════
    print_step(4, "HSET 覆盖更新 — 只修改一个字段，不影响其他")

    print_command('HSET user:1001 city "上海"', "把 city 从「北京」改为「上海」")
    result = client.hset("user:1001", "city", "上海")
    print_result(result, "HSET user:1001 city (0=更新，不是新增)")
    show_blackboard(client, "更新 city 后 — 注意只有 city 变了")

    print_note("HGETALL 确认：name 和 age 没变，只有 city 被改成了「上海」。")
    all_fields = client.hgetall("user:1001")
    print(f"  → {all_fields}")

    print_key_point(
        "Hash 修改单个字段是原子操作——不会影响其他字段。\n"
        "    这是 Hash 相比 JSON String 的巨大优势——\n"
        "    用 JSON String 改一个字段需要读→反序列化→改→序列化→写回整个 JSON。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: HEXISTS — 检查字段是否存在
    # ═══════════════════════════════════════════════════════════
    print_step(5, "HEXISTS — 检查某个字段是否存在")

    print_command("HEXISTS user:1001 name", "检查 name 字段是否存在")
    result = client.hexists("user:1001", "name")
    print_result(result, "HEXISTS user:1001 name (1=存在)")

    print_command("HEXISTS user:1001 email", "检查 email 字段是否存在")
    result = client.hexists("user:1001", "email")
    print_result(result, "HEXISTS user:1001 email (0=不存在)")

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: HDEL — 删除一个字段
    # ═══════════════════════════════════════════════════════════
    print_step(6, "HDEL — 删除表格中的某一行")

    print_command("HDEL user:1001 city", "删除 city 字段")
    result = client.hdel("user:1001", "city")
    print_result(result, "HDEL user:1001 city (删除了几个字段)")
    show_blackboard(client, "HDEL city 之后 — city 那一行消失了")

    print_command("HGETALL user:1001", "确认 city 已被删除")
    result = client.hgetall("user:1001")
    print_result(result, "HGETALL user:1001")
    print_note("删除一个字段不影响其他字段。")

    # ═══════════════════════════════════════════════════════════
    # 第 7 步: HINCRBY — 原子递增
    # ═══════════════════════════════════════════════════════════
    print_step(7, "HINCRBY — 表格里的原子计数器")

    print_command("HINCRBY user:1001 login_count 1", "首次登录，login_count +1")
    result = client.hincrby("user:1001", "login_count", 1)
    print_result(result, "HINCRBY user:1001 login_count 1")
    print_note("HINCRBY 自动创建不存在的字段（从 0 开始）。")

    # 连续递增
    for i in range(4):
        client.hincrby("user:1001", "login_count", 1)
    print_command("HINCRBY user:1001 login_count 1", "再登录 4 次")
    result = client.hget("user:1001", "login_count")
    print(f"  → login_count 当前值: {Color.HIGHLIGHT}{result}{Color.RESET}")

    # 递减
    print_command("HINCRBY user:1001 login_count -3", "减 3——加负数等于减")
    result = client.hincrby("user:1001", "login_count", -3)
    print_result(result, "HINCRBY user:1001 login_count -3")

    show_blackboard(client, "HINCRBY 操作后 — login_count 字段已更新")

    print_key_point(
        "HINCRBY 是 Hash 版原子递增——在对象存储中内嵌计数器。\n"
        "    不需要额外维护一个独立的 String 计数器 key。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 8 步: HMGET — 一次读多个字段
    # ═══════════════════════════════════════════════════════════
    print_step(8, "HMGET — 一次读取多个字段")

    # 先补充几个字段
    client.hset("user:1001", "level", "VIP")
    client.hset("user:1001", "points", "9999")

    print_command('HMGET user:1001 name level points', "一次读取 3 个字段")
    result = client.hmget("user:1001", "name", "level", "points")
    print_result(result, "HMGET user:1001 name level points")
    print_note("HMGET 比连续 3 次 HGET 少了 2 次网络往返。")

    # ═══════════════════════════════════════════════════════════
    # 第 9 步: HLEN, HKEYS, HVALS
    # ═══════════════════════════════════════════════════════════
    print_step(9, "HLEN / HKEYS / HVALS — 查看表格概况")

    print_command("HLEN user:1001", "看 user:1001 有几个字段")
    result = client.hlen("user:1001")
    print_result(result, "HLEN user:1001")

    print_command("HKEYS user:1001", "列出所有字段名")
    result = client.hkeys("user:1001")
    print_result(result, "HKEYS user:1001")

    print_command("HVALS user:1001", "列出所有字段值")
    result = client.hvals("user:1001")
    print_result(result, "HVALS user:1001")

    # ═══════════════════════════════════════════════════════════
    # 第 10 步: Hash vs String 内存效率对比
    # ═══════════════════════════════════════════════════════════
    print_step(10, "Hash vs String 内存效率对比")

    print_note("为了展示对比，我们分别用 String 和 Hash 存储同样的用户数据。")
    print_note("（这里只模拟结构，不做实际内存测量）")

    # 用 String 方式存储（多个 key）
    section("String 方式 — 每个字段一个 key")
    client.set("str_user:1001:name", "张三")
    client.set("str_user:1001:age", "28")
    client.set("str_user:1001:city", "北京")
    client.set("str_user:1001:level", "VIP")
    show_blackboard(client, "String 方式 — 4 个独立的 key", pattern="str_user:*")

    # 用 Hash 方式存储（一个 key 多个 field）
    section("Hash 方式 — 一个 key 所有字段")
    client.hset("hash_user:1001", "name", "张三")
    client.hset("hash_user:1001", "age", "28")
    client.hset("hash_user:1001", "city", "北京")
    client.hset("hash_user:1001", "level", "VIP")
    show_blackboard(client, "Hash 方式 — 1 个 key 包含 4 个字段", pattern="hash_user:*")

    # 读取方式对比
    section("读取方式对比")
    print(f"  {Color.INFO}String 读取所有字段:{Color.RESET}")
    print(f"    → MGET str_user:1001:name str_user:1001:age str_user:1001:city str_user:1001:level")
    str_result = client.mget("str_user:1001:name", "str_user:1001:age",
                              "str_user:1001:city", "str_user:1001:level")
    print(f"    → {str_result}")

    print(f"\n  {Color.INFO}Hash 读取所有字段:{Color.RESET}")
    print(f"    → HGETALL hash_user:1001")
    hash_result = client.hgetall("hash_user:1001")
    print(f"    → {hash_result}")

    print_key_point(
        "Hash 的优势:\n"
        "    1. 内存更省——所有字段存在同一个 key 下\n"
        "    2. 读取更方便——HGETALL 一次拿到所有字段\n"
        "    3. 修改更灵活——改一个字段不影响其他字段\n"
        "    4. 内嵌计数器——HINCRBY 直接在对象里做加减"
    )

    show_blackboard(client, "当前黑板全貌 — String + Hash 两种方式共存")

    # ═══════════════════════════════════════════════════════════
    # 第 11 步: 清理
    # ═══════════════════════════════════════════════════════════
    print_step(11, "清理 — 擦掉黑板")

    flush_db(client)
    show_blackboard(client, "全部清理完毕")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 恭喜！你已经掌握了 Redis Hash 的核心操作:{Color.RESET}

   {Color.HIGHLIGHT}HSET{Color.RESET}         →  在表格中写入一个字段
   {Color.HIGHLIGHT}HGET{Color.RESET}         →  读取一个字段
   {Color.HIGHLIGHT}HGETALL{Color.RESET}      →  读取所有字段
   {Color.HIGHLIGHT}HMGET{Color.RESET}        →  一次读取多个字段
   {Color.HIGHLIGHT}HDEL{Color.RESET}         →  删除一个字段
   {Color.HIGHLIGHT}HEXISTS{Color.RESET}      →  检查字段是否存在
   {Color.HIGHLIGHT}HINCRBY{Color.RESET}      →  字段原子递增
   {Color.HIGHLIGHT}HLEN{Color.RESET}         →  看字段总数
   {Color.HIGHLIGHT}HKEYS{Color.RESET}        →  列出所有字段名
   {Color.HIGHLIGHT}HVALS{Color.RESET}        →  列出所有字段值

{Color.DIM}Hash = 专门存储对象的工具。一个 key 对应一个「表格」，每一行就是一个字段。{Color.RESET}
""")

    cleanup_demo_keys(client, "demo:*")


if __name__ == "__main__":
    main()
