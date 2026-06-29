# s01: Mini Git — 链表 + 哈希 + DAG

> *"版本控制不是魔法。它只是链表、哈希表和 DAG 的组合。"*
>
> **前提知识**: Python 基础（类、函数、列表操作）。不需要学过任何数据结构。

---

## 1. 本章工程问题

想象你在写一个项目。今天改了 `app.py`，明天可能要回到「上周五的版本」。你怎么管理？

**手动方案**：
```
项目_v1/
项目_v2/
项目_v2_备份/
项目_v3_最终版/
项目_v3_真的最终版/
```

这个方案的问题：
- 不知道 v2 和 v3 之间到底改了什么
- 6 个月后完全忘了哪个是哪个
- 两个人同时改？灾难

**工程需求**：我们需要一个系统，能：
1. **记录每一次修改**（什么时候、谁、改了什么）
2. **回到任意历史版本**
3. **同时开发两个功能互不干扰**（分支）
4. **把两条开发线合并到一起**

这就是 Git 做的事。而 Git 的底层，就是三个数据结构的组合。

---

## 2. 为什么普通方法不够好

如果你用 Python 的 list 来存 commit：

```python
commits = []  # 存储所有版本

def save_snapshot(files):
    commits.append(files)  # 每次保存整个项目
```

| 问题 | 为什么 list 不够 |
|------|-----------------|
| 怎么知道「上一个版本是谁」？ | list 有顺序但节点之间没有**显式的链接关系** |
| 怎么创建分支？ | list 是线性的——没法表示「从这里分叉出两条线」 |
| 怎么快速找到一个 commit？ | list 查找是 O(n)，你要遍历所有 commit |
| 合并分支时怎么记录？ | list 无法表示「一个节点有两个来源」 |

**你需要的不只是「存数据」，而是「存关系」。** 这就是数据结构的用武之地。

---

## 3. 数据结构是如何解决问题的

Git 用了三个数据结构来解决上面的问题：

```
问题                          数据结构           在 Git 中的角色
─────────────────────────────────────────────────────────────
commit 之间怎么链接？         单向链表            commit chain (parent 指针)
怎么快速定位一个 commit？     哈希表              object store (SHA-1 → commit)
分支合并怎么表示？             DAG                 commit 历史 (merge commit)
```

### 链表 → commit chain

每个 commit 记住「我的上一个版本是谁」（parent 指针）。这样就形成了一条链：

```
[init] → [commit A] → [commit B] → [commit C] (HEAD)
  ↑          ↑             ↑             ↑
parent     parent        parent        parent
 =None     =init         =commit A     =commit B
```

### 哈希表 → O(1) 对象定位

Git 给每个 commit 计算一个 SHA-1 哈希值作为「身份证号」。然后用哈希表存储：
```
"a1b2c3d..." → Commit 对象
"e4f5g6h..." → Commit 对象
```

查找任意 commit 只需要 O(1) 时间——不需要遍历整个链表。

### DAG → 分支合并历史

普通的 commit chain（链表）只有一条线。但 merge 操作需要「一个节点有两个 parent」：

```
main:    A → B → C ──→ M (merge commit, parent: C 和 E)
              ↘       ↗
feature:       D → E
```

DAG（有向无环图）允许一个节点有多个 parent，完美表示分支合并。

---

## 4. 数据结构原理

### 4.1 单向链表

```
链表:
┌───────┐    ┌───────┐    ┌───────┐
│ value │    │ value │    │ value │
│ A     │    │ B     │    │ C     │
│ next ─┼───→│ next ─┼───→│ next ─┼───→ None
└───────┘    └───────┘    └───────┘
  HEAD

和数组的区别:
  数组: [A][B][C]  — 连续内存, O(1) 随机访问, O(n) 插入(中间)
  链表: A→B→C     — 离散内存, O(n) 随机访问, O(1) 插入(已知位置)
```

**为什么 commit chain 用链表？** 因为版本控制的核心操作是「追加新版本到最后」——这正是链表的强项。而且现实中你只知道「过去」（parent），不知道「未来」（谁会在我后面建 commit），单向就够了。

### 4.2 哈希表

```
key ──→ [哈希函数] ──→ index ──→ bucket[index]

例如: hash("a1b2c3d") → 7 → bucket[7] = Commit 对象

冲突处理 (链地址法):
  bucket[7] → (key1, val1) → (key2, val2)  (两个 key 映射到了同一个 bucket)
```

**为什么 Git 用哈希？** 因为需要在几十万个 commit 中 O(1) 找到任意一个。没有哈希表，`git checkout <hash>` 每次都要遍历整个链表。

### 4.3 DAG（有向无环图）

```
DAG = 图的特化:
  - 有向: 边有方向（从子节点指向父节点）
  - 无环: 不存在 A→B→C→A 这样的循环

拓扑排序: DAG 中节点的一种线性排列，保证 parent 在 child 前面。
在 Git 里 = 「按时间从旧到新排列所有 commit」。
```

**为什么 commit 历史必须是 DAG？** 如果有环（A→B→C→A），那 A 既是自己的祖先又是自己的后代——这在时间上是不可能的。commit 的 parent 一定是「更早的」commit。

---

## 5. Python 从零实现

本章有三个实现文件，从底层到上层：

### 5.1 `linked_list.py` — 单向链表

```python
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None    # ← 这就是「链接」

class LinkedList:
    def __init__(self):
        self.head = None    # 链表的入口

    def append(self, value):
        """在尾部追加 — O(n)"""
        # 必须从头走到尾 → O(n)

    def prepend(self, value):
        """在头部插入 — O(1)"""
        # 新节点直接成为 head → O(1)

    def find(self, value):
        """按值查找 — O(n)"""
        # 从头遍历，一个一个找
```

