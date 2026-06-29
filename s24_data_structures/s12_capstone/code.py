#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s12: 综合项目 — AI Agent 平台骨架

═══════════════════════════════════════════════════════════════
把前 11 章的数据结构全部用在一个真实的系统中。

项目骨架包含:
  - Graph Workflow (s11: DAG + 拓扑排序)
  - Task Queue        (s03: 队列管理待执行任务)
  - File Storage      (s04: 树形目录管理 agent 定义)
  - Key-Value Cache   (s05: 哈希表缓存 LLM 响应)
  - Search History    (s10: 倒排索引搜索历史对话)
  - Versioning        (s01: commit chain 记录修改历史)

这是一个骨架——你来实现每个模块的具体逻辑。
═══════════════════════════════════════════════════════════════

运行: python s24_data_structures/s12_capstone/code.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import (
    Color, print_header, print_step, print_note, print_key_point, print_success,
)

# 导入前 11 章的数据结构
from s01_mini_git.linked_list import LinkedList
from s01_mini_git.commit_chain import CommitChain
from s02_mini_browser.stack import Stack
from s03_mini_mq.queue import Queue
from s04_mini_fs.tree import Tree, TreeNode
from s05_mini_redis.hash_table import HashTable
from s07_mini_leaderboard.skip_list import SkipList
from s09_mini_db_index.bplus_tree import BPlusTree
from s10_mini_search.inverted_index import InvertedIndex
from s11_mini_agent.graph import Graph


class AIAgentPlatform:
    """
    AI Agent 平台骨架

    模块:
      workflow_engine  — DAG 编排 agent 工作流
      task_queue       — 管理待执行任务
      file_storage     — 树形存储 agent 定义
      llm_cache        — 哈希表缓存 LLM 响应
      search_index     — 倒排索引搜索历史
      version_history  — commit chain 记录修改
    """

    def __init__(self):
        # s11: 图 — Workflow 引擎
        self.workflow_engine = Graph(directed=True)

        # s03: 队列 — 任务队列
        self.task_queue = Queue()

        # s04: 树 — 文件存储
        self.file_storage = Tree("/agents")
        self.file_storage.add_node(self.file_storage.root, "definitions")
        self.file_storage.add_node(self.file_storage.root, "logs")

        # s05: 哈希表 — LLM 响应缓存
        self.llm_cache = HashTable()

        # s10: 倒排索引 — 搜索历史
        self.search_index = InvertedIndex()

        # s01: commit chain — 版本历史
        self.version_history = CommitChain()

        print_success("AI Agent 平台骨架已初始化")

    def status(self):
        """显示所有模块状态"""
        print(f"\n  {Color.HIGHLIGHT}AI Agent 平台 — 模块状态:{Color.RESET}")
        print(f"    Workflow 节点数: {len(self.workflow_engine.nodes)}")
        print(f"    任务队列: {len(self.task_queue)} 待处理")
        print(f"    缓存条目: {len(self.llm_cache)} 条")
        print(f"    文档索引: {self.search_index.stats()}")
        print(f"    版本历史: {len(self.version_history.commits_by_hash)} 个 commit")


def main():
    print_header("s12: 综合项目 — AI Agent 平台")

    print(f"""
  {Color.HIGHLIGHT}前 11 章的数据结构，现在在一个系统中协同工作:{Color.RESET}

    {Color.DIM}s01 链表 + DAG{Color.RESET}     →  版本管理 (commit chain)
    {Color.DIM}s02 栈{Color.RESET}           →  操作撤销 (undo stack)
    {Color.DIM}s03 队列{Color.RESET}         →  任务调度 (task queue)
    {Color.DIM}s04 树{Color.RESET}           →  文件组织 (agent 定义)
    {Color.DIM}s05 哈希表{Color.RESET}       →  响应缓存 (LLM cache)
    {Color.DIM}s07 跳表{Color.RESET}         →  排行榜 (agent 评分)
    {Color.DIM}s09 B+ 树{Color.RESET}        →  数据索引 (对话存储)
    {Color.DIM}s10 倒排索引{Color.RESET}     →  全文搜索 (历史对话)
    {Color.DIM}s11 图 + DAG{Color.RESET}     →  Workflow 编排
""")

    platform = AIAgentPlatform()
    platform.status()

    print_step("你的任务", "让这些模块真正工作起来！")
    print_note("每个模块的接口已定义，底层数据结构已实现。")
    print_note("你的任务是把它们连起来，让整个平台真正运行。")
    print_note("例如:")
    print_note("  1. 用 commit_chain 记录每次修改")
    print_note("  2. 用 hash_table 缓存 LLM 的重复响应")
    print_note("  3. 用 inverted_index 索引所有对话历史")
    print_note("  4. 用 graph 编排一个完整的 agent workflow")

    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"\n{Color.SUCCESS}🎉 s24 全部 12 章完成！{Color.RESET}")
    print(f"{Color.DIM}从链表到图，从 Mini Git 到 AI Agent 平台。{Color.RESET}")
    print(f"{Color.DIM}你不仅学会了数据结构，更理解了它们为什么存在。{Color.RESET}\n")


if __name__ == "__main__":
    main()
