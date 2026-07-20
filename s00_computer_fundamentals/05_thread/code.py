#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s00-05: 线程 — Thread, 竞态条件, Lock, GIL

学习目标:
  - 创建和管理线程
  - 理解竞态条件
  - 使用 Lock 保护共享数据
  - 理解 Python GIL 的影响

运行: python 05_thread/code.py
"""

import threading
import time


# ═══════════════════════════════════════════════════════════
# Demo 1: 创建和启动线程
# ═══════════════════════════════════════════════════════════
def demo_1_basic_thread():
    print("── Demo 1: 基本线程 ──")

    def worker(name, delay):
        print(f"  [{name}] 开始工作")
        time.sleep(delay)
        print(f"  [{name}] 完成 (睡了 {delay}s)")

    # 创建线程
    t1 = threading.Thread(target=worker, args=("A", 0.5))
    t2 = threading.Thread(target=worker, args=("B", 0.3))

    print("  启动线程...")
    t1.start()
    t2.start()

    # 等待线程完成
    t1.join()
    t2.join()
    print("  两个线程都完成了")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 2: 竞态条件 — 没有锁时数据出错
# ═══════════════════════════════════════════════════════════
def demo_2_race_condition():
    print("── Demo 2: 竞态条件 ──")

    counter = 0
    ITERATIONS = 100000

    def increment():
        nonlocal counter
        for _ in range(ITERATIONS):
            counter += 1  # 不是原子操作！

    t1 = threading.Thread(target=increment)
    t2 = threading.Thread(target=increment)

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    expected = ITERATIONS * 2
    print(f"  期望值: {expected}")
    print(f"  实际值: {counter}")
    print(f"  丢失了: {expected - counter} 次递增")
    print(f"  → 两个线程同时读写 counter，互相覆盖")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 3: Lock — 保护共享数据
# ═══════════════════════════════════════════════════════════
def demo_3_lock():
    print("── Demo 3: 用 Lock 保护 ──")

    counter = 0
    lock = threading.Lock()
    ITERATIONS = 100000

    def increment_safe():
        nonlocal counter
        for _ in range(ITERATIONS):
            with lock:       # 获取锁
                counter += 1  # 安全区域
                               # with 结束自动释放锁

    t1 = threading.Thread(target=increment_safe)
    t2 = threading.Thread(target=increment_safe)

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    expected = ITERATIONS * 2
    print(f"  期望值: {expected}")
    print(f"  实际值: {counter}")
    print(f"  ✅ 加锁后数据一致")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 4: GIL 演示 — CPU 密集 vs I/O 密集
# ═══════════════════════════════════════════════════════════
def demo_4_gil():
    print("── Demo 4: GIL 的影响 ──")

    # CPU 密集型：多线程不会更快
    def cpu_work():
        total = 0
        for i in range(10_000_000):
            total += i
        return total

    print("  CPU 密集型任务 (计算 1000 万次加法):")
    start = time.time()
    cpu_work()
    cpu_work()
    single_time = time.time() - start
    print(f"    单线程串行两次: {single_time:.3f}s")

    start = time.time()
    t1 = threading.Thread(target=cpu_work)
    t2 = threading.Thread(target=cpu_work)
    t1.start(); t2.start()
    t1.join(); t2.join()
    thread_time = time.time() - start
    print(f"    两个线程并行:     {thread_time:.3f}s")
    print(f"    → 多线程没有更快(GIL 限制了)")

    # I/O 密集型：多线程有效
    print()
    print("  I/O 密集型任务 (sleep 0.3s 两次):")

    def io_work():
        time.sleep(0.3)

    start = time.time()
    io_work()
    io_work()
    print(f"    串行两次: {time.time() - start:.3f}s")

    start = time.time()
    t1 = threading.Thread(target=io_work)
    t2 = threading.Thread(target=io_work)
    t1.start(); t2.start()
    t1.join(); t2.join()
    print(f"    两个线程: {time.time() - start:.3f}s")
    print(f"    → I/O 操作释放 GIL，多线程有效")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 5: 守护线程
# ═══════════════════════════════════════════════════════════
def demo_5_daemon():
    print("── Demo 5: 守护线程 ──")

    def background_worker():
        for i in range(5):
            print(f"    守护线程: 第 {i+1} 次心跳")
            time.sleep(0.2)

    t = threading.Thread(target=background_worker, daemon=True)
    t.start()

    time.sleep(0.5)  # 主线程等一小会
    print("  主线程退出 → 守护线程自动被杀")
    print(f"  → 不用 t.join()，程序直接结束")
    print()


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("s00-05: 线程 — Thread, 竞态条件, Lock, GIL")
    print("=" * 60)
    print()

    demo_1_basic_thread()
    demo_2_race_condition()
    demo_3_lock()
    demo_4_gil()
    demo_5_daemon()

    print("─" * 60)
    print("小结:")
    print("  线程: 共享内存, 适合 I/O 并发")
    print("  GIL: Python 多线程不能并行 CPU 计算")
    print("  Lock: 防御竞态条件")
    print("  daemon=True: 主线程退出, 守护线程自动结束")