**核心理解**：链表的每个节点只有「一根指针」，指向下一个。这决定了你只能**单向遍历**——从 head 开始，跟着 next 走到底。

### 5.2 `commit_chain.py` — Commit Chain

```python
class Commit:
    def __init__(self, hash_val, message, parent=None):
        self.hash = hash_val      # 唯一标识
        self.message = message    # "我做了什么"
        self.parent = parent      # ← 指向上一个 commit（形成链！）
        self.parents = [parent] if parent else []  # DAG 兼容

class CommitChain:
    def commit(self, message):
        """创建新 commit — O(1)"""
        # 新 commit 的 parent = 当前 HEAD
        # HEAD 移动到新 commit
```

**关键设计**：`parent` 字段让每个 commit 知道「我来自哪里」。`git log` 就是从这个 parent 链往回走。

### 5.3 `dag.py` — DAG

```python
class DAGNode:
    def __init__(self, name):
        self.parents = []    # 入边（我来自哪些节点）
        self.children = []   # 出边（哪些节点来自我）

class DAG:
    def topological_sort(self):
        """Kahn 算法 — O(V + E)"""
        # 1. 计算每个节点的入度
        # 2. 入度为 0 的节点入队（根节点）
        # 3. 每次出队一个节点，把它的 children 的入度减 1
        # 4. 如果某个 child 入度变成 0，入队
        # 5. 结果数量 < 节点总数 → 有环！
```

**核心思想**：拓扑排序 = 保证每个节点排在它的 parent 后面。这就是 `git log --topo-order` 做的事。

---

## 6. 时间复杂度分析

| 操作 | 链表 | 哈希表 | DAG |
|------|------|--------|-----|
| 插入 | O(1) 头部 / O(n) 尾部 | 平均 O(1) | O(1) 加节点 |
| 查找 | O(n) | 平均 O(1) | — |
| 遍历所有 | O(n) | O(n) | O(V + E) |
| 拓扑排序 | — | — | O(V + E) |
| 环检测 | — | — | O(V + E) |

**为什么这个组合是高效的？**
- commit（追加）：链表 O(1)
- checkout（定位）：哈希表 O(1)
- merge（合并）：DAG O(1) 加边 + 已有数据
- log（查看历史）：链表遍历 O(n)——这正是你要看的

---

## 7. 小型项目实践

### Mini Git 框架

打开 `mini_git.py`——框架已经搭好，5 个方法标记了 `TODO`：

| 方法 | 在时间树上的操作 | 使用的数据结构 |
|------|-----------------|---------------|
| `commit(message)` | 创建新节点，移动分支标签 | CommitChain + DAG |
| `log()` | 从当前分支往回遍历 | 链表遍历 |
| `branch(name)` | 在当前节点贴新标签 | dict (哈希表) |
| `checkout(name)` | 移动 HEAD 到另一个分支 | 指针赋值 |
| `merge(branch)` | 创建双 parent 节点 | DAG 加边 |

每个 TODO 都有具体提示——告诉你应该用哪个数据结构、第几步做什么。

### 你的任务

1. 读懂 `linked_list.py`、`commit_chain.py`、`dag.py` 三个文件
2. 打开 `mini_git.py`，按 TODO 提示实现 5 个方法
3. 运行 `code.py` 验证你的实现是否正确

---

## 8. 可视化运行过程

运行 `python s24_data_structures/s01_mini_git/code.py`，你会看到：

```
步骤 1: 链表基础
  [0] [HEAD] 'init: 项目启动'
       ↓
  [1] 'feat: 添加 main.py'
       ↓
  [2] 'fix: 修复登录 bug'

步骤 3: Commit Chain
  ● c0004 (HEAD)  添加功能 B
  ● c0003  修复 bug
  ● c0002  添加功能 A
  ● c0001  第一次提交

步骤 5: DAG 的 merge 结构
  ● A
    ● B ← [A]
      ● C ← [B]
        ● M ← [C,E]    ← merge commit！两个 parent
      ● D ← [B]
        ● E ← [D]

  拓扑排序: A → B → C → D → E → M
```

---

## 9. 思考题

1. **为什么 commit chain 是单向链表而不是双向链表？** 现实中的 commit 需要知道「下一个是谁」吗？如果改成双向链表，会带来什么问题？

2. **如果不用哈希表，怎么通过 hash 找到 commit？** 时间复杂度是多少？为什么 Git 不能用这个方法？

3. **DAG 的「无环」特性为什么对 Git 很重要？** 如果 commit 历史有环（A→B→C→A），`git log` 会发生什么？

4. **链表插入头部是 O(1)，尾部是 O(n)。Git 的 commit 是插在头部还是尾部？** 为什么这样设计？

5. **打开 `mini_git.py`**，实现 `commit()` 方法。你的实现中，`chain.head_commit` 指向的是最新的还是最旧的 commit？

---

## 10. 本章总结

| 概念 | 一句话 |
|------|--------|
| 链表 | 每个节点只知道「下一个是谁」，只能单向走 |
| Commit Chain | 链表特化——每个 commit 指向它的 parent |
| 哈希表 | key → hash → index，O(1) 定位 |
| DAG | 链表推广——一个节点可以有多个 parent，但不能有环 |
| 拓扑排序 | 从旧到新排列所有 commit |
| 三者关系 | 链表存顺序 → 哈希表做索引 → DAG 表示分支合并 |

> **核心收获**：Git 不是魔法。commit 历史 = 链表，对象查找 = 哈希表，分支合并 = DAG。三个简单的数据结构，组合起来就是世界上最流行的版本控制系统。

---

**下一章**: [s02: Mini Browser — 栈](../s02_mini_browser/) → 用两个栈实现浏览器的前进后退
