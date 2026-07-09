#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s17: Pub/Sub 与 Stream — 消息传递的两种方式

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - Pub/Sub 和 Stream 的核心区别是什么？
  - Pub/Sub 的 "fire-and-forget" 特性意味着什么？
  - Stream 的消费组怎么工作？为什么需要 ACK？
  - 什么场景选 Pub/Sub？什么场景选 Stream？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s17_pubsub_stream/code.py
"""

import sys
import time
import threading
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from s25_redis.utils import (
    Color,
    get_redis_client,
    get_raw_client,
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
    print(f"{Color.HEADER}  s17: Pub/Sub 与 Stream — 消息传递的两种方式{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    client = get_redis_client()
    raw_client = get_raw_client()

    # 清理
    client.delete("mystream", "chat:messages")
    cleanup_demo_keys(client, "demo:*")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: Pub/Sub — 实时广播
    # ═══════════════════════════════════════════════════════════
    print_step(1, "Pub/Sub — 实时广播消息")

    received_messages = []

    def pubsub_subscriber():
        """在后台线程中运行订阅者"""
        sub_client = get_redis_client()
        pubsub = sub_client.pubsub()
        pubsub.subscribe("demo:news")

        for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"]
                received_messages.append(data)
                print(f"\n  {Color.SUCCESS}📡 [订阅者] 收到频道 '{message['channel']}': {data}{Color.RESET}")
            if message["data"] == "STOP":
                break

        sub_client.close()

    print_note("启动订阅者线程（监听 demo:news 频道）")
    sub_thread = threading.Thread(target=pubsub_subscriber, daemon=True)
    sub_thread.start()
    time.sleep(0.5)  # 等订阅者就绪
    print(f"  {Color.SUCCESS}✅ 订阅者已就绪，正在监听...{Color.RESET}")

    section("发布消息")

    messages = ["你好，Redis Pub/Sub！", "这是第二条消息", "第三条消息", "STOP"]

    for msg in messages:
        print_command(f'PUBLISH demo:news "{msg}"')
        result = client.publish("demo:news", msg)
        print(f"  → 返回 {result} 个订阅者收到")
        time.sleep(0.5)

    sub_thread.join(timeout=2)

    print(f"\n  总共收到 {len(received_messages)} 条消息:")
    for i, m in enumerate(received_messages):
        print(f"    {i+1}. {m}")

    print_key_point(
        "Pub/Sub = 实时广播。\n"
        "    发布者不关心谁在听，订阅者在线就能收到。\n"
        "    但如果订阅者不在线（还没 SUBSCRIBE），消息就丢失了。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: Pub/Sub 的致命缺陷 — 迟到的订阅者
    # ═══════════════════════════════════════════════════════════
    print_step(2, "Pub/Sub 缺陷演示 — 迟到的订阅者收不到消息")

    print_note("先发布消息，再开订阅者 —— 订阅者将错过所有已发布的消息")

    # 先发消息
    section("第一步：发布消息（此时没有订阅者）")
    pub_count = client.publish("demo:late", "这条消息你永远收不到")
    print(f"  PUBLISH → {pub_count} 个订阅者（没有订阅者，消息丢失！）")
    pub_count = client.publish("demo:late", "这条也丢了")
    print(f"  PUBLISH → {pub_count} 个订阅者")

    # 后开订阅者
    late_msg = []

    def late_subscriber():
        sub_client = get_redis_client()
        pubsub = sub_client.pubsub()
        pubsub.subscribe("demo:late")
        for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"]
                late_msg.append(data)
                print(f"\n  {Color.SUCCESS}📡 [迟到订阅者] 收到: {data}{Color.RESET}")
            if message["data"] == "STOP_LATE":
                break
        sub_client.close()

    section("第二步：启动订阅者（此时之前的消息已经丢失）")
    late_thread = threading.Thread(target=late_subscriber, daemon=True)
    late_thread.start()
    time.sleep(0.5)

    client.publish("demo:late", "这条可以收到")
    client.publish("demo:late", "STOP_LATE")
    late_thread.join(timeout=2)

    print(f"\n  迟到订阅者收到的消息数: {len(late_msg)}")
    print(f"  之前发布的 2 条消息全部丢失！")

    print_key_point(
        "Pub/Sub 是 'fire-and-forget'（发完即忘）。\n"
        "    消息不持久、不排队、不重试。\n"
        "    如果订阅者离线或迟到，它永远不会收到已发布的消息。\n"
        "    Stream 解决了这个问题——消息会持久化保存。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: Stream — 可靠的消息队列
    # ═══════════════════════════════════════════════════════════
    print_step(3, "Stream — 持久化的消息队列")

    section("XADD — 添加消息到 Stream")

    # 使用 raw_client 以便正确编码
    msg1 = raw_client.xadd("mystream", {"sensor": "温度", "value": "25.3"})
    print_command(f'XADD mystream * sensor 温度 value 25.3')
    print(f"  消息 ID: {Color.HIGHLIGHT}{msg1.decode() if isinstance(msg1, bytes) else msg1}{Color.RESET}")

    time.sleep(0.01)  # 保证时间戳不同
    msg2 = raw_client.xadd("mystream", {"sensor": "湿度", "value": "68%"})
    print_command(f'XADD mystream * sensor 湿度 value 68%')
    print(f"  消息 ID: {Color.HIGHLIGHT}{msg2.decode() if isinstance(msg2, bytes) else msg2}{Color.RESET}")

    time.sleep(0.01)
    msg3 = raw_client.xadd("mystream", {"sensor": "气压", "value": "1013hPa"})
    print_command(f'XADD mystream * sensor 气压 value 1013hPa')
    print(f"  消息 ID: {Color.HIGHLIGHT}{msg3.decode() if isinstance(msg3, bytes) else msg3}{Color.RESET}")

    show_blackboard(client, "Stream 添加消息后")

    section("XREAD — 读取消息")

    # 从 Stream 开头读
    print_command("XREAD COUNT 10 STREAMS mystream 0", "从头读取所有消息")
    all_msgs = raw_client.xread({"mystream": "0"}, count=10)
    print(f"\n  Stream 内容:")
    for msg_id, msg_data in all_msgs[b"mystream"]:
        id_str = msg_id.decode() if isinstance(msg_id, bytes) else msg_id
        data_str = {k.decode() if isinstance(k, bytes) else k:
                    v.decode() if isinstance(v, bytes) else v
                    for k, v in msg_data.items()}
        print(f"    {Color.YELLOW}[{id_str}]{Color.RESET} {data_str}")

    # 从某个 ID 之后读
    first_id = msg1.decode() if isinstance(msg1, bytes) else msg1
    print_command(f"XREAD COUNT 10 STREAMS mystream {first_id}", f"从 {first_id} 之后读取")
    after_msgs = raw_client.xread({"mystream": first_id}, count=10)
    print(f"\n  从 {first_id} 之后的消息:")
    if b"mystream" in after_msgs:
        for msg_id, msg_data in after_msgs[b"mystream"]:
            id_str = msg_id.decode() if isinstance(msg_id, bytes) else msg_id
            data_str = {k.decode() if isinstance(k, bytes) else k:
                        v.decode() if isinstance(v, bytes) else v
                        for k, v in msg_data.items()}
            print(f"    {Color.YELLOW}[{id_str}]{Color.RESET} {data_str}")
    else:
        print(f"    (没有新消息)")

    print_key_point(
        "Stream 的消息是持久化存储的。\n"
        "    每条消息有一个自动生成的 ID（时间戳-序号）。\n"
        "    可以从任意位置开始读取（消息回溯）。\n"
        "    消息消费后不会消失——需要显式删除或设置 MAXLEN。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: 消费组（Consumer Group）
    # ═══════════════════════════════════════════════════════════
    print_step(4, "消费组 — 多消费者分摊消息")

    section("创建消费组")

    # 删除可能存在的消费组
    try:
        raw_client.xgroup_destroy("mystream", "workers")
    except Exception:
        pass

    print_command("XGROUP CREATE mystream workers $", "创建消费组 workers")
    raw_client.xgroup_create("mystream", "workers", id="0", mkstream=True)
    print(f"  {Color.SUCCESS}✅ 消费组 workers 已创建{Color.RESET}")

    section("从消费组读取消息（A 处理第一条）")

    print_command("XREADGROUP GROUP workers consumer_a COUNT 1 STREAMS mystream >",
                  "consumer_a 读取一条未处理的消息")
    result_a = raw_client.xreadgroup("workers", "consumer_a", {"mystream": ">"}, count=1)

    consumer_a_msg = None
    if b"mystream" in result_a:
        for msg_id, msg_data in result_a[b"mystream"]:
            consumer_a_msg = msg_id
            id_str = msg_id.decode() if isinstance(msg_id, bytes) else msg_id
            data_str = {k.decode() if isinstance(k, bytes) else k:
                        v.decode() if isinstance(v, bytes) else v
                        for k, v in msg_data.items()}
            print(f"  consumer_a 收到: {Color.YELLOW}[{id_str}]{Color.RESET} {data_str}")

    section("从消费组读取消息（B 处理第二条）")

    print_command("XREADGROUP GROUP workers consumer_b COUNT 1 STREAMS mystream >",
                  "consumer_b 读取下一条未处理的消息")
    result_b = raw_client.xreadgroup("workers", "consumer_b", {"mystream": ">"}, count=1)

    if b"mystream" in result_b:
        for msg_id, msg_data in result_b[b"mystream"]:
            id_str = msg_id.decode() if isinstance(msg_id, bytes) else msg_id
            data_str = {k.decode() if isinstance(k, bytes) else k:
                        v.decode() if isinstance(v, bytes) else v
                        for k, v in msg_data.items()}
            print(f"  consumer_b 收到: {Color.YELLOW}[{id_str}]{Color.RESET} {data_str}")

    section("XACK — 确认消息已处理")

    if consumer_a_msg:
        msg_id_str = consumer_a_msg.decode() if isinstance(consumer_a_msg, bytes) else consumer_a_msg
        print_command(f"XACK mystream workers {msg_id_str}", "consumer_a 确认已处理")
        ack_count = raw_client.xack("mystream", "workers", consumer_a_msg)
        print(f"  ACK 结果: {ack_count} 条消息已确认")

    # 查看待处理消息
    print_command("XPENDING mystream workers", "查看待处理的消息（未 ACK 的）")
    pending_info = raw_client.xpending("mystream", "workers")
    if isinstance(pending_info, (list, tuple)) and len(pending_info) >= 1:
        pending_count = pending_info[0] if pending_info[0] else 0
        print(f"  待处理消息数: {pending_count}")
        print_note(f"consumer_b 没有 ACK，所以消息还在待处理列表")

    print_key_point(
        "消费组让多个消费者分摊处理 Stream 中的消息。\n"
        "    - 每条消息只分配给消费组中的一个消费者\n"
        "    - 消费者处理完必须 XACK，否则消息留在待处理列表\n"
        "    - 如果消费者崩溃，未 ACK 的消息可以重新分配给其他消费者"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: Stream 弥补 Pub/Sub 的缺陷
    # ═══════════════════════════════════════════════════════════
    print_step(5, "Stream 弥补 Pub/Sub 的缺陷 — 迟到的消费者也能看历史")

    # 先往 Stream 写消息
    section("提前写入消息到 Stream")
    raw_client.xadd("chat:messages", {"user": "Alice", "msg": "大家好！"})
    raw_client.xadd("chat:messages", {"user": "Bob", "msg": "你好 Alice！"})
    raw_client.xadd("chat:messages", {"user": "Charlie", "msg": "今天天气真好"})
    print(f"  {Color.SUCCESS}✅ 3 条消息已写入 Stream{Color.RESET}")

    # Stream 的消费者在之后启动，仍然能读到历史
    section("迟到的消费者读取 Stream 历史消息")

    print_command("XREAD COUNT 10 STREAMS chat:messages 0", "从头读取所有消息")
    history = raw_client.xread({"chat:messages": "0"}, count=10)
    if b"chat:messages" in history:
        print(f"\n  {Color.SUCCESS}📜 迟到的消费者读到了历史消息！{Color.RESET}")
        for msg_id, msg_data in history[b"chat:messages"]:
            id_str = msg_id.decode() if isinstance(msg_id, bytes) else msg_id
            data_str = {k.decode() if isinstance(k, bytes) else k:
                        v.decode() if isinstance(v, bytes) else v
                        for k, v in msg_data.items()}
            print(f"    {Color.YELLOW}[{id_str}]{Color.RESET} {data_str}")
    else:
        print(f"  (没有消息)")

    print_note("Pub/Sub 中迟到的订阅者什么都收不到")
    print_note("Stream 中迟到的消费者可以从头读取所有历史消息")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 恭喜！你掌握了 Pub/Sub 和 Stream:{Color.RESET}

   {Color.HIGHLIGHT}Pub/Sub{Color.RESET}     →  实时广播，fire-and-forget，离线丢失
   {Color.HIGHLIGHT}SUBSCRIBE{Color.RESET}   →  订阅频道
   {Color.HIGHLIGHT}PUBLISH{Color.RESET}     →  发布消息
   {Color.HIGHLIGHT}Stream{Color.RESET}      →  持久化消息队列，支持消费组和 ACK
   {Color.HIGHLIGHT}XADD/XREAD{Color.RESET}  →  写入/读取消息
   {Color.HIGHLIGHT}XREADGROUP{Color.RESET}  →  消费组读取消息
   {Color.HIGHLIGHT}XACK{Color.RESET}        →  确认消息已处理

{Color.DIM}选择指南：需要实时广播不在意丢消息 → Pub/Sub。需要可靠消息处理 → Stream。{Color.RESET}
""")

    # 清理
    raw_client.delete("mystream", "chat:messages")
    for key in ["demo:news", "demo:late"]:
        raw_client.delete(key)
    cleanup_demo_keys(raw_client, "demo:*")
    raw_client.close()
    client.close()


if __name__ == "__main__":
    main()
