#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单向链表 (Singly Linked List)

链表是最简单的「动态有序集合」。
每个节点 (Node) 存储一个值 + 指向下一个节点的引用。

和数组的关键区别:
  - 数组: 连续内存, O(1) 随机访问, O(n) 插入/删除(中间)
  - 链表: 离散内存, O(n) 随机访问, O(1) 插入/删除(已知位置)

Git 的 commit chain 就是一个单向链表: 每个 commit 指向它的 parent。
"""


class Node:
    """链表节点"""

    def __init__(self, value):
        self.value = value
        self.next = None  # 指向下一个节点

    def __repr__(self):
        return f"Node({self.value!r})"


class LinkedList:
    """
    单向链表

    操作:
      append(value)   — O(n) 尾部追加
      prepend(value)  — O(1) 头部插入
      find(value)     — O(n) 按值查找
      insert_after(node, value) — O(1) 在指定节点后插入
      delete(value)   — O(n) 删除第一个匹配节点
      traverse()      — O(n) 遍历所有节点
      to_list()       — O(n) 转为 Python list

    空间复杂度: O(n)
    """

    def __init__(self):
        self.head = None  # 头节点 (链表入口)
        self._size = 0

    # ── 基本操作 ─────────────────────────────────────────────

    def append(self, value):
        """在尾部追加节点 — O(n)"""
        new_node = Node(value)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:  # 遍历到最后一个节点
                current = current.next
            current.next = new_node
        self._size += 1

    def prepend(self, value):
        """在头部插入节点 — O(1)"""
        new_node = Node(value)
        new_node.next = self.head
        self.head = new_node
        self._size += 1

    def find(self, value):
        """按值查找节点 — O(n)，返回第一个匹配的 Node 或 None"""
        current = self.head
        while current:
            if current.value == value:
                return current
            current = current.next
        return None

    def insert_after(self, node, value):
        """在指定节点后插入 — O(1)"""
        if node is None:
            raise ValueError("node 不能为 None")
        new_node = Node(value)
        new_node.next = node.next
        node.next = new_node
        self._size += 1

    def delete(self, value):
        """删除第一个匹配值的节点 — O(n)"""
        if self.head is None:
            return False

        # 删除头节点
        if self.head.value == value:
            self.head = self.head.next
            self._size -= 1
            return True

        # 在链表中查找
        current = self.head
        while current.next:
            if current.next.value == value:
                current.next = current.next.next  # 跳过被删除的节点
                self._size -= 1
                return True
            current = current.next
        return False

    def traverse(self):
        """遍历所有节点 — O(n)，生成器"""
        current = self.head
        while current:
            yield current
            current = current.next

    def to_list(self):
        """转为 Python list — O(n)"""
        return [node.value for node in self.traverse()]

    # ── 信息方法 ─────────────────────────────────────────────

    def __len__(self):
        return self._size

    def __contains__(self, value):
        return self.find(value) is not None

    def __iter__(self):
        return self.traverse()

    def __repr__(self):
        if self.head is None:
            return "LinkedList([])"
        nodes_str = " → ".join(repr(n.value) for n in self.traverse())
        return f"LinkedList([{nodes_str}])"

    def print_structure(self):
        """以 ASCII 图形打印链表结构"""
        if self.head is None:
            print("  (空链表)")
            return

        current = self.head
        i = 0
        while current:
            marker = " [HEAD]" if i == 0 else ""
            print(f"  [{i}]{marker} {current.value!r}")
            if current.next:
                print(f"       ↓")
            current = current.next
            i += 1


# ═══════════════════════════════════════════════════════════════
# 演示代码
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from utils import Color, print_step, print_note, print_key_point

    print(f"\n{Color.HEADER}  单向链表 — 基础演示{Color.RESET}\n")

    # 创建链表
    print_step("1", "创建链表并添加元素")
    ll = LinkedList()
    ll.append("commit-A")
    ll.append("commit-B")
    ll.append("commit-C")
    ll.prepend("commit-init")
    print(f"  {ll}")
    ll.print_structure()

    # 查找
    print_step("2", "查找和遍历")
    found = ll.find("commit-B")
    print_note(f"找到: {found}")
    print_note(f"遍历: {ll.to_list()}")

    # 插入
    print_step("3", "在指定节点后插入")
    node_a = ll.find("commit-A")
    ll.insert_after(node_a, "commit-A-hotfix")
    print(f"  {ll}")
    ll.print_structure()

    print_key_point(
        "链表的关键特征:\n"
        "    - 每个节点只知道「下一个是谁」(单向)\n"
        "    - 无法直接访问「第 N 个元素」，必须从头遍历\n"
        "    - 插入/删除「已知位置后面」是 O(1)的"
    )
