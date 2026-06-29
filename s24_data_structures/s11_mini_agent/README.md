# s11: Mini Agent Framework — 图 + DAG

> *"树只能表示层级关系。当你需要表示任意连接——任务 A 依赖 B 和 C，B 又依赖 D——你需要图。"*
>
> **前提知识**: 学过 s04（树）和 s01（DAG）。理解拓扑排序的概念（s01）。

---

## 1. 本章工程问题

你在做一个 AI Agent 平台。Agent 的 Workflow 长这样：

```
用户提问
  ↓
理解意图 ──→ 检索文档 ──→ 生成答案 ──→ 返回给用户
  ↓                        ↑
查询数据库 ─────────────────┘
```

这个 Workflow 需要：
1. **表示任务依赖关系**——哪些任务必须在哪些任务之前执行
2. **检测循环依赖**——如果 A 依赖 B，B 依赖 C，C 又依赖 A，死锁了
3. **按正确顺序执行**——先执行没有依赖的任务，再执行依赖它们的任务

**树不够用了**——因为一个节点可能有多个输入（「生成答案」同时依赖「检索文档」和「查询数据库」）。

**你需要图（Graph）**——最通用的数据结构。

---

## 2. 图、树、DAG 的关系

回顾整个 s24 的演进：

```
链表（s01）: ● → ● → ● → ●
  每个节点 1 个 next → 一对一关系

树（s04）:        ●
               /  |  \
              ●   ●   ●
  每个节点 1 个 parent, N 个 children → 一对多关系

DAG（s01）:    ●
              / \
             ●   ●
              \ /
               ●
  每个节点 N 个 parent, N 个 children, 无环 → 多对多 + 单向

图（s11）:     ● ←→ ●
              \   /
               ●─┘
  每个节点 N 个邻居, 可以有环 → 多对多 + 任意方向
```

限制逐层放宽。越宽松的结构，能表达的关系越复杂，但算法也越复杂。

---

## 3. 数据结构原理

### 图的表示：邻接表

```
图:
  A → B, A → C
  B → D
  C → D
  D → E

邻接表:
  A: [B, C]     ← A 指向 B 和 C
  B: [D]        ← B 指向 D
  C: [D]
  D: [E]
  E: []         ← E 没有出边
```

每个节点存一个「出边列表」——它连接到了哪些邻居。

### 拓扑排序：确定执行顺序

```
Kahn 算法:

1. 计算每个节点的入度（有多少个节点指向我）
   A:0, B:1, C:1, D:2, E:1

2. 入度为 0 的节点入队（没有依赖，可以直接执行）
   Queue: [A]

3. 每次出队一个节点，把它指向的邻居的入度减 1
   出队 A → B 入度 -1 = 0 → B 入队
           → C 入度 -1 = 0 → C 入队
   Queue: [B, C]

4. 重复直到队列为空
   出队 B → D 入度 -1 = 1
   出队 C → D 入度 -1 = 0 → D 入队
   ...
   出队 E

结果: A → B → C → D → E
```

### 环检测

```
加一条边 E → A（制造环）:

  A → B → D → E → A → B → ... (无限循环！)

Kahn 算法的结果:
  处理完 B, C, D, E 后，A 的入度仍然是 1（因为 E→A）
  
  len(result) = 4 ≠ 5（总数）→ 有环！
```

---

## 4. Agent Workflow = DAG

### 节点类型

```
start:      入口节点（无入边）
fetch_data: 调用 API 获取数据
process:    处理数据
validate:   验证结果
tool:       调用工具（搜索、计算等）
condition:  条件分支
end:        出口节点（无出边）
```

### 数据在边上流动

```
start → fetch_docs → rank_docs → generate_answer → end
              ↑
         llm_call（返回文档列表）
```

每个节点执行完后，它的输出成为下一个节点的输入。图 + 数据流 = Workflow 引擎。

### LLM 调用是特殊的节点

在真实 Agent 框架中，LLM 调用节点：
- 输入：prompt（可能是前面节点的输出拼接而成）
- 输出：LLM 的回复文本
- 可能失败（需要重试逻辑——还记得 s03 的消息队列吗？）

我们的 Mini Agent 用 MockLLM（返回预设文本）代替真实的 LLM 调用——数据结构才是本章的焦点。

---

## 5. Python 从零实现

打开 `graph.py`，核心代码：

### 图 + 拓扑排序

```python
class Graph:
    def __init__(self, directed=True):
        self.nodes = {}       # name → GraphNode
        self.directed = directed

    def add_edge(self, from_name, to_name):
        from_node = self.add_node(from_name)
        to_node = self.add_node(to_name)
        from_node.edges.append(to_name)      # 出边
        to_node.in_edges.append(from_name)    # 入边

    def topological_sort(self):
        # 计算入度
        in_degree = {name: len(node.in_edges) 
                     for name, node in self.nodes.items()}
        # 入度为 0 的节点入队
        queue = deque([name for name, deg in in_degree.items() 
                       if deg == 0])
        result = []
        
        while queue:
            name = queue.popleft()
            result.append(name)
            # 减少邻居的入度
            for neighbor in self.nodes[name].edges:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # 检查是否有环
        if len(result) != len(self.nodes):
            return None  # 有环！
        return result
```

