#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
树 (Tree) — 层级结构

树是「一对多」关系的标准数据结构。每个节点有一个 parent、多个 children。

和链表的区别: 链表是特殊的树——每个节点只有一个 child (退化树)。
和 DAG 的区别: 树中每个节点只有一个 parent，DAG 中可以有多个。

工程应用:
  - 文件系统 (目录 = 节点, 子目录/文件 = children)
  - DOM 树 (HTML 的结构)
  - 组织架构图
  - 编译器 AST (抽象语法树)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import Color


class TreeNode:
    """树的节点"""

    def __init__(self, name, data=None):
        self.name = name
        self.data = data
        self.parent = None
        self.children = []   # 子节点列表

    def add_child(self, child_node):
        """添加子节点"""
        child_node.parent = self
        self.children.append(child_node)

    def remove_child(self, child_name):
        """按名称移除子节点"""
        for i, child in enumerate(self.children):
            if child.name == child_name:
                del self.children[i]
                return True
        return False

    def get_child(self, name):
        """按名称获取子节点"""
        for child in self.children:
            if child.name == name:
                return child
        return None

    def is_leaf(self):
        return len(self.children) == 0

    def path(self):
        """返回从根到当前节点的完整路径"""
        parts = []
        node = self
        while node:
            parts.append(node.name)
            node = node.parent
        return "/" + "/".join(reversed(parts))

    def __repr__(self):
        return f"TreeNode({self.name}, children={len(self.children)})"


class Tree:
    """
    通用树结构

    操作:
      add_node(parent, name)    — 添加节点
      find(path)                — 按路径查找
      traverse_preorder()       — 前序遍历
      traverse_postorder()      — 后序遍历
      traverse_levelorder()     — 层序遍历 (BFS)
    """

    def __init__(self, root_name="/"):
        self.root = TreeNode(root_name)
        self._node_map = {root_name: self.root}  # 快速按名查找 (仅演示用)

    def add_node(self, parent, name, data=None):
        """在 parent 下添加子节点"""
        node = TreeNode(name, data)
        parent.add_child(node)
        self._node_map[name] = node
        return node

    def find_by_path(self, path):
        """
        按路径查找节点 — O(depth × branching)

        例: "/home/user/docs" → root → home → user → docs
        """
        if path == "/":
            return self.root
        parts = [p for p in path.strip("/").split("/") if p]
        current = self.root
        for part in parts:
            found = current.get_child(part)
            if not found:
                return None
            current = found
        return current

    def traverse_preorder(self, node=None):
        """
        前序遍历: 先访问父节点，再依次访问子节点。
        用于: 复制目录树 (先创建父目录，再创建子内容)
        """
        if node is None:
            node = self.root
        yield node
        for child in node.children:
            yield from self.traverse_preorder(child)

    def traverse_postorder(self, node=None):
        """
        后序遍历: 先访问子节点，再访问父节点。
        用于: 删除目录树 (先删子内容，再删父目录)
        """
        if node is None:
            node = self.root
        for child in node.children:
            yield from self.traverse_postorder(child)
        yield node

    def traverse_levelorder(self):
        """层序遍历 (BFS) — 逐层访问"""
        from collections import deque
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            yield node
            for child in node.children:
                queue.append(child)

    def print_tree(self):
        """打印 ASCII 目录树"""
        print(f"\n  {Color.HIGHLIGHT}目录树:{Color.RESET}")

        def _print(node, prefix=""):
            connector = "├── " if node.parent else ""
            file_marker = "" if node.children else f" {Color.DIM}(file){Color.RESET}"
            print(f"  {prefix}{connector}{Color.HIGHLIGHT}{node.name}{Color.RESET}{file_marker}")
            for i, child in enumerate(node.children):
                is_last = (i == len(node.children) - 1)
                new_prefix = prefix + ("│   " if not node.parent else "    " if node.parent and not prefix else "    ")
                if node.parent:
                    new_prefix = prefix + ("│   " if not is_last else "    ")
                else:
                    new_prefix = prefix + ("│   " if not is_last else "    ")
                _print(child, new_prefix)

        _print(self.root)


# ═══════════════════════════════════════════════════════════════
# 演示
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    from utils import print_step, print_key_point, print_note

    print(f"\n{Color.HEADER}  树 — 层级结构演示{Color.RESET}\n")

    tree = Tree("/")

    print_step("1", "构建文件系统树")
    home = tree.add_node(tree.root, "home")
    user = tree.add_node(home, "user")
    tree.add_node(user, "documents")
    tree.add_node(user, "Downloads")
    tree.add_node(user, "Desktop")
    etc = tree.add_node(tree.root, "etc")
    tree.add_node(etc, "nginx")
    tree.add_node(tree.root, "tmp")
    tree.print_tree()

    print_step("2", "前序遍历 (创建文件用)")
    print(f"  {Color.DIM}{[n.name for n in tree.traverse_preorder()]}{Color.RESET}")

    print_step("3", "后序遍历 (删除文件用)")
    print(f"  {Color.DIM}{[n.name for n in tree.traverse_postorder()]}{Color.RESET}")

    print_key_point("树 = 一对多层级结构。文件系统是最直观的树。")
