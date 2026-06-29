#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini Git — 链表 + 哈希 + DAG 的综合应用

这是一个「小型版本控制系统」的框架。
数据结构 (linked_list.py / commit_chain.py / dag.py) 已为你实现。
你的任务是把它们组装成一个能工作的 Mini Git。

MiniGit 支持的指令:
  git init              — 初始化仓库
  git commit -m "msg"   — 创建新 commit
  git log               — 查看提交历史
  git branch <name>     — 创建分支
  git checkout <name>   — 切换到分支
  git merge <branch>    — 合并指定分支到当前分支

═══════════════════════════════════════════════════════════════
框架说明:
  - 标记为 # TODO 的地方需要你来实现
  - 接口已经定义好，数据结构已经就位
  - 每个 TODO 都有提示，解释这一步在时间树上的含义
═══════════════════════════════════════════════════════════════
"""

import sys
from pathlib import Path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from s01_mini_git.commit_chain import CommitChain, Commit
from s01_mini_git.dag import DAG


class MiniGit:
    """
    迷你版本控制系统

    底层使用:
      - CommitChain: commit 的链表历史 (单向链表)
      - DAG: 分支合并关系 (有向无环图)
      - dict (哈希表): 分支名 → commit 的映射 (O(1) 查找)
    """

    def __init__(self):
        # 分支: 分支名 → 指向的 commit 对象
        # 这就是「标签贴纸」——分支只是一个指向 commit 的指针
        self.branches = {"main": None}

        # HEAD: 当前所在的分支名
        # 「你现在站在哪个分支标签上」
        self.HEAD = "main"

        # commit 历史链
        self.chain = CommitChain()

        # DAG: 记录所有 commit 之间的 parent 关系
        self.dag = DAG()

        # 所有 commit 的哈希索引 (hash → Commit)
        # 这模拟了 Git 的 object store——通过哈希 O(1) 定位对象
        self.objects = {}

        # 暂存区: 当前要提交的文件内容 (简化版)
        self.staging = {}

    # ═══════════════════════════════════════════════════════════
    # git init — 初始化
    # ═══════════════════════════════════════════════════════════
    # 已实现，不需要修改。

    @classmethod
    def init(cls):
        """创建一个新的 Mini Git 仓库"""
        return cls()

    # ═══════════════════════════════════════════════════════════
    # git commit — 创建新 commit
    # ═══════════════════════════════════════════════════════════

    def commit(self, message):
        """
        创建一个新的 commit。

        在时间树上的操作:
          1. 以当前分支指向的 commit 为 parent
          2. 创建新节点
          3. 新节点加入 commit chain (链表追加)
          4. 新节点加入 DAG (parent 关系)
          5. 当前分支标签移到新节点

        提示: 使用 self.chain.commit(message) 创建 commit，
              然后用 self.dag.add_edge() 记录 parent 关系，
              最后更新 self.branches[self.HEAD] 指向新 commit。
        """
        # TODO: 实现 commit 逻辑
        #
        # 步骤:
        # 1. parent = self.branches[self.HEAD]   # 当前分支指向的 commit
        # 2. commit_obj = self.chain.commit(message)  # 创建新 commit
        # 3. 把 commit_obj 存入 self.objects[commit_obj.hash]
        # 4. 如果有 parent: self.dag.add_edge(commit_obj.hash, parent.hash)
        # 5. self.branches[self.HEAD] = commit_obj   # 分支标签前移
        #
        # 打印: f'[{self.HEAD} {commit_obj.hash[:7]}] {message}'
        #
        raise NotImplementedError("TODO: 实现 git commit")

    # ═══════════════════════════════════════════════════════════
    # git log — 查看历史
    # ═══════════════════════════════════════════════════════════

    def log(self, max_count=None):
        """
        查看当前分支的提交历史。

        从当前分支指向的 commit 开始，沿 parent 指针往回遍历。

        提示: self.chain.log() 已经实现了基础 log，
              但你需要改为从当前分支的 commit 开始，
              而不是从 chain.head_commit 开始。
        """
        # TODO: 实现从当前分支的 commit 开始的 log
        #
        # 提示: 从 self.branches[self.HEAD] 开始，沿 parent 往回走。
        #
        raise NotImplementedError("TODO: 实现 git log")

    # ═══════════════════════════════════════════════════════════
    # git branch — 创建分支
    # ═══════════════════════════════════════════════════════════

    def branch(self, name):
        """
        创建一个新分支，指向当前 commit。

        在时间树上: 在当前节点上贴一张新标签。
        不会复制任何数据——只是创建一个新指针。

        提示: self.branches[name] = self.branches[self.HEAD]
        """
        # TODO: 实现创建分支
        #
        # 检查: 分支名是否已存在？已存在则报错。
        # 否则: self.branches[name] = self.branches[self.HEAD]
        #
        raise NotImplementedError("TODO: 实现 git branch")

    # ═══════════════════════════════════════════════════════════
    # git checkout — 切换分支
    # ═══════════════════════════════════════════════════════════

    def checkout(self, name):
        """
        切换到指定分支。

        在时间树上: 把 HEAD 从当前分支移到目标分支。
        工作区的文件会变成目标分支的版本（文件操作超出本框架范围）。

        提示: self.HEAD = name
        """
        # TODO: 实现切换分支
        #
        # 检查: 分支是否存在？不存在则报错。
        # 否则: self.HEAD = name
        #
        raise NotImplementedError("TODO: 实现 git checkout")

    # ═══════════════════════════════════════════════════════════
    # git merge — 合并分支
    # ═══════════════════════════════════════════════════════════

    def merge(self, branch_name):
        """
        把指定分支合并到当前分支。

        在时间树上: 创建一个 merge commit，它有两个 parent:
          - parent 1: 当前分支指向的 commit
          - parent 2: 被合并分支指向的 commit

        提示: 创建一个特殊的 commit，手动设置它的 parents 列表
              包含两个 parent，然后更新 DAG 和分支指针。
        """
        # TODO: 实现合并逻辑
        #
        # 步骤:
        # 1. 获取当前 commit 和被合并分支的 commit
        # 2. 创建一个新 commit（信息: f"Merge branch '{branch_name}' into {self.HEAD}"）
        # 3. 新 commit 的 parents = [当前commit, 被合并commit]
        # 4. 更新 DAG: 两条边都加上
        # 5. 更新当前分支标签和 objects 索引
        #
        raise NotImplementedError("TODO: 实现 git merge")

    # ═══════════════════════════════════════════════════════════
    # 辅助方法（已实现）
    # ═══════════════════════════════════════════════════════════

    def status(self):
        """显示当前状态"""
        print(f"\n  HEAD → {self.HEAD}")
        print(f"  分支列表:")
        for name, commit in self.branches.items():
            marker = " ← HEAD" if name == self.HEAD else ""
            commit_info = commit.hash[:7] if commit else "(空)"
            print(f"    {name} → {commit_info}{marker}")

    def dag_info(self):
        """显示 DAG 的拓扑排序"""
        order = self.dag.topological_sort()
        if order:
            print(f"\n  提交顺序 (拓扑排序):")
            for i, h in enumerate(order):
                obj = self.objects.get(h)
                if obj:
                    marker = ""
                    for name, c in self.branches.items():
                        if c and c.hash == h:
                            marker += f" [{name}]"
                    print(f"    {i+1}. {h[:7]}{marker}  {obj.message}")


# ═══════════════════════════════════════════════════════════════
# 演示: 框架接口测试 (不包含 TODO 实现)
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from utils import Color, print_step, print_note, print_key_point

    print(f"\n{Color.HEADER}  Mini Git 框架 — 接口预览{Color.RESET}\n")

    git = MiniGit.init()
    git.status()

    print_step("提示", "这是 Mini Git 的框架。")
    print_note("数据结构已实现: linked_list.py, commit_chain.py, dag.py")
    print_note("你的任务: 实现 mini_git.py 中标记为 TODO 的方法")
    print_note("完成后的 Mini Git 支持: init, commit, log, branch, checkout, merge")
