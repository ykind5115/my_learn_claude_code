#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s00-06: 协程 — async/await, 事件循环, asyncio.gather

学习目标:
  - 理解 async/await 语法
  - 理解事件循环的协作式调度
  - 对比协程 vs 线程的并发能力
  - 理解什么时候用协程

运行: python 06_coroutine/code.py
"""

import asyncio
import time
import threading


# ═══════════════════════════════════════════════════════════
# Demo 1: 基本 async/await
# ═══════════════════════════════════════════════════════════
def demo_1_basic_async():
    print("── Demo 1: 基本 async/await ──")

    async def say_hello(name, delay):
        print(f"  [{name}] 开始")
        await asyncio.sleep(delay)  # 不阻塞事件循环的 sleep
        print(f"  [{name}] 完成")
        return f"结果:{name}"

    async def main():
        results = await asyncio.gather(
            say_hello("A", 0.3),
            say_hello("B", 0.2),
            say_hello("C", 0.1),
        )
        print(f"  gather 返回: {results}")

    asyncio.run(main())
    print(f"  → 三个协程并发执行，总共只等最长的那个(0.3s)")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 2: 协程 vs 同步 — 性能对比
# ═══════════════════════════════════════════════════════════
def demo_2_performance():
    print("── Demo 2: 协程 vs 同步串行 ──")

    async def io_task(task_id):
        await asyncio.sleep(0.1)  # 模拟 I/O 操作
        return task_id

    COUNT = 50

    # 同步方式
    async def sync_way():
        start = time.time()
        for i in range(COUNT):
            await io_task(i)  # 一个接一个
        return time.time() - start

    # 并发方式
    async def async_way():
        start = time.time()
        await asyncio.gather(*[io_task(i) for i in range(COUNT)])
        return time.time() - start

    async def main():
        sync_time = await sync_way()
        async_time = await async_way()
        print(f"  同步串行 {COUNT} 个任务: {sync_time:.3f}s")
        print(f"  协程并发 {COUNT} 个任务: {async_time:.3f}s")
        if sync_time > 0.01:
            print(f"  加速比: {sync_time / async_time:.1f}x")

    asyncio.run(main())
    print()


# ═══════════════════════════════════════════════════════════
# Demo 3: 协程 vs 线程 — 大量并发对比
# ═══════════════════════════════════════════════════════════
def demo_3_coroutine_vs_thread():
    print("── Demo 3: 协程 vs 线程 — 1000 并发 ──")

    COUNT = 1000

    # 协程方式
    async def coro_task(task_id):
        await asyncio.sleep(0.01)
        return task_id

    async def run_coroutines():
        start = time.time()
        await asyncio.gather(*[coro_task(i) for i in range(COUNT)])
        return time.time() - start

    # 线程方式
    def thread_task(task_id):
        time.sleep(0.01)
        return task_id

    def run_threads():
        start = time.time()
        threads = [threading.Thread(target=thread_task, args=(i,))
                   for i in range(COUNT)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return time.time() - start

    coro_time = asyncio.run(run_coroutines())
    print(f"  协程 {COUNT} 个任务: {coro_time:.3f}s")

    thread_time = run_threads()
    print(f"  线程 {COUNT} 个任务: {thread_time:.3f}s")
    print(f"  → 协程创建/切换开销远小于线程")
    print(f"  → 每个线程 ~1MB 栈 = {COUNT}线程 ≈ {COUNT}MB 内存")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 4: 协程中不能用阻塞函数
# ═══════════════════════════════════════════════════════════
def demo_4_blocking_trap():
    print("── Demo 4: 协程陷阱 — 阻塞函数 ──")

    async def bad_task(name):
        print(f"  [{name}] 开始")
        time.sleep(0.2)  # ❌ 阻塞！整个事件循环卡住
        print(f"  [{name}] 完成")

    async def good_task(name):
        print(f"  [{name}] 开始")
        await asyncio.sleep(0.2)  # ✅ 不阻塞
        print(f"  [{name}] 完成")

    async def main():
        print("  使用 time.sleep (阻塞):")
        start = time.time()
        await asyncio.gather(bad_task("A"), bad_task("B"))
        print(f"  耗时: {time.time() - start:.3f}s (串行了！)")

        print()
        print("  使用 asyncio.sleep (非阻塞):")
        start = time.time()
        await asyncio.gather(good_task("A"), good_task("B"))
        print(f"  耗时: {time.time() - start:.3f}s (真正并发)")

    asyncio.run(main())
    print(f"  → 协程里绝不能调用阻塞函数！")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 5: 用协程模拟 Agent 并行工具执行
# ═══════════════════════════════════════════════════════════
def demo_5_agent_tools():
    print("── Demo 5: 模拟 Agent 的并行工具执行 ──")

    async def tool_read_file(path):
        print(f"    📖 读取 {path}...")
        await asyncio.sleep(0.2)  # 模拟 I/O
        return f"<content of {path}>"

    async def tool_search(query):
        print(f"    🔍 搜索 {query}...")
        await asyncio.sleep(0.3)  # 模拟搜索
        return f"<search results for {query}>"

    async def tool_run_bash(cmd):
        print(f"    💻 执行 {cmd}...")
        await asyncio.sleep(0.15)  # 模拟 bash
        return f"<output of {cmd}>"

    async def agent_turn(tools_to_call):
        """模拟 Agent 循环中的工具执行阶段"""
        tasks = []
        for name, args in tools_to_call:
            if name == "read_file":
                tasks.append(tool_read_file(*args))
            elif name == "search":
                tasks.append(tool_search(*args))
            elif name == "bash":
                tasks.append(tool_run_bash(*args))

        results = await asyncio.gather(*tasks)
        return results

    async def main():
        print("  模型返回了 3 个 tool_use 块:")
        tools = [
            ("read_file", ["README.md"]),
            ("search", ["error handling pattern"]),
            ("bash", ["ls -la"]),
        ]
        results = await agent_turn(tools)
        print()
        print(f"  全部完成，结果:")
        for r in results:
            print(f"    {r}")
        print(f"  → 这就是 s02 并行工具执行的原型")

    asyncio.run(main())
    print()


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("s00-06: 协程 — async/await, 事件循环, asyncio.gather")
    print("=" * 60)
    print()

    demo_1_basic_async()
    demo_2_performance()
    demo_3_coroutine_vs_thread()
    demo_4_blocking_trap()
    demo_5_agent_tools()

    print("─" * 60)
    print("小结:")
    print("  async def + await = 协程的标准写法")
    print("  asyncio.gather = 并发运行，全完成再继续")
    print("  协程适用: 大量 I/O 并发（记得用 await 而非阻塞调用）")
    print("  协程不适用: CPU 密集（会卡住事件循环）")
