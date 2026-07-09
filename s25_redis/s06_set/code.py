#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s06: Set — 去重与集合运算（黑板上的标签贴纸）

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - Set 和 List 的核心区别是什么？
  - SINTER / SUNION / SDIFF 分别做什么？
  - SRANDMEMBER 和 SPOP 的区别是什么？
  - 什么场景下应该用 Set 而不是 List？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s06_set/code.py
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
    print(f"{Color.HEADER}  s06: Set — 去重与集合运算（黑板上的标签贴纸）{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # 连接 Redis
    client = get_redis_client()

    # 清理残留
    cleanup_demo_keys(client, "demo:*")
    client.flushdb()

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: SADD — 往袋子里加标签
    # ═══════════════════════════════════════════════════════════
    print_step(1, "SADD — 往袋子里加标签（自动去重）")

    print_command('SADD article:42:tags "Redis" "教程" "NoSQL" "缓存"',
                  "给文章 42 打上 4 个标签")
    result = client.sadd("article:42:tags", "Redis", "教程", "NoSQL", "缓存")
    print_result(result, "SADD article:42:tags (新增了几个)")
    show_blackboard(client, "文章 42 的标签")

    print_command('SADD article:42:tags "Redis"', "再添加一个重复的「Redis」——应该没变化")
    result = client.sadd("article:42:tags", "Redis")
    print_result(result, "SADD article:42:tags 'Redis' 再次 (0=没新增)")
    print_note("Set 自动去重——重复添加同一个元素，返回 0，集合大小不变。")

    print_key_point(
        "SADD 会自动去重——同一个元素只能出现在集合中一次。\n"
        "    这是 Set 和 List 最核心的区别之一。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: SMEMBERS — 看所有标签
    # ═══════════════════════════════════════════════════════════
    print_step(2, "SMEMBERS — 看袋子里所有标签")

    print_command("SMEMBERS article:42:tags", "查看文章 42 的所有标签")
    result = client.smembers("article:42:tags")
    print_result(result, "SMEMBERS article:42:tags")
    print_note("注意：Set 是无序的——SMEMBERS 返回的顺序可能和插入顺序不同。")

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: SISMEMBER — 检查标签是否存在
    # ═══════════════════════════════════════════════════════════
    print_step(3, "SISMEMBER — 检查某张标签在不在袋子里")

    print_command('SISMEMBER article:42:tags "Redis"', "检查「Redis」标签")
    result = client.sismember("article:42:tags", "Redis")
    print_result(result, "SISMEMBER 'Redis' (1=存在)")

    print_command('SISMEMBER article:42:tags "Python"', "检查「Python」标签")
    result = client.sismember("article:42:tags", "Python")
    print_result(result, "SISMEMBER 'Python' (0=不存在)")

    print_note("SISMEMBER 是 O(1) 操作——不管集合有 10 个还是 1000 万个元素，速度一样快。")

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: SREM — 移除标签
    # ═══════════════════════════════════════════════════════════
    print_step(4, "SREM — 从袋子里拿走一张标签")

    print_command('SREM article:42:tags "NoSQL"', "移除「NoSQL」标签")
    result = client.srem("article:42:tags", "NoSQL")
    print_result(result, "SREM article:42:tags (删除了几个)")
    show_blackboard(client, "SREM 之后 — NoSQL 标签消失了")

    print_note("SREM 返回实际删除了几个元素。不存在的元素会返回 0。")

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: SCARD — 看集合大小
    # ═══════════════════════════════════════════════════════════
    print_step(5, "SCARD — 袋子里有几张标签？")

    print_command("SCARD article:42:tags", "看文章 42 有几个标签")
    result = client.scard("article:42:tags")
    print_result(result, "SCARD article:42:tags")
    print_note("SCARD 是 O(1) 操作——Redis 内部维护了集合大小计数器。")

    show_blackboard(client, "当前黑板")

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: SINTER — 交集（共同标签）
    # ═══════════════════════════════════════════════════════════
    print_step(6, "SINTER — 交集（两篇文章的共同标签）")

    # 创建第二篇文章的标签
    client.sadd("article:43:tags", "Redis", "实战", "Python", "教程")
    show_blackboard(client, "文章 42 和 43 的标签对比")

    print_command("SINTER article:42:tags article:43:tags", "找两篇文章的共同标签")
    result = client.sinter("article:42:tags", "article:43:tags")
    print_result(result, "SINTER (共同标签)")
    print_note("交集 = 两个集合中都存在的元素。")

    # 展示交集图解
    print(f"\n  {Color.DIM}文章 42 标签:{Color.RESET} {client.smembers('article:42:tags')}")
    print(f"  {Color.DIM}文章 43 标签:{Color.RESET} {client.smembers('article:43:tags')}")
    print(f"  {Color.HIGHLIGHT}共同标签:     {result}{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 7 步: SUNION — 并集（所有标签）
    # ═══════════════════════════════════════════════════════════
    print_step(7, "SUNION — 并集（两篇文章的所有标签，去重）")

    print_command("SUNION article:42:tags article:43:tags", "合并所有标签——去重")
    result = client.sunion("article:42:tags", "article:43:tags")
    print_result(result, "SUNION (所有标签)")
    print_note("并集 = 两个集合的并集，重复元素只出现一次。")

    print_key_point(
        "集合运算是 Set 相对于 List 的巨大优势:\n"
        "    SINTER = 交集（共同部分）\n"
        "    SUNION = 并集（全部去重）\n"
        "    SDIFF  = 差集（我有你没有）"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 8 步: SDIFF — 差集（我有你没有）
    # ═══════════════════════════════════════════════════════════
    print_step(8, "SDIFF — 差集（文章 42 有但文章 43 没有的）")

    print_command("SDIFF article:42:tags article:43:tags", "文章 42 有但 43 没有的标签")
    result = client.sdiff("article:42:tags", "article:43:tags")
    print_result(result, "SDIFF (文章42独有)")

    print_command("SDIFF article:43:tags article:42:tags", "文章 43 有但 42 没有的标签")
    result = client.sdiff("article:43:tags", "article:42:tags")
    print_result(result, "SDIFF (文章43独有)")

    # ═══════════════════════════════════════════════════════════
    # 第 9 步: SRANDMEMBER — 随机抽取
    # ═══════════════════════════════════════════════════════════
    print_step(9, "SRANDMEMBER — 随机抽奖（不删除）")

    # 准备抽奖池
    for uid in ["用户A", "用户B", "用户C", "用户D", "用户E"]:
        client.sadd("lottery:pool", uid)

    show_blackboard(client, "抽奖池")

    print_command("SRANDMEMBER lottery:pool", "随机抽一个（不删除）")
    result = client.srandmember("lottery:pool")
    print_result(result, "SRANDMEMBER 1 次")

    print_command("SRANDMEMBER lottery:pool 3", "随机抽 3 个（不删除）")
    result = client.srandmember("lottery:pool", 3)
    print_result(result, "SRANDMEMBER 3 次")
    print_note("SRANDMEMBER 不删除被抽到的元素——适合展示型抽奖。")

    show_blackboard(client, "SRANDMEMBER 后 — 集合没变（没有删除）")

    # ═══════════════════════════════════════════════════════════
    # 第 10 步: SPOP — 随机弹出（删除）
    # ═══════════════════════════════════════════════════════════
    print_step(10, "SPOP — 随机弹出并删除（适合发奖）")

    print_command("SPOP lottery:pool", "随机弹出一个——该用户中奖并被移除")
    result = client.spop("lottery:pool")
    print_result(result, "SPOP 1 次")

    print_command("SPOP lottery:pool 2", "随机弹出 2 个")
    result = client.spop("lottery:pool", 2)
    print_result(result, "SPOP 2 次")

    show_blackboard(client, "SPOP 后 — 集合变小了（元素被移除了）")

    print_key_point(
        "SRANDMEMBER vs SPOP：\n"
        "    SRANDMEMBER = 只读，不改变集合（适合展示中奖名单预览）\n"
        "    SPOP = 读写，从集合中移除（适合实际发奖，保证每个人只能中一次）"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 11 步: 实战 — 共同好友
    # ═══════════════════════════════════════════════════════════
    print_step(11, "实战 — 共同好友（集合运算的经典场景）")

    # 两个用户的好友列表
    client.sadd("user:1001:friends", "user:1002", "user:1003", "user:1004", "user:1005")
    client.sadd("user:1002:friends", "user:1001", "user:1003", "user:1005", "user:1006")
    show_blackboard(client, "两个用户的好友列表")

    print_command("SINTER user:1001:friends user:1002:friends", "共同好友")
    result = client.sinter("user:1001:friends", "user:1002:friends")
    print_result(result, "共同好友")

    print_command("SCARD user:1001:friends", "user:1001 有多少好友")
    result = client.scard("user:1001:friends")
    print_result(result, "user:1001 的好友数")

    print_command("SUNION user:1001:friends user:1002:friends", "去重后的所有好友")
    result = client.sunion("user:1001:friends", "user:1002:friends")
    print_result(result, "所有好友（去重）")

    print_key_point(
        "共同好友是 SINTER 最典型的应用场景。\n"
        "    在社交类应用中，SINTER 可以快速计算：\n"
        "    - 共同关注的人\n"
        "    - 共同加入的群组\n"
        "    - 共同喜欢的文章"
    )

    show_blackboard(client, "当前黑板全貌")

    # ═══════════════════════════════════════════════════════════
    # 第 12 步: 清理
    # ═══════════════════════════════════════════════════════════
    print_step(12, "清理 — 擦掉黑板")

    flush_db(client)
    show_blackboard(client, "全部清理完毕")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 恭喜！你已经掌握了 Redis Set 的核心操作:{Color.RESET}

   {Color.HIGHLIGHT}SADD{Color.RESET}         →  添加标签（自动去重）
   {Color.HIGHLIGHT}SMEMBERS{Color.RESET}     →  查看所有标签
   {Color.HIGHLIGHT}SISMEMBER{Color.RESET}    →  检查标签是否存在（O(1)）
   {Color.HIGHLIGHT}SREM{Color.RESET}         →  移除标签
   {Color.HIGHLIGHT}SCARD{Color.RESET}        →  看标签总数
   {Color.HIGHLIGHT}SINTER{Color.RESET}       →  交集（共同部分）
   {Color.HIGHLIGHT}SUNION{Color.RESET}       →  并集（全部去重）
   {Color.HIGHLIGHT}SDIFF{Color.RESET}        →  差集（我有你没有）
   {Color.HIGHLIGHT}SRANDMEMBER{Color.RESET}  →  随机抽取（不删）
   {Color.HIGHLIGHT}SPOP{Color.RESET}         →  随机弹出（删除）

{Color.DIM}Set = 自动去重 + O(1) 查找 + 集合运算——标签系统和社交场景的利器。{Color.RESET}
""")

    cleanup_demo_keys(client, "demo:*")


if __name__ == "__main__":
    main()
