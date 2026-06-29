#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini File System — 树形目录结构

═══════════════════════════════════════════════════════════════
Linux 文件系统 = 一棵倒置的树:
  / 是根节点
  目录是内部节点 (有 children)
  文件是叶子节点 (无 children)

你的任务: 实现 FileSystem 类中标记为 TODO 的方法。
"""

import sys
from pathlib import Path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from s04_mini_fs.tree import Tree, TreeNode


class File:
    """文件 (叶子节点存储的数据)"""
    def __init__(self, name, content=""):
        self.name = name
        self.content = content


class FileSystem:
    """迷你文件系统 — 基于树"""

    def __init__(self):
        self.tree = Tree("/")
        self.current_dir = self.tree.root  # 当前工作目录
        self._files = {}  # 完整路径 → File 对象

    def mkdir(self, name):
        """
        创建目录。
        在当前目录下创建一个新的子目录节点。
        """
        # TODO: 实现 mkdir
        # 检查: 当前目录下是否已有同名节点
        # 创建: self.tree.add_node(self.current_dir, name)
        raise NotImplementedError("TODO: 实现 mkdir")

    def touch(self, name, content=""):
        """
        创建文件。
        在当前目录下创建一个文件节点 + File 对象。
        """
        # TODO: 实现 touch
        raise NotImplementedError("TODO: 实现 touch")

    def cd(self, path):
        """
        切换工作目录。
        支持 ".." (上级目录) 和绝对/相对路径。
        """
        # TODO: 实现 cd
        raise NotImplementedError("TODO: 实现 cd")

    def ls(self):
        """
        列出当前目录下的所有文件和子目录。
        返回: [(名称, 类型), ...]  类型 = "dir" 或 "file"
        """
        # TODO: 实现 ls
        raise NotImplementedError("TODO: 实现 ls")

    def pwd(self):
        """打印当前工作目录的完整路径"""
        return self.current_dir.path()


class DemoFileSystem(FileSystem):
    """演示用完整实现"""

    def mkdir(self, name):
        if self.current_dir.get_child(name):
            print(f"    mkdir: '{name}' 已存在")
            return None
        node = self.tree.add_node(self.current_dir, name)
        print(f"    mkdir: {node.path()}")
        return node

    def touch(self, name, content=""):
        node = self.tree.add_node(self.current_dir, name)
        filepath = node.path()
        self._files[filepath] = File(name, content)
        print(f"    touch: {filepath}")

    def cd(self, path):
        if path == "..":
            if self.current_dir.parent:
                self.current_dir = self.current_dir.parent
        elif path.startswith("/"):
            target = self.tree.find_by_path(path)
            if target and target.children is not None:
                self.current_dir = target
        else:
            target = self.current_dir.get_child(path)
            if target and isinstance(target, TreeNode):
                self.current_dir = target
        print(f"    cd: {self.pwd()}")

    def ls(self):
        results = []
        for child in self.current_dir.children:
            t = "dir" if child.children else "file"
            results.append((child.name, t))
            print(f"    {child.name}/" if t == "dir" else f"    {child.name}")
        return results
