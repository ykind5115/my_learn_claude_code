#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图 (Graph) — 多对多关系

图是树和 DAG 的推广——节点之间可以任意连接。

表示方法: 邻接表 (adjacency list)
  每个节点存储一个列表，包含它连接到的所有邻居。

关键操作:
  add_node(name)           — O(1)
  add_edge(from, to)       — O(1)
  topological_sort()       — O(V + E)  (DAG 才有意义)
  has_cycle()              — O(V + E)  (DFS 检测)
  bfs(start)               — O(V + E)  (最短路径)
  dfs(start)               — O(V + E)  (深度优先遍历)

和树的区别: 图中节点可以有多个「入边」(多个来源)。
和 DAG 的区别: 图可以有环，DAG 不能。
"""

from collections import deque
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import Color


class GraphNode:
    """图节点"""
    def __init__(self, name, data=None):
        self.name = name
        self.data = data
        self.edges = []      # 出边: 指向的邻居节点名
        self.in_edges = []   # 入边: 来自哪些节点

    def __repr__(self):
        return f"Node({self.name}, out={len(self.edges)}, in={len(self.in_edges)})"


class Graph:
    """
    图 — 邻接表实现

    支持 DAG 检测和拓扑排序。
    """

    def __init__(self, directed=True):
        self.nodes = {}      # name → GraphNode
        self.directed = directed

    def add_node(self, name, data=None):
        """添加节点 — O(1)"""
        if name not in self.nodes:
            self.nodes[name] = GraphNode(name, data)
        return self.nodes[name]

    def add_edge(self, from_name, to_name):
        """添加边 — O(1)"""
        from_node = self.add_node(from_name)
        to_node = self.add_node(to_name)
        if to_name not in from_node.edges:
            from_node.edges.append(to_name)
            to_node.in_edges.append(from_name)

    def topological_sort(self):
        """
        拓扑排序 (Kahn 算法) — O(V + E)

        DAG 才有效——如果有环，返回 None。
        用于 Workflow 编排: 确定任务的执行顺序。
        """
        in_degree = {name: len(node.in_edges) for name, node in self.nodes.items()}
        queue = deque([name for name, deg in in_degree.items() if deg == 0])
        result = []

        while queue:
            name = queue.popleft()
            result.append(name)
            for neighbor in self.nodes[name].edges:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(self.nodes):
            # 还有节点没被访问 → 有环
            remaining = set(self.nodes.keys()) - set(result)
            print(f"    {Color.WARNING}检测到环！涉及节点: {remaining}{Color.RESET}")
            return None
        return result

    def has_cycle(self):
        """检测是否有环 — O(V + E)"""
        return self.topological_sort() is None

    def bfs(self, start_name):
        """
        广度优先搜索 — O(V + E)

        逐层遍历。用于找最短路径 (无权图)。
        """
        if start_name not in self.nodes:
            return []
        visited = set()
        queue = deque([start_name])
        result = []
        while queue:
            name = queue.popleft()
            if name not in visited:
                visited.add(name)
                result.append(name)
                for neighbor in self.nodes[name].edges:
                    if neighbor not in visited:
                        queue.append(neighbor)
        return result

    def dfs(self, start_name, visited=None):
        """
        深度优先搜索 — O(V + E)

        沿一条路走到底，再回溯。
        """
        if visited is None:
            visited = set()
        visited.add(start_name)
        result = [start_name]
        for neighbor in self.nodes[start_name].edges:
            if neighbor not in visited:
                result.extend(self.dfs(neighbor, visited))
        return result

    def print_structure(self):
        """打印邻接表"""
        print(f"\n  {Color.HIGHLIGHT}图结构 (邻接表):{Color.RESET}")
        for name, node in self.nodes.items():
            edges_str = " → ".join(node.edges) if node.edges else "(无出边)"
            in_str = ", ".join(node.in_edges) if node.in_edges else "无"
            print(f"    {name}: out=[{edges_str}], in=[{in_str}]")


# ═══════════════════════════════════════════════════════════════
# 演示
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    from utils import print_step, print_key_point, print_note

    print(f"\n{Color.HEADER}  图 — 多对多关系 + DAG 检测{Color.RESET}\n")

    g = Graph(directed=True)

    print_step("1", "构建 Workflow DAG")
    g.add_edge("start", "fetch_data")
    g.add_edge("start", "load_config")
    g.add_edge("fetch_data", "process")
    g.add_edge("load_config", "process")
    g.add_edge("process", "validate")
    g.add_edge("validate", "end")
    g.print_structure()

    print_step("2", "拓扑排序 — 确定执行顺序")
    order = g.topological_sort()
    if order:
        print(f"    {Color.SUCCESS}{' → '.join(order)}{Color.RESET}")

    print_step("3", "BFS 和 DFS")
    print_note(f"BFS 从 'start': {g.bfs('start')}")
    print_note(f"DFS 从 'start': {g.dfs('start')}")

    print_step("4", "环检测")
    print_note(f"有效 DAG (无环)? {not g.has_cycle()}")
    g.add_edge("end", "start")  # 制造一个环
    print_note(f"加边 end→start 后有环? {g.has_cycle()}")

    print_key_point("图 = 最通用的数据结构。Workflow/DAG/网络拓扑都用图表示。")
