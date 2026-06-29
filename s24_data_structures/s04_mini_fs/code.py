#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s04: Mini File System — 树

运行: python s24_data_structures/s04_mini_fs/code.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import (
    Color, print_header, print_step, print_note, print_key_point, print_success,
)
from s04_mini_fs.tree import Tree, TreeNode
from s04_mini_fs.mini_fs import DemoFileSystem


def demo_tree():
    print_step(1, "树的遍历 — 三种方式")
    tree = Tree("/")
    home = tree.add_node(tree.root, "home")
    user = tree.add_node(home, "user")
    tree.add_node(user, "docs")
    tree.add_node(user, "pics")
    tree.add_node(tree.root, "etc")
    tree.print_tree()

    print_note(f"前序 (创建): {[n.name for n in tree.traverse_preorder()]}")
    print_note(f"后序 (删除): {[n.name for n in tree.traverse_postorder()]}")
    print_note(f"层序 (BFS):  {[n.name for n in tree.traverse_levelorder()]}")

    print_key_point(
        "三种遍历的应用:\n"
        "    前序 → 复制目录 (先建父文件夹再填内容)\n"
        "    后序 → 删除目录 (先删内容再删空文件夹)\n"
        "    层序 → 按层级展示 (ls -R)"
    )


def demo_filesystem():
    print_step(2, "Mini File System — 树就是文件系统")
    fs = DemoFileSystem()
    fs.mkdir("home")
    fs.mkdir("etc")
    fs.cd("home")
    fs.mkdir("user")
    fs.cd("user")
    fs.touch("README.md", "# Hello")
    fs.touch("config.txt", "DEBUG=True")
    fs.cd("..")
    fs.cd("..")
    fs.ls()
    fs.cd("home")
    fs.ls()

    print_key_point("Linux 文件系统 = 树。每个目录是一个节点，路径 = 从根遍历到目标。")


def main():
    print_header("s04: Mini File System — 树")
    print(f"  {Color.HIGHLIGHT}数据结构: 树 (Tree) — 一对多层级结构{Color.RESET}\n")

    demo_tree()
    demo_filesystem()

    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"\n{Color.SUCCESS}✅ 树 = 层级组织。文件系统、DOM、组织架构——都是树。{Color.RESET}")
    print(f"{Color.HIGHLIGHT}下一步: 打开 mini_fs.py，实现 TODO 方法！{Color.RESET}\n")


if __name__ == "__main__":
    main()
