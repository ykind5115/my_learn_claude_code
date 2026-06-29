#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini Agent Framework — 基于图的 Workflow 编排

═══════════════════════════════════════════════════════════════
AI Agent 的 Workflow = DAG:
  节点 = 任务 (LLM 调用 / 工具调用 / 条件判断)
  边   = 数据流 / 依赖关系
  拓扑排序 = 执行顺序

你的任务: 实现 AgentFramework 类中标记为 TODO 的方法。
"""

import sys
from pathlib import Path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from s11_mini_agent.graph import Graph


class MockLLM:
    """模拟 LLM — 返回预设响应"""
    def __init__(self, responses=None):
        self.responses = responses or {}
        self.call_count = 0

    def invoke(self, prompt):
        self.call_count += 1
        return self.responses.get(prompt, f"Mock response #{self.call_count}: {prompt[:30]}...")


class AgentNode:
    """Workflow 中的节点"""
    def __init__(self, name, node_type="task", func=None):
        self.name = name
        self.type = node_type  # task / tool / condition / start / end
        self.func = func       # 要执行的函数


class AgentFramework:
    """迷你 AI Agent 框架"""

    def __init__(self):
        self.graph = Graph(directed=True)
        self.nodes = {}  # name → AgentNode
        self.llm = MockLLM()

    def add_node(self, name, node_type="task", func=None):
        """添加节点到 Workflow"""
        self.graph.add_node(name)
        self.nodes[name] = AgentNode(name, node_type, func)

    def add_edge(self, from_node, to_node):
        """添加依赖关系"""
        self.graph.add_edge(from_node, to_node)

    def validate(self):
        """
        验证 Workflow 是否合法 (无环)。

        提示: return not self.graph.has_cycle()
        """
        # TODO: 实现验证
        raise NotImplementedError("TODO: 实现 validate")

    def get_execution_order(self):
        """
        获取拓扑排序后的执行顺序。

        提示: return self.graph.topological_sort()
        """
        # TODO: 实现执行顺序
        raise NotImplementedError("TODO: 实现 get_execution_order")

    def run(self):
        """执行 Workflow"""
        order = self.get_execution_order()
        if order is None:
            return "Workflow 中存在环！无法执行。"
        results = {}
        for name in order:
            node = self.nodes.get(name)
            if node and node.func:
                results[name] = node.func()
                print(f"    执行: {name} → {results[name]}")
        return results


class DemoAgentFramework(AgentFramework):
    def validate(self):
        return not self.graph.has_cycle()

    def get_execution_order(self):
        return self.graph.topological_sort()
