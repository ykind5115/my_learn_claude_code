#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s07: Sorted Set — 排行榜（黑板上的积分榜）

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - Sorted Set 和 Set 的核心区别是什么？
  - ZRANGE 和 ZREVRANGE 的区别是什么？
  - ZRANK 和 ZREVRANK 的区别是什么？
  - ZADD 和 ZINCRBY 的区别是什么？
  - 怎么用 Sorted Set 实现延迟队列？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s07_sorted_set/code.py
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
    print(f"{Color.HEADER}  s07: Sorted Set — 排行榜（黑板上的积分榜）{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # 连接 Redis
    client = get_redis_client()

    # 清理残留
    cleanup_demo_keys(client, "demo:*")
    client.flushdb()

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: ZADD — 在积分榜上添加成员
    # ═══════════════════════════════════════════════════════════
    print_step(1, "ZADD — 在积分榜上添加成员（带分数）")

    print_command("ZADD leaderboard 1500 '张三'", "添加张三，分数 1500")
    result = client.zadd("leaderboard", {"张三": 1500})
    print_result(result, "ZADD leaderboard (新增了几个)")

    print_command("ZADD leaderboard 2200 '李四'", "添加李四，分数 2200")
    result = client.zadd("leaderboard", {"李四": 2200})
    print_result(result, "ZADD leaderboard")

    print_command("ZADD leaderboard 1800 '王五'", "添加王五，分数 1800")
    result = client.zadd("leaderboard", {"王五": 1800})
    print_result(result, "ZADD leaderboard")

    print_command("ZADD leaderboard 950 '赵六'", "添加赵六，分数 950")
    result = client.zadd("leaderboard", {"赵六": 950})
    print_result(result, "ZADD leaderboard")

    show_blackboard(client, "ZADD 之后 — 积分榜创建完成")

    print_key_point(
        "ZADD = 带分数的 SADD。\n"
        "    每个成员带一个分数（score），分数可以是整数或浮点数。\n"
        "    Sorted Set 内部自动按分数排序——插入时定位到正确位置。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: ZRANGE — 按分数升序查看
    # ═══════════════════════════════════════════════════════════
    print_step(2, "ZRANGE — 按分数从低到高查看（升序）")

    print_command("ZRANGE leaderboard 0 -1", "查看全部成员（分数从低到高）")
    result = client.zrange("leaderboard", 0, -1)
    print_result(result, "ZRANGE leaderboard 0 -1")
    print_note("最低分的「赵六」(950) 排在最前面。")

    print_command("ZRANGE leaderboard 0 -1 WITHSCORES", "带分数查看")
    result = client.zrange("leaderboard", 0, -1, withscores=True)
    print_result(result, "ZRANGE WITHSCORES")
    print_note("WITHSCORES 参数让 ZRANGE 同时返回分数。")

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: ZREVRANGE — 按分数降序查看（排行榜）
    # ═══════════════════════════════════════════════════════════
    print_step(3, "ZREVRANGE — 按分数从高到低查看（降序 = 排行榜）")

    print_command("ZREVRANGE leaderboard 0 -1 WITHSCORES",
                  "从高到低查看——真正的排行榜")
    result = client.zrevrange("leaderboard", 0, -1, withscores=True)
    print_result(result, "ZREVRANGE (排行榜)")

    print_command("ZREVRANGE leaderboard 0 2 WITHSCORES", "Top 3（前三名）")
    result = client.zrevrange("leaderboard", 0, 2, withscores=True)
    print_result(result, "ZREVRANGE Top 3")
    print_note("ZREVRANGE 0 2 = 前三名（索引 0=第1名, 1=第2名, 2=第3名）。")

    print_key_point(
        "ZRANGE vs ZREVRANGE：\n"
        "    ZRANGE = 分数从低到高（升序，最低分排第一）\n"
        "    ZREVRANGE = 分数从高到低（降序，最高分排第一）\n"
        "    排行榜一般用 ZREVRANGE。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: ZRANK / ZREVRANK — 查排名
    # ═══════════════════════════════════════════════════════════
    print_step(4, "ZRANK / ZREVRANK — 查排名")

    print_command('ZRANK leaderboard "张三"', "升序排名（0=最低分）")
    result = client.zrank("leaderboard", "张三")
    print_result(result, "ZRANK 张三 (升序)")
    print(f"  → 张三分数 {client.zscore('leaderboard', '张三')}，"
          f"升序排第 {result} 名（从0开始）")

    print_command('ZREVRANK leaderboard "张三"', "降序排名（0=最高分）")
    result = client.zrevrank("leaderboard", "张三")
    print_result(result, "ZREVRANK 张三 (降序)")
    print(f"  → 张三降序排第 {result} 名——也就是正数第 {result + 1} 名")

    print_note("ZRANK 返回的是索引（从 0 开始），显示给用户时记得 +1。")

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: ZSCORE — 查分数
    # ═══════════════════════════════════════════════════════════
    print_step(5, "ZSCORE — 查某个成员的分数")

    print_command('ZSCORE leaderboard "张三"', "查张三的分数")
    result = client.zscore("leaderboard", "张三")
    print_result(result, "ZSCORE 张三")

    print_command('ZSCORE leaderboard "不存在的人"', "查不存在的成员")
    result = client.zscore("leaderboard", "不存在的人")
    print_result(result, "ZSCORE 不存在的成员")
    print_note("成员不存在返回 None。")

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: ZINCRBY — 原子增减分数
    # ═══════════════════════════════════════════════════════════
    print_step(6, "ZINCRBY — 原子增减分数（排行榜实时更新）")

    show_blackboard(client, "当前排行榜（更新前）")

    print_command('ZINCRBY leaderboard 300 "张三"', "张三赢了，加 300 分！")
    result = client.zincrby("leaderboard", 300, "张三")
    print_result(result, "ZINCRBY 张三 +300 (新分数)")
    show_blackboard(client, "ZINCRBY 后 — 张三分数变了，排名可能也变了")

    print_command('ZREVRANGE leaderboard 0 -1 WITHSCORES',
                  "确认排名变化——张三从第3名跳到第？")
    result = client.zrevrange("leaderboard", 0, -1, withscores=True)
    print_result(result, "更新后的排行榜")

    # 模拟连续加分
    print_command('ZINCRBY leaderboard 500 "赵六"', "赵六赢了！加 500 分！")
    result = client.zincrby("leaderboard", 500, "赵六")
    print_result(result, "ZINCRBY 赵六 +500")

    print_command('ZREVRANGE leaderboard 0 -1 WITHSCORES', "最新的排行榜")
    result = client.zrevrange("leaderboard", 0, -1, withscores=True)
    print_result(result, "最终排行榜")

    print_key_point(
        "ZINCRBY 原子地增减分数，Sorted Set 自动重新排序。\n"
        "    不需要手动删除再插入——O(log n) 自动完成。\n"
        "    这就是实时排行榜的技术基础。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 7 步: ZREM — 删除成员
    # ═══════════════════════════════════════════════════════════
    print_step(7, "ZREM — 从积分榜删除成员")

    print_command('ZREM leaderboard "赵六"', "赵六作弊，从排行榜删除")
    result = client.zrem("leaderboard", "赵六")
    print_result(result, "ZREM leaderboard (删除了几个)")
    show_blackboard(client, "ZREM 后 — 赵六从排行榜消失了")

    # ═══════════════════════════════════════════════════════════
    # 第 8 步: ZCARD — 看总人数
    # ═══════════════════════════════════════════════════════════
    print_step(8, "ZCARD — 看积分榜上有多少人")

    print_command("ZCARD leaderboard", "看排行榜总人数")
    result = client.zcard("leaderboard")
    print_result(result, "ZCARD leaderboard")

    # ═══════════════════════════════════════════════════════════
    # 第 9 步: ZCOUNT — 按分数段统计
    # ═══════════════════════════════════════════════════════════
    print_step(9, "ZCOUNT — 统计分数在某范围内的人数")

    print_command("ZCOUNT leaderboard 1500 2000", "统计 1500~2000 分之间的人数")
    result = client.zcount("leaderboard", 1500, 2000)
    print_result(result, "ZCOUNT leaderboard 1500 2000")
    print_note("ZCOUNT 包含两端（>=1500 且 <=2000）。")

    print_command("ZCOUNT leaderboard 2000 +inf", "统计 2000 分以上的人数")
    result = client.zcount("leaderboard", 2000, "+inf")
    print_result(result, "ZCOUNT leaderboard 2000 +inf")

    print_command("ZCOUNT leaderboard -inf 1500", "统计 1500 分以下的人数")
    result = client.zcount("leaderboard", "-inf", 1500)
    print_result(result, "ZCOUNT leaderboard -inf 1500")

    # ═══════════════════════════════════════════════════════════
    # 第 10 步: ZRANGEBYSCORE — 按分数范围查成员
    # ═══════════════════════════════════════════════════════════
    print_step(10, "ZRANGEBYSCORE — 按分数范围查看成员")

    # 补充一些成员
    client.zadd("leaderboard", {"小明": 1200, "小红": 1900, "小刚": 700})
    show_blackboard(client, "补充成员后")

    print_command("ZRANGEBYSCORE leaderboard 1000 2000 WITHSCORES",
                  "查看分数在 1000~2000 之间的成员")
    result = client.zrangebyscore("leaderboard", 1000, 2000, withscores=True)
    print_result(result, "ZRANGEBYSCORE 1000~2000")

    print_command("ZRANGEBYSCORE leaderboard 2000 +inf WITHSCORES",
                  "查看 2000 分以上的成员")
    result = client.zrangebyscore("leaderboard", 2000, "+inf", withscores=True)
    print_result(result, "ZRANGEBYSCORE 2000+")

    # ═══════════════════════════════════════════════════════════
    # 第 11 步: 延迟队列实战演示
    # ═══════════════════════════════════════════════════════════
    print_step(11, "实战：延迟队列 — 用时间戳做分数")

    print_note("延迟队列：将来某个时间点才执行的任务。")
    print_note("用时间戳作为分数，ZRANGEBYSCORE 查看哪些任务到了执行时间。")

    now = int(time.time())
    task1_time = now + 3     # 3 秒后执行
    task2_time = now + 8     # 8 秒后执行
    task3_time = now + 15    # 15 秒后执行

    print_command(f"ZADD delay:tasks {task1_time} '发送欢迎邮件'")
    client.zadd("delay:tasks", {"发送欢迎邮件": task1_time})
    print_command(f"ZADD delay:tasks {task2_time} '生成数据报表'")
    client.zadd("delay:tasks", {"生成数据报表": task2_time})
    print_command(f"ZADD delay:tasks {task3_time} '清理临时缓存'")
    client.zadd("delay:tasks", {"清理临时缓存": task3_time})

    show_blackboard(client, "延迟队列 — 可以看到每个任务的执行时间戳")

    # 查询当前时间应该执行的任务
    print_command("ZRANGEBYSCORE delay:tasks -inf <当前时间戳>",
                  "检查哪些任务已到期（当前时间之前应该执行的）")
    result = client.zrangebyscore("delay:tasks", "-inf", now, withscores=True)
    print(f"  → 已到期任务: {Color.HIGHLIGHT}{result if result else '无'}{Color.RESET}")
    print(f"  {Color.DIM}(当前时间戳: {now}){Color.RESET}")

    # 等 4 秒后再检查
    print(f"\n  {Color.DIM}等待 4 秒...{Color.RESET}")
    time.sleep(4)
    now_after = int(time.time())

    print_command(f"ZRANGEBYSCORE delay:tasks -inf {now_after}",
                  "4 秒后重新检查——欢迎邮件应该到期了")
    result = client.zrangebyscore("delay:tasks", "-inf", now_after, withscores=True)
    for member, score in result:
        print(f"  → ✅ {member} (时间戳: {score}, 已到期)")
    print_note("延迟队列用时间戳作为分数，后台定时扫描 ZRANGEBYSCORE 取到期任务。")

    show_blackboard(client, "延迟队列状态")

    print_key_point(
        "Sorted Set 做延迟队列的优势：\n"
        "    1. 用时间戳做分数——天然按时间排序\n"
        "    2. ZRANGEBYSCORE 按时间范围取到期任务——O(log n)\n"
        "    3. ZREMRANGEBYRANK 删除已处理任务\n"
        "    4. 无需轮询所有任务，只需查最小分数的那些"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 12 步: ZREMRANGEBYRANK — 按排名删除
    # ═══════════════════════════════════════════════════════════
    print_step(12, "ZREMRANGEBYRANK — 按排名范围删除（清理底部成员）")

    print_command("ZREMRANGEBYRANK leaderboard 0 1",
                  "删除升序排名 0~1（最低分的两个）")
    result = client.zremrangebyrank("leaderboard", 0, 1)
    print_result(result, "ZREMRANGEBYRANK (删除了几个)")

    print_command("ZREVRANGE leaderboard 0 -1 WITHSCORES",
                  "删除后剩下的成员")
    result = client.zrevrange("leaderboard", 0, -1, withscores=True)
    print_result(result, "剩余排行榜")

    show_blackboard(client, "ZREMRANGEBYRANK 后")

    print_note("ZREMRANGEBYRANK 按升序排名删除——0 是最低分。")
    print_note("适合「排行榜只保留前 100 名」的场景。")

    # ═══════════════════════════════════════════════════════════
    # 第 13 步: 清理
    # ═══════════════════════════════════════════════════════════
    print_step(13, "清理 — 擦掉黑板")

    flush_db(client)
    show_blackboard(client, "全部清理完毕")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 恭喜！你已经掌握了 Redis Sorted Set 的核心操作:{Color.RESET}

   {Color.HIGHLIGHT}ZADD{Color.RESET}             →  添加成员（带分数，自动排序）
   {Color.HIGHLIGHT}ZRANGE{Color.RESET}           →  分数从低到高查看
   {Color.HIGHLIGHT}ZREVRANGE{Color.RESET}        →  分数从高到低查看（排行榜）
   {Color.HIGHLIGHT}ZRANK{Color.RESET}            →  查升序排名
   {Color.HIGHLIGHT}ZREVRANK{Color.RESET}         →  查降序排名
   {Color.HIGHLIGHT}ZSCORE{Color.RESET}           →  查某个成员的分数
   {Color.HIGHLIGHT}ZINCRBY{Color.RESET}          →  原子增减分数
   {Color.HIGHLIGHT}ZREM{Color.RESET}             →  删除成员
   {Color.HIGHLIGHT}ZCARD{Color.RESET}            →  看总人数
   {Color.HIGHLIGHT}ZCOUNT{Color.RESET}           →  按分数段统计人数
   {Color.HIGHLIGHT}ZRANGEBYSCORE{Color.RESET}    →  按分数范围查成员
   {Color.HIGHLIGHT}ZREMRANGEBYRANK{Color.RESET}  →  按排名范围删除

{Color.DIM}Sorted Set = 排行榜 + 延迟队列 + 滑动窗口的万能工具。{Color.RESET}
""")

    cleanup_demo_keys(client, "demo:*")


if __name__ == "__main__":
    main()
