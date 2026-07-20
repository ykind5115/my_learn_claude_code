#!/usr/bin/env python3
"""s31-04: 消息队列"""
import os, sys, time, threading, queue
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_key_point, print_section, print_note

def demo_all():
    print_step(1, "生产者-消费者模型")
    q = queue.Queue()
    results = []

    def producer():
        for i in range(10):
            q.put(f"msg_{i}")
            time.sleep(0.05)

    def consumer(name, delay):
        while True:
            try: msg = q.get(timeout=1)
            except: break
            time.sleep(delay)
            results.append(f"{name}:{msg}")

    # 快生产者 + 慢消费者
    t1 = threading.Thread(target=producer)
    t2 = threading.Thread(target=consumer, args=("C1", 0.1))
    t1.start(); t2.start(); t1.join(); t2.join()
    print(f"  处理了 {len(results)} 条消息 (消费者慢但不会丢消息)")

    print_step(2, "Agent 中的应用")
    print(f"  s15-s17 Agent 团队: 通过消息总线异步通信")
    print(f"  s13 后台任务: 耗时操作丢到队列由后台处理")

if __name__ == "__main__":
    print_section("s31-04: 消息队列")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("消息队列 = 解耦 + 削峰 + 异步")
