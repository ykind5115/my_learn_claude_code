#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s03: Mini Message Queue — 队列

运行: python s24_data_structures/s03_mini_mq/code.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import (
    Color, print_header, print_step, print_note, print_key_point, print_success,
)
from s03_mini_mq.queue import Queue, CircularQueue
from s03_mini_mq.mini_mq import DemoMessageQueue


def demo_queue():
    print_step(1, "队列的基本操作 — FIFO")
    q = Queue()
    for item in ["A", "B", "C", "D"]:
        q.enqueue(item)
        print_note(f"enqueue('{item}')")
    q.print_structure()
    print_note("dequeue (先进先出):")
    while not q.is_empty():
        print_note(f"  dequeue() → '{q.dequeue()}'")

    print_key_point("队列 = FIFO。和栈(LIFO)相反——先来的先出去。")


def demo_circular_queue():
    print_step(2, "循环队列 — 用数组高效实现")
    cq = CircularQueue(4)
    for i in range(4):
        cq.enqueue(f"任务{i}")
    print_note("入队 4 个任务，队列满了")
    try:
        cq.enqueue("任务5")
    except OverflowError:
        print_note("队列满！无法入队")
    print_note(f"dequeue → '{cq.dequeue()}' — 腾出空间")
    cq.enqueue("任务5")
    print_note("现在可以入队了——循环利用数组空间")

    print_key_point("循环队列 = 固定大小数组 + head/tail 指针循环移动。")


def demo_message_queue():
    print_step(3, "Mini Message Queue — 生产者消费者")
    mq = DemoMessageQueue()
    mq.create_topic("orders")
    mq.create_topic("notifications")

    print_note("生产者发布消息...")
    mq.publish("orders", "用户 #42 下单了")
    mq.publish("orders", "用户 #99 下单了")
    mq.publish("notifications", "欢迎新用户")
    mq.status()

    print_note("消费者处理消息...")
    mq.consume("orders")
    mq.consume("orders")
    mq.consume("notifications")
    mq.status()

    print_key_point("消息队列 = 解耦 + 削峰 + FIFO 顺序保证。")


def main():
    print_header("s03: Mini Message Queue — 队列")
    print(f"  {Color.HIGHLIGHT}数据结构: 队列 (Queue) — FIFO{Color.RESET}\n")

    demo_queue()
    demo_circular_queue()
    demo_message_queue()

    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"\n{Color.SUCCESS}✅ 队列 = FIFO，栈的反面。解耦生产者和消费者的利器。{Color.RESET}")
    print(f"{Color.HIGHLIGHT}下一步: 打开 mini_mq.py，实现 TODO 方法！{Color.RESET}\n")


if __name__ == "__main__":
    main()
