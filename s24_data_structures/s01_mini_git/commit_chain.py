#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Commit Chain — 单向链表的 Git 特化

每个 commit 节点包含:
  - hash: 唯一标识（简化版，用序号模拟）
  - message: 提交信息
  - parent: 指向上一个 commit 的引用（形成链）

这就是 Git 的 commit 历史本质: 一个从最新 commit 开始、沿着 parent 指针
往回走的单向链表。

    [init] → [commit-A] → [commit-B] → [commit-C] (HEAD)
      ↑                                       ↑
    parent=NULL                          parent=commit-B

HEAD 指向最新的 commit。git log 就是从 HEAD 开始，沿着 parent 往回遍历。
"""

import sys
from pathlib import Path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from s01_mini_git.linked_list import Node as LLNode


class Commit:
    """一个 commit 节点"""

    def __init__(self, hash_val, message, parent=None):
        self.hash = hash_val        # 唯一标识
        self.message = message      # 提交信息
        self.parent = parent        # 指向上一个 commit (None = 根 commit)
        # 在 DAG 场景下可以有多个 parent (merge commit)
        self.parents = [parent] if parent else []

    def add_parent(self, parent_commit):
        """添加一个 parent（用于 merge commit）"""
        if parent_commit not in self.parents:
            self.parents.append(parent_commit)

    def __repr__(self):
        parents_str = ",".join(p.hash[:7] for p in self.parents if p) or "None"
        return f"Commit(hash={self.hash[:7]}, msg={self.message!r}, parents=[{parents_str}])"


class CommitChain:
    """
    Commit 历史链 (单向链表视角)

    提供类似 git log 的操作: 从 HEAD 开始沿着 parent 往回遍历。
    """

    def __init__(self):
        self.head_commit = None       # HEAD 指向的 commit
        self.commits_by_hash = {}     # hash → Commit (快速查找)
        self._counter = 0             # 生成简单 hash

    def _make_hash(self):
        """生成一个简化的 commit hash"""
        self._counter += 1
        return f"c{self._counter:04d}"

    def commit(self, message):
        """
        创建一个新的 commit — O(1)

        相当于 git commit:
          1. 创建新 commit 节点
          2. parent 指向当前的 HEAD
          3. HEAD 移动到新节点
        """
        new_hash = self._make_hash()
        new_commit = Commit(new_hash, message, parent=self.head_commit)
        self.commits_by_hash[new_hash] = new_commit
        self.head_commit = new_commit
        return new_commit

    def log(self, max_count=None):
        """
        查看提交历史 — O(n)

        从 HEAD 开始，沿着 parent 指针往回遍历。
        相当于 git log --oneline。
        """
        result = []
        current = self.head_commit
        count = 0
        while current:
            marker = " (HEAD)" if current is self.head_commit else ""
            result.append(f"{current.hash[:7]}{marker}  {current.message}")
            # 如果有多个 parent，取第一个（主链）
            current = current.parents[0] if current.parents else None
            count += 1
            if max_count and count >= max_count:
                break
        return result

    def find(self, hash_prefix):
        """
        通过 hash 前缀查找 commit — O(1)
        这就是 Git 用 SHA-1 哈希定位对象的能力。
        """
        for h, commit in self.commits_by_hash.items():
            if h.startswith(hash_prefix):
                return commit
        return None

    def walk(self):
        """从 HEAD 遍历整条链 — O(n)，生成器"""
        current = self.head_commit
        while current:
            yield current
            current = current.parents[0] if current.parents else None

    def __repr__(self):
        if not self.head_commit:
            return "CommitChain(empty)"
        return f"CommitChain(HEAD={self.head_commit.hash[:7]}, total={len(self.commits_by_hash)})"

    def print_history(self):
        """打印 ASCII 历史图"""
        if not self.head_commit:
            print("  (空历史)")
            return
        print(f"\n  {Color.HIGHLIGHT}Commit 历史:{Color.RESET}")
        for line in self.log():
            print(f"    ● {line}")


# 导入颜色（用于 print_history）
import sys
from pathlib import Path
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))
from utils import Color

# ═══════════════════════════════════════════════════════════════
# 演示代码
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from utils import print_step, print_key_point

    print(f"\n{Color.HEADER}  Commit Chain — Git 的链表本质{Color.RESET}\n")

    chain = CommitChain()

    print_step("1", "创建提交历史（git commit）")
    chain.commit("第一次提交：创建 README")
    chain.commit("添加 main.py")
    chain.commit("修复登录 bug")
    chain.commit("添加单元测试")
    chain.print_history()

    print_step("2", "查看 log（沿 parent 往回走）")
    for line in chain.log():
        print(f"    {line}")

    print_step("3", "通过 hash 查找")
    found = chain.find("c0002")
    if found:
        print(f"    找到: {found}")

    print_key_point(
        "git log 的本质: 从 HEAD 开始，沿着 parent 指针往回遍历链表。\n"
        "    每个 commit 只知道「上一个是谁」，不知道「下一个是谁」。\n"
        "    这就是单向链表的特性——只能往一个方向走。"
    )
