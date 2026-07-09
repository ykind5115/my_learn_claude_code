#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s04: List — 队列与栈（黑板上的传送带）

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - LPUSH 和 RPUSH 的区别是什么？
  - 怎么用 List 实现一个消息队列？
  - BLPOP 和 LPOP 的区别是什么？
  - LTRIM 怎么实现「只保留最新 N 条」？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s04_list/code.py
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
    print(f"{Color.HEADER}  s04: List — 队列与栈（黑板上的传送带）{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    # 连接 Redis
    client = get_redis_client()

    # 清理残留
    cleanup_demo_keys(client, "demo:*")
    client.flushdb()

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: LPUSH + RPUSH — 从左右两端推入
    # ═══════════════════════════════════════════════════════════
    print_step(1, "LPUSH + RPUSH — 从左右两端推入")

    print_command("LPUSH queue '任务A'", "从左边推入「任务A」")
    result = client.lpush("queue", "任务A")
    print_result(result, "LPUSH queue (返回列表长度)")
    show_blackboard(client, "LPUSH 任务A 之后")

    print_command("LPUSH queue '任务B'", "从左边推入「任务B」——它会在任务A前面")
    result = client.lpush("queue", "任务B")
    print_result(result, "LPUSH queue")
    show_blackboard(client, "LPUSH 任务B 之后")

    print_command("RPUSH queue '任务C'", "从右边推入「任务C」——它会在任务A后面")
    result = client.rpush("queue", "任务C")
    print_result(result, "RPUSH queue")
    show_blackboard(client, "RPUSH 任务C 之后")

    print_note("LPUSH 从左边推入，新元素在列表最前面（索引0）。")
    print_note("RPUSH 从右边推入，新元素在列表最后面（索引-1）。")

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: LRANGE — 查看传送带
    # ═══════════════════════════════════════════════════════════
    print_step(2, "LRANGE — 查看传送带上的内容")

    print_command("LRANGE queue 0 -1", "查看列表全部内容（-1 = 最后一个）")
    result = client.lrange("queue", 0, -1)
    print_result(result, "LRANGE queue 0 -1")

    print_command("LRANGE queue 0 1", "只查看前两个元素")
    result = client.lrange("queue", 0, 1)
    print_result(result, "LRANGE queue 0 1")

    print_note("LRANGE key start stop 返回从 start 到 stop（含两端）的元素。")

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: LPOP + RPOP — 从两端弹出
    # ═══════════════════════════════════════════════════════════
    print_step(3, "LPOP + RPOP — 从两端弹出元素")

    print_command("LPOP queue", "从左边弹出一个元素")
    result = client.lpop("queue")
    print_result(result, "LPOP queue")
    show_blackboard(client, "LPOP 一次后 — 最左边的元素被取走了")

    print_command("RPOP queue", "从右边弹出一个元素")
    result = client.rpop("queue")
    print_result(result, "RPOP queue")
    show_blackboard(client, "RPOP 一次后 — 最右边的元素被取走了")

    print_command("LPOP queue", "再弹一次——只剩一个元素了")
    result = client.lpop("queue")
    print_result(result, "LPOP queue")
    show_blackboard(client, "再次 LPOP — 队列已空")

    print_command("LPOP queue", "对空列表 POP——不会报错")
    result = client.lpop("queue")
    print_result(result, "LPOP queue (空列表)")
    print_note("空列表 LPOP 返回 None（对应 Redis 的 nil），不是报错。")

    print_key_point(
        "弹出（POP）= 取出 + 删除。\n"
        "    LPOP 从左边取，RPOP 从右边取。\n"
        "    空列表 POP 返回 nil，不会报错。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: 栈模式（后进先出）
    # ═══════════════════════════════════════════════════════════
    print_step(4, "栈模式 — LPUSH + LPOP（后进先出）")

    print_command("LPUSH stack '第1页'", "推入第1页")
    client.lpush("stack", "第1页")
    print_command("LPUSH stack '第2页'", "推入第2页——放在最前面")
    client.lpush("stack", "第2页")
    print_command("LPUSH stack '第3页'", "推入第3页——放在最前面")
    client.lpush("stack", "第3页")
    show_blackboard(client, "栈 — 推入 3 个元素")

    print_command("LPOP stack", "弹出——后进先出")
    result = client.lpop("stack")
    print_result(result, "第1次 LPOP")
    result = client.lpop("stack")
    print_result(result, "第2次 LPOP")
    result = client.lpop("stack")
    print_result(result, "第3次 LPOP")

    print_note("栈：LPUSH + LPOP，后进先出（LIFO）。")
    print_note("适合「撤销操作」「浏览历史回退」等场景。")

    show_blackboard(client, "栈弹完后 — 空了")

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: 队列模式（先进先出）
    # ═══════════════════════════════════════════════════════════
    print_step(5, "队列模式 — RPUSH + LPOP（先进先出）")

    print_command("RPUSH msg_queue '消息1'", "从右边推入消息1")
    client.rpush("msg_queue", "消息1")
    print_command("RPUSH msg_queue '消息2'", "从右边推入消息2")
    client.rpush("msg_queue", "消息2")
    print_command("RPUSH msg_queue '消息3'", "从右边推入消息3")
    client.rpush("msg_queue", "消息3")
    show_blackboard(client, "队列 — 推入 3 条消息")

    print_command("LPOP msg_queue", "从左边弹出——先进先出")
    result = client.lpop("msg_queue")
    print_result(result, "第1次 LPOP")
    result = client.lpop("msg_queue")
    print_result(result, "第2次 LPOP")
    result = client.lpop("msg_queue")
    print_result(result, "第3次 LPOP")

    print_note("队列：RPUSH + LPOP，先进先出（FIFO）。")
    print_note("适合「消息队列」「任务队列」等场景。")

    show_blackboard(client, "队列消费完后 — 空了")

    # ═══════════════════════════════════════════════════════════
    # 第 6 步: LTRIM — 裁剪传送带
    # ═══════════════════════════════════════════════════════════
    print_step(6, "LTRIM — 裁剪，只保留最新 N 条")

    print_command("RPUSH recent '文章1' '文章2' '文章3' '文章4' '文章5'", "推入 5 篇文章")
    client.rpush("recent", "文章1", "文章2", "文章3", "文章4", "文章5")
    show_blackboard(client, "5 篇文章")

    print_command("LTRIM recent 0 2", "只保留索引 0 到 2（前 3 条）")
    result = client.ltrim("recent", 0, 2)
    print_result(result, "LTRIM recent 0 2")
    show_blackboard(client, "LTRIM 后 — 只剩前 3 条，后 2 条被丢弃")

    # 演示实战用法：LPUSH + LTRIM 永远保留最新 N 条
    print_command("LPUSH + LTRIM 组合", "每次推入后立即裁剪，确保不超过 3 条")
    client.lpush("news", "新闻A")
    client.ltrim("news", 0, 2)
    client.lpush("news", "新闻B")
    client.ltrim("news", 0, 2)
    client.lpush("news", "新闻C")
    client.ltrim("news", 0, 2)
    client.lpush("news", "新闻D")  # 推入第 4 条
    client.ltrim("news", 0, 2)     # 裁剪，丢弃最旧的那条
    show_blackboard(client, "LPUSH + LTRIM 后 — 永远只有最新 3 条")

    print_note("LPUSH + LTRIM = 最新 N 条记录的最优方案。")
    print_note("无论推入多少条，列表长度永远不超过 N。")

    # ═══════════════════════════════════════════════════════════
    # 第 7 步: LINDEX — 通过索引访问
    # ═══════════════════════════════════════════════════════════
    print_step(7, "LINDEX — 通过索引访问指定位置的元素")

    client.rpush("mylist", "A", "B", "C", "D", "E")
    show_blackboard(client, "准备了一个包含 5 个元素的列表")

    print_command("LINDEX mylist 0", "索引 0 = 第一个元素")
    result = client.lindex("mylist", 0)
    print_result(result, "LINDEX mylist 0")

    print_command("LINDEX mylist -1", "索引 -1 = 最后一个元素")
    result = client.lindex("mylist", -1)
    print_result(result, "LINDEX mylist -1")

    print_command("LINDEX mylist -2", "索引 -2 = 倒数第二个")
    result = client.lindex("mylist", -2)
    print_result(result, "LINDEX mylist -2")

    print_command("LINDEX mylist 10", "越界索引")
    result = client.lindex("mylist", 10)
    print_result(result, "LINDEX mylist 10 (越界)")

    print_command("LLEN mylist", "看列表长度")
    result = client.llen("mylist")
    print_result(result, "LLEN mylist")
    print_note("LLEN 是 O(1) 操作——Redis 内部维护了长度计数器。")

    # ═══════════════════════════════════════════════════════════
    # 第 8 步: 阻塞弹出演示 — BLPOP / BRPOP
    # ═══════════════════════════════════════════════════════════
    print_step(8, "阻塞弹出 — BLPOP / BRPOP（队列为空时等待）")

    print_note("BLPOP 和 BRPOP 是阻塞版本——队列为空时不会立即返回，而是等待。")
    print_note("这是消息队列的核心机制。")

    # 先准备一个空队列
    client.delete("task_queue")

    # 先启动一个线程来消费（因为 BLPOP 会阻塞）
    blpop_result = {"value": None, "done": False}

    def consumer():
        print(f"  {Color.DIM}[消费者] 等待任务... BLPOP task_queue 5 (最多等 5 秒){Color.RESET}")
        result = client.blpop("task_queue", timeout=5)
        if result:
            blpop_result["value"] = result
        else:
            blpop_result["value"] = ("超时", "nil")
        blpop_result["done"] = True

    consumer_thread = threading.Thread(target=consumer, daemon=True)
    consumer_thread.start()

    time.sleep(0.5)  # 确保消费者先进入等待

    print(f"\n  {Color.INFO}[生产者] 推入一个任务...{Color.RESET}")
    print_command("RPUSH task_queue '发送邮件'", "生产者推入任务")
    result = client.rpush("task_queue", "发送邮件")
    print_result(result, "RPUSH task_queue")

    consumer_thread.join(timeout=6)

    if blpop_result["value"]:
        if blpop_result["value"] == ("超时", "nil"):
            print(f"\n  → {Color.WARNING}BLPOP 超时——队列一直为空{Color.RESET}")
        else:
            key, value = blpop_result["value"]
            print(f"\n  → {Color.SUCCESS}消费者收到任务！key={key}, value={value}{Color.RESET}")
    else:
        print(f"\n  → {Color.ERROR}未收到消息（异常）{Color.RESET}")

    print_note("消费者调用 BLPOP 后进入等待，不消耗 CPU。")
    print_note("一旦有 RPUSH 推入新任务，消费者立即被唤醒。")

    # 展示超时场景
    print()
    print_command("BLPOP empty_queue 3", "对一个空队列 BLPOP，等 3 秒")
    print(f"  {Color.DIM}等待 3 秒...{Color.RESET}")
    result = client.blpop("empty_queue", timeout=3)
    print_result(result, "BLPOP empty_queue 3")
    print_note("超时返回 None，需要调用方自行处理。")

    show_blackboard(client, "当前黑板状态")

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
{Color.SUCCESS}🎉 恭喜！你已经掌握了 Redis List 的核心操作:{Color.RESET}

   {Color.HIGHLIGHT}LPUSH{Color.RESET} / {Color.HIGHLIGHT}RPUSH{Color.RESET}  →  从传送带两端推入元素
   {Color.HIGHLIGHT}LPOP{Color.RESET}  / {Color.HIGHLIGHT}RPOP{Color.RESET}  →  从传送带两端弹出元素
   {Color.HIGHLIGHT}LRANGE{Color.RESET}       →  查看传送带上的内容
   {Color.HIGHLIGHT}LTRIM{Color.RESET}        →  裁剪，只保留一部分
   {Color.HIGHLIGHT}LLEN{Color.RESET}         →  看传送带有多长
   {Color.HIGHLIGHT}LINDEX{Color.RESET}       →  通过索引访问
   {Color.HIGHLIGHT}BLPOP{Color.RESET} / {Color.HIGHLIGHT}BRPOP{Color.RESET}  →  阻塞弹出（队列为空时等待）

{Color.DIM}List 最有价值的场景就是消息队列——RPUSH 生产 + BLPOP 消费。{Color.RESET}
""")

    cleanup_demo_keys(client, "demo:*")


if __name__ == "__main__":
    main()
