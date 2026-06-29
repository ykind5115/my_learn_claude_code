#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
栈 (Stack) — LIFO (Last In, First Out)

栈是最简单的受限数据结构——只能在一端(栈顶)插入和删除。
就像一摞盘子: 你只能动最上面那个。

关键操作:
  push(item)  — O(1) 压入栈顶
  pop()       — O(1) 弹出栈顶
  peek()      — O(1) 查看栈顶(不弹出)
  is_empty()  — O(1)

工程应用:
  - 浏览器前进/后退 (两个栈)
  - 函数调用栈 (Python/C 的运行时)
  - 撤销操作 (Ctrl+Z)
  - DFS (深度优先搜索)
"""


class Stack:
    """
    基于 Python list 的栈实现

    空间复杂度: O(n)
    """

    def __init__(self):
        self._items = []

    def push(self, item):
        """压入栈顶 — O(1)"""
        self._items.append(item)

    def pop(self):
        """
        弹出栈顶元素 — O(1)
        栈空时抛出 IndexError
        """
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        """
        查看栈顶元素(不弹出) — O(1)
        栈空时抛出 IndexError
        """
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def is_empty(self):
        """栈是否为空 — O(1)"""
        return len(self._items) == 0

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"Stack({self._items})"

    def print_structure(self):
        """以 ASCII 图形打印栈"""
        if self.is_empty():
            print("  (空栈)")
            return
        print(f"  ┌──────┐")
        for i, item in enumerate(reversed(self._items)):
            marker = " ← TOP" if i == 0 else ""
            print(f"  │ {str(item):<20} │{marker}")
        print(f"  └──────┘")


class LinkedListStack:
    """
    基于链表的栈实现 (展示栈的底层可以是不同数据结构)

    同样 O(1) push/pop/peek。
    """

    class _Node:
        def __init__(self, value, next_node=None):
            self.value = value
            self.next = next_node

    def __init__(self):
        self._top = None  # 栈顶节点
        self._size = 0

    def push(self, item):
        """新节点成为新的栈顶 — O(1)"""
        new_node = self._Node(item, self._top)
        self._top = new_node
        self._size += 1

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        value = self._top.value
        self._top = self._top.next
        self._size -= 1
        return value

    def peek(self):
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._top.value

    def is_empty(self):
        return self._top is None

    def __len__(self):
        return self._size


# ═══════════════════════════════════════════════════════════════
# 演示代码
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from utils import Color, print_step, print_key_point, print_note

    print(f"\n{Color.HEADER}  栈 — LIFO 演示{Color.RESET}\n")

    s = Stack()

    print_step("1", "push 入栈")
    for page in ["首页", "搜索页", "商品详情", "购物车"]:
        s.push(page)
        print_note(f"push('{page}') → 栈大小: {len(s)}")
    s.print_structure()

    print_step("2", "peek 查看栈顶")
    print_note(f"栈顶: {s.peek()} (栈不变)")

    print_step("3", "pop 出栈")
    while not s.is_empty():
        print_note(f"pop() → '{s.pop()}'  (剩余: {len(s)})")

    print_key_point("栈 = LIFO。最后进来的最先出去。就像浏览器的后退按钮。")