### BFS 和 DFS

```python
# BFS: 逐层探索，用于找最短路径（无权图）
def bfs(self, start):
    visited = set()
    queue = deque([start])
    result = []
    while queue:
        name = queue.popleft()
        if name not in visited:
            visited.add(name)
            result.append(name)
            queue.extend(self.nodes[name].edges)
    return result

# DFS: 一条路走到底再回溯
def dfs(self, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    result = [start]
    for neighbor in self.nodes[start].edges:
        if neighbor not in visited:
            result.extend(self.dfs(neighbor, visited))
    return result
```

**注意**：BFS 用了队列（s03），DFS 用了递归（内部用调用栈，s02）。前面学的数据结构在这里自然出现了。

---

## 6. 时间复杂度分析

| 操作 | 复杂度 | 原因 |
|------|--------|------|
| `add_node()` | O(1) | dict 插入 |
| `add_edge()` | O(1) | 追加到邻接表 |
| `topological_sort()` | O(V + E) | 每个节点和每条边各处理一次 |
| `has_cycle()` | O(V + E) | 基于拓扑排序 |
| `bfs(start)` | O(V + E) | 每个节点和每条边最多访问一次 |
| `dfs(start)` | O(V + E) | 同上 |

V = 节点数，E = 边数。对于 Agent Workflow，通常 V 和 E 都很小（几十到几百），这些操作几乎是瞬间的。

---

## 7. 小型项目实践

### Mini Agent Framework

打开 `mini_agent.py`——`AgentFramework` 类有 2 个 TODO 方法：

| 方法 | 你的任务 |
|------|---------|
| `validate()` | 检查 Workflow 是否合法（无环）→ `not self.graph.has_cycle()` |
| `get_execution_order()` | 返回拓扑排序后的执行顺序 → `self.graph.topological_sort()` |

这两个方法基本是 Graph 的一层薄封装——关键是理解「为什么 Agent Workflow 必须是无环图」。

### 你的任务

1. 读懂 `graph.py`（重点是拓扑排序的 Kahn 算法）
2. 打开 `mini_agent.py`，实现 2 个 TODO 方法
3. 扩展思考：如果要支持「条件分支」（如果 A 的结果是 X 则执行 B，否则执行 C），图结构需要怎么改？

---

## 8. 可视化运行过程

运行 `python s24_data_structures/s11_mini_agent/code.py`：

```
步骤 1: 图结构
  A: out=[B → C], in=[]
  B: out=[D], in=[A]
  C: out=[D], in=[A]
  D: out=[E], in=[B, C]    ← D 有两个输入！
  E: out=[], in=[D]

  拓扑排序: A → B → C → D → E
  BFS from A: ['A', 'B', 'C', 'D', 'E']

步骤 2: Agent Workflow
  RAG: start → fetch_docs → rank_docs → generate_answer → validate → end
  
步骤 3: 环检测
  合法 DAG? True
  添加循环边 validate → fetch_docs...
  合法 DAG? False — 检测到环！
```

---

## 9. 思考题

1. **为什么 Agent Workflow 必须是 DAG？** 如果允许环——A 执行完触发 B，B 执行完触发 A——会发生什么？在什么场景下这可能是有用的（迭代 agent）？

2. **BFS 和 DFS 在 Workflow 中分别有什么用？** BFS 适合找「离起点最近」的节点；DFS 适合找「最深的依赖链」。在 Agent 编排中各有什么应用？

3. **拓扑排序的结果是唯一的吗？** A 依赖 B，C 依赖 B，那么 B→A→C 和 B→C→A 都是合法的拓扑序——哪个更好？Workflow 引擎如何选择？

4. **图的表示除了邻接表还有邻接矩阵。** 什么场景下邻接矩阵更好？（提示：边很多 vs 边很少）

5. **打开 `mini_agent.py`**，实现 `get_execution_order()`。如果 Workflow 中有 100 个节点但只有 10 条边，拓扑排序的复杂度是多少？

---

## 10. 本章总结

| 概念 | 一句话 |
|------|--------|
| 图 | 节点 + 边——最通用的数据结构 |
| 邻接表 | 每个节点存它的出边列表 |
| DAG | 有向 + 无环——Workflow 的数学基础 |
| 拓扑排序 | 保证「依赖的先执行」的线性排列 |
| Kahn 算法 | 入度为 0 的节点入队，逐个消除 |
| 环检测 | 拓扑排序结果 < 节点总数 → 有环 |
| BFS / DFS | 逐层探索 / 深度优先——图遍历的两种策略 |

> **核心收获**：图是数据结构的「终极形态」——它解除了所有限制（树限制 parent 数，DAG 限制环）。AI Agent 的 Workflow 就是 DAG + 数据流。拓扑排序保证任务按依赖顺序执行——这比手动管理执行顺序可靠得多。从 s01 的链表到 s11 的图，你见证了数据结构如何通过「放宽限制」来表达更复杂的现实关系。

---

**上一章**: [s10: Mini Search Engine — 倒排索引](../s10_mini_search/)
**下一章**: [s12: 综合项目 — AI Agent 平台骨架](../s12_capstone/)
