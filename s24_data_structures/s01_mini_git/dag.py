#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DAG (有向无环图) — 链表的多 parent 推广

如果 commit chain 是链表（每个节点一个 parent），
那 merge commit 就需要 DAG（一个节点可以有多个 parent）。

Git 的 commit 历史就是一个 DAG:
  - 节点 = commit
  - 边 = parent 指针（从新 commit 指向旧 commit）
  - 无环 = 不可能出现 A→B→C→A 这种循环
  - 有向 = parent 指针有方向（从子节点指向父节点）

拓扑排序: DAG 中所有节点的一种线性排列，保证对每条边 u→v，u 排在 v 前面。
在 Git 中等价于「按时间顺序排列所有 commit」。
"""

from collections import deque
import sys
from pathlib import Path
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))
from utils import Color


class DAGNode:
    """DAG 节点"""

    def __init__(self, name, data=None):
        self.name = name
        self.data = data
        self.parents = []    # 入边: 指向父节点
        self.children = []   # 出边: 指向子节点

    def add_parent(self, parent_node):
        if parent_node not in self.parents:
            self.parents.append(parent_node)
        if self not in parent_node.children:
            parent_node.children.append(self)

    def __repr__(self):
        parents_str = ",".join(p.name for p in self.parents) or "None"
        children_str = ",".join(c.name for c in self.children) or "None"
        return f"DAGNode({self.name}, parents=[{parents_str}], children=[{children_str}])"


class DAG:
    """
    简化 DAG（用于表示 Git 的 commit 历史）

    特性:
      - 每个节点可以有多个 parent（merge commit）
      - 每个节点可以有多个 children（被多个分支引用）
      - 无环（通过拓扑排序检测）
    """

    def __init__(self):
        self.nodes = {}  # name → DAGNode

    def add_node(self, name, data=None):
        """添加节点 — O(1)"""
        if name not in self.nodes:
            self.nodes[name] = DAGNode(name, data)
        return self.nodes[name]

    def add_edge(self, from_name, to_name):
        """
        添加边 from → to (from 的 parent 是 to)

        在 Git 中: from = 新 commit, to = 它的 parent。
        箭头从新 commit 指向旧 commit。
        """
        from_node = self.add_node(from_name)
        to_node = self.add_node(to_name)
        from_node.add_parent(to_node)

    def topological_sort(self):
        """
        拓扑排序 (Kahn 算法) — O(V + E)

        返回节点的线性排列，保证每个节点排在它的 parent 后面。
        如果图中有环，返回 None。
        """
        # 计算每个节点的入度 (有多少个 parent)
        in_degree = {name: len(node.parents) for name, node in self.nodes.items()}

        # 入度为 0 的节点 (根节点) 入队
        queue = deque([name for name, deg in in_degree.items() if deg == 0])

        result = []
        while queue:
            node_name = queue.popleft()
            result.append(node_name)

            for child in self.nodes[node_name].children:
                in_degree[child.name] -= 1
                if in_degree[child.name] == 0:
                    queue.append(child.name)

        # 如果结果数量 != 节点总数，说明有环
        if len(result) != len(self.nodes):
            return None  # 有环！

        return result

    def has_cycle(self):
        """检测是否有环 — O(V + E)"""
        return self.topological_sort() is None

    def print_structure(self):
        """打印 ASCII 图形"""
        if not self.nodes:
            print("  (空 DAG)")
            return

        # 找到根节点 (没有 parent 的节点)
        roots = [n for n in self.nodes.values() if not n.parents]

        print(f"\n  {Color.HIGHLIGHT}DAG 结构 (从根节点向下):{Color.RESET}")

        def print_node(node, indent=0, visited=None):
            if visited is None:
                visited = set()
            if node.name in visited:
                print(f"{'  ' * indent}{Color.DIM}{node.name} (已访问){Color.RESET}")
                return
            visited.add(node.name)

            parent_info = f" ← [{','.join(p.name for p in node.parents)}]" if node.parents else ""

            print(f"{'  ' * indent}● {Color.HIGHLIGHT}{node.name}{Color.RESET}{Color.DIM}{parent_info}{Color.RESET}")
            for child in node.children:
                print_node(child, indent + 1, visited.copy())

        for root in roots:
            print_node(root)

    def print_topo_order(self):
        """打印拓扑排序结果"""
        order = self.topological_sort()
        if order is None:
            print(f"  {Color.ERROR}图中存在环！无法拓扑排序。{Color.RESET}")
        else:
            print(f"  {Color.HIGHLIGHT}拓扑排序 (从旧到新):{Color.RESET}")
            print(f"  {Color.DIM}{' → '.join(order)}{Color.RESET}")


# ═══════════════════════════════════════════════════════════════
# 演示代码
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from utils import print_step, print_key_point, print_note

    print(f"\n{Color.HEADER}  DAG — Git 分支合并的数学本质{Color.RESET}\n")

    dag = DAG()

    print_step("1", "构建 Git 风格的 commit DAG")
    # main 分支: A → B → C
    #                ↘
    # feature 分支:    D → E
    #                  ↘
    # merge:            M (两个 parent: C 和 E)

    dag.add_edge("C", "B")       # C 的 parent 是 B
    dag.add_edge("B", "A")       # B 的 parent 是 A
    dag.add_edge("E", "D")       # E 的 parent 是 D
    dag.add_edge("D", "B")       # D 的 parent 是 B (feature 从 B 分出)
    dag.add_edge("M", "C")       # merge commit M 的 parent 是 C
    dag.add_edge("M", "E")       # merge commit M 的另一个 parent 是 E

    print_note("commit 关系:")
    print_note("  A ← B ← C ← M")
    print_note("       ↖ D ← E ↗")

    dag.print_structure()

    print_step("2", "拓扑排序 — 按时间顺序排列 commit")
    dag.print_topo_order()

    print_step("3", "环检测")
    print_note(f"有环? {dag.has_cycle()}")

    print_key_point(
        "Git 的 commit 历史 = DAG (有向无环图)\n"
        "    - 有向: parent 指针从子节点指向父节点\n"
        "    - 无环: 不可能出现 A→B→C→A\n"
        "    - merge commit 的特殊之处: 有多个 parent\n"
        "    拓扑排序 = 从旧到新排列所有 commit"
    )
