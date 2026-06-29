#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
队列 (Queue) — FIFO (First In, First Out)

队列是「先来的先服务」——就像排队买咖啡。

关键操作:
  enqueue(item) — O(1) 入队(尾部)
  dequeue()     — O(1) 出队(头部)
  peek()        — O(1) 查看队头
  is_empty()    — O(1)

和栈的区别: 栈是 LIFO (后进先出)，队列是 FIFO (先进先出)。

工程应用:
  - 消息队列 (RabbitMQ, Kafka)
  - 任务调度 (打印机队列, CPU 任务队列)
  - BFS (广度优先搜索)
  - 生产者-消费者模式
"""


class Queue:
    """
    基于 collections.deque 的高效队列 (推荐用于生产)

    空间复杂度: O(n)
    """

    def __init__(self):
        from collections import deque
        self._items = deque()

    def enqueue(self, item):
        """入队 — O(1)"""
        self._items.append(item)

    def dequeue(self):
        """出队 — O(1)，队空时抛出 IndexError"""
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self._items.popleft()

    def peek(self):
        """查看队头 — O(1)"""
        if self.is_empty():
            raise IndexError("peek from empty queue")
        return self._items[0]

    def is_empty(self):
        return len(self._items) == 0

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"Queue({list(self._items)})"

    def print_structure(self):
        items = list(self._items)
        if not items:
            print("  (空队列)")
            return
        print(f"  队头 → {' | '.join(str(x) for x in items)} → 队尾")


class CircularQueue:
    """
    循环队列 — 基于固定大小数组

    优势: 不需要动态扩容，适合嵌入式/实时系统。
    用 head 和 tail 两个指针追踪队列两端。
    """

    def __init__(self, capacity=8):
        self._data = [None] * capacity
        self._capacity = capacity
        self._head = 0   # 队头位置
        self._tail = 0   # 下一个入队位置
        self._size = 0

    def enqueue(self, item):
        if self._size == self._capacity:
            raise OverflowError("队列已满")
        self._data[self._tail] = item
        self._tail = (self._tail + 1) % self._capacity
        self._size += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        item = self._data[self._head]
        self._head = (self._head + 1) % self._capacity
        self._size -= 1
        return item

    def peek(self):
        if self.is_empty():
            raise IndexError("peek from empty queue")
        return self._data[self._head]

    def is_empty(self):
        return self._size == 0

    def __len__(self):
        return self._size


# ═══════════════════════════════════════════════════════════════
# 演示
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from utils import Color, print_step, print_key_point, print_note

    print(f"\n{Color.HEADER}  队列 — FIFO 演示{Color.RESET}\n")

    q = Queue()
    print_step("1", "enqueue 入队")
    for msg in ["订单1", "订单2", "订单3", "订单4"]:
        q.enqueue(msg)
        print_note(f"enqueue('{msg}')")
    q.print_structure()

    print_step("2", "dequeue 出队 (FIFO)")
    while not q.is_empty():
        print_note(f"dequeue() → '{q.dequeue()}'")

    print_key_point("队列 = FIFO。先来的先服务。就像排队——先到的人先被处理。")
