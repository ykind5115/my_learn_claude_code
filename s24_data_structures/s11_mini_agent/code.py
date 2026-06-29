#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s11: Mini Agent Framework — 图 + DAG + Workflow

运行: python s24_data_structures/s11_mini_agent/code.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import (
    Color, print_header, print_step, print_note, print_key_point, print_success, print_warning,
)
from s11_mini_agent.graph import Graph
from s11_mini_agent.mini_agent import DemoAgentFramework


def demo_graph():
    print_step(1, "图的基本操作 — 邻接表")
    g = Graph(directed=True)
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    g.add_edge("B", "D")
    g.add_edge("C", "D")
    g.add_edge("D", "E")
    g.print_structure()

    print_note(f"BFS from A: {g.bfs('A')}")
    print_note(f"DFS from A: {g.dfs('A')}")
    print_note(f"拓扑排序: {g.topological_sort()}")


def demo_agent_workflow():
    print_step(2, "Agent Workflow — DAG 编排任务")

    agent = DemoAgentFramework()

    # 构建一个简单的 RAG workflow
    agent.add_node("start", node_type="start")
    agent.add_node("fetch_docs")
    agent.add_node("rank_docs")
    agent.add_node("generate_answer")
    agent.add_node("validate_output")
    agent.add_node("end", node_type="end")

    agent.add_edge("start", "fetch_docs")
    agent.add_edge("fetch_docs", "rank_docs")
    agent.add_edge("rank_docs", "generate_answer")
    agent.add_edge("generate_answer", "validate_output")
    agent.add_edge("validate_output", "end")

    print_note("RAG Workflow: start → fetch → rank → generate → validate → end")
    order = agent.get_execution_order()
    if order:
        print_note(f"执行顺序: {' → '.join(order)}")

    print_step(3, "DAG 验证 — 检测循环依赖")
    print_note(f"合法 DAG? {agent.validate()}")

    print_note("添加一个循环边 validate_output → fetch_docs ...")
    agent.add_edge("validate_output", "fetch_docs")
    print_warning(f"合法 DAG? {agent.validate()} — 检测到环！")


def main():
    print_header("s11: Mini Agent Framework — 图 + DAG")
    print(f"  {Color.HIGHLIGHT}数据结构: 图 + DAG — Workflow 编排的核心{Color.RESET}\n")
    demo_graph()
    demo_agent_workflow()
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"\n{Color.SUCCESS}✅ 图 = 最通用的数据结构。Workflow = DAG + 拓扑排序。{Color.RESET}")
    print(f"{Color.HIGHLIGHT}下一步: 打开 mini_agent.py，实现 TODO 方法！{Color.RESET}\n")


if __name__ == "__main__":
    main()
