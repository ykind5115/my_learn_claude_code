# s09: Mini DB Index — B+ 树

> *"B+ 树没有发明新的算法。它只是把节点变大了——大到一次磁盘 IO 能读几百个 key。树矮了，IO 少了，查询就快了。"*
>
> **前提知识**: 学过 s04（树）和 s07（跳表）。理解 s08（内存 vs 磁盘的 IO 成本）。

---

## 1. 本章工程问题

你在做一个数据库。用户表有 1 亿行数据：

```sql
SELECT * FROM users WHERE age = 25;
```

没有索引：数据库扫描全部 1 亿行 → 几分钟。
有索引：数据库查 B+ 树索引 → 几毫秒。

**B+ 树是数据库索引的标准答案**——MySQL、PostgreSQL、SQLite 全部用它。为什么不是跳表？为什么不是二叉树？答案就在 s08——**磁盘 IO 的成本**。

---

## 2. B+ 树和普通树的区别

### 二叉树（每个节点 1 个 key）

```
        [50]
       /    \
    [30]    [70]
   /    \  /    \
 [10] [40] [60] [90]

深度 = log₂(n)，每个节点存 1 个 key。
1 亿行 → 深度 ≈ 27 层 → 27 次 IO → 270ms
```

### B+ 树（每个节点 500 个 key）

```
         [100, 200, 300, 400, 500]        ← 内部节点（只存索引）
        /    |    |    |    |    \
   叶子节点（存数据 + 链表）

深度 = log₅₀₀(n)，每个节点存 500 个 key。
1 亿行 → 深度 ≈ 3 层 → 3 次 IO → 30ms
```

**差距：27 次 IO vs 3 次 IO。270ms vs 30ms。**

---

## 3. B+ 树的设计特点

### 特点 1：所有数据在叶子节点

```
内部节点:         [50, 100]
                 /    |     \
                /     |      \
叶子节点:  [10,20,30] [50,60,70] [100,150,200]
             ↓ 数据      ↓ 数据       ↓ 数据
          实际的行    实际的行     实际的行
```

内部节点只存 key + 子节点指针。叶子节点存 key + 实际数据。这样内部节点可以很「轻」——一个节点存几百个 key。

### 特点 2：叶子节点之间有链表

```
叶子: [10,20,30] → [50,60,70] → [100,150,200] → ...
        ↑              ↑               ↑
      next_leaf      next_leaf       next_leaf
```

**这是 B+ 树独有的优势**：范围查询不需要回到内部节点。顺着叶子链表一直走就行。

```sql
SELECT * FROM users WHERE age BETWEEN 25 AND 35;
-- 1. 定位到 age=25 的叶子
-- 2. 顺着 next_leaf 走到 age>35 → O(log n + k)!
```

### 特点 3：分裂保持平衡

当节点满了（key 数 > order - 1），把节点一分为二。

```
插入前: [10, 20, 30, 40]  ← order=5, 最多 4 个 key
插入 25:
  1. [10, 20, 25, 30, 40] → 超过限制了！
  2. 分裂: [10, 20, 25] 和 [30, 40]
  3. 把 30 提升到父节点
```

这个过程和跳表的「概率平衡」不同——B+ 树通过**分裂保证绝对平衡**。

---

## 4. 关键操作详解

### 查找

```
search(25) 在:
         [30, 70]
        /    |    \
  [10,20] [30,50] [70,90]

1. 在根节点 [30,70] 中: 25 < 30 → 走最左边的子节点
2. 在 [10,20] 中: 25 > 20 → 但 25 < 下一个分隔 key → 在 [10,20] 末尾
3. 等等...实际定位逻辑: 25 < 30 所以走 children[0]
4. 在叶子 [10,20] 中找 25 → 不存在 → None

search(50):
1. 根节点 [30,70]: 30 ≤ 50 < 70 → 走 children[1]（30 和 70 之间的子节点）
2. 在叶子 [30,50] 中找到 50 → 返回
```

### 范围查询

```
range_query(25, 65):

1. 定位到包含 25 的叶子节点 → [10,20]（不对，25 不在这里）
   重新定位: 25 ≥ 20, 但 < 30... 实际上 25 不在树中
   范围查询会找到第一个 ≥ 25 的叶子节点 → [30,50]

2. 在 [30,50] 中: 30, 50 都 ≤ 65 → 全部收集
3. 沿着 next_leaf → [70,90]: 70 > 65 → 停止

结果: [30, 50]
```

---

## 5. Python 从零实现

打开 `bplus_tree.py`，核心结构：

```python
class BPlusNode:
    def __init__(self, is_leaf=False):
        self.keys = []        # 有序 key 列表
        self.children = []    # 子节点指针（内部节点用）
        self.values = []      # 实际数据（叶子节点用）
        self.next_leaf = None # 叶子链表（范围查询的关键！）
        self.is_leaf = is_leaf

class BPlusTree:
    def __init__(self, order=4):
        self.order = order    # 每个节点最多 order-1 个 key
        self.root = BPlusNode(is_leaf=True)

    def search(self, key):
        node = self.root
        while not node.is_leaf:
            # 在内部节点找去哪个子节点
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        # 在叶子节点中查找
        for i, k in enumerate(node.keys):
            if k == key:
                return node.values[i]
        return None
```

### 分裂根节点

```python
def _split_root(self):
    old_root = self.root
    mid = len(old_root.keys) // 2

    left = BPlusNode(is_leaf=old_root.is_leaf)
    right = BPlusNode(is_leaf=old_root.is_leaf)
    left.keys = old_root.keys[:mid]
    right.keys = old_root.keys[mid:]

    if old_root.is_leaf:
        left.values = old_root.values[:mid]
        right.values = old_root.values[mid:]
        left.next_leaf = right  # ← 维护叶子链表！

    new_root = BPlusNode(is_leaf=False)
    new_root.keys = [right.keys[0]]  # 提升中间 key
    new_root.children = [left, right]
    self.root = new_root
```

---

## 6. 时间复杂度分析

| 操作 | B+ 树 | 二叉树 | 跳表（磁盘） |
|------|-------|--------|------------|
| 精确查找 | O(log n) ≈ 3 次 IO | O(log n) ≈ 27 次 IO | O(log n) ≈ 30 次 IO |
| 范围查询 | O(log n + k) 叶子链表 | O(log n + k) 中序遍历 | O(log n + k) |
| 插入 | O(log n) | O(log n) | O(log n) |
| 删除 | O(log n) | O(log n) | O(log n) |

**B+ 树的 O(log n) 底数是 order（~500），二叉树的底数是 2。** 同样的 n，B+ 树的深度小得多。

### 空间分析

- 每个内部节点：存几百个 key + 几百个子指针 → 刚好填满一个磁盘 block（4KB~16KB）
- 空间利用率通常 > 50%（分裂保证一半满）

---

## 7. 小型项目实践

### Mini DB Index 框架

打开 `mini_db_index.py`——`DBIndex` 类有 3 个 TODO 方法：

| 方法 | 你的任务 |
|------|---------|
| `insert(key, row_id)` | 在 B+ 树中插入索引条目 |
| `search(key)` | 精确查找 → 返回匹配的 row_id 列表 |
| `range_query(lo, hi)` | 范围查询 → 返回范围内的所有 (key, row_id) |

### 你的任务

1. 读懂 `bplus_tree.py`（重点是 `search` 的导航逻辑和 `_split_root` 的分裂逻辑）
2. 打开 `mini_db_index.py`，实现 3 个 TODO 方法（每个方法基本上只需要一行代码——调用 BPlusTree 的对应方法）
3. 思考：如果同一个 age 值对应多个 user（比如 age=25 有 3 个人），B+ 树的 value 应该存什么？

---

## 8. 可视化运行过程

运行 `python s24_data_structures/s09_mini_db_index/code.py`：

```
步骤 1: B+ 树结构
  Lv0:       [50]
  Lv1:     [10,20,25,30,35,40,45]  [50,55,60,65,70,75,80,90] (叶子)

  search(60) = 'data-60'
  range_query[30, 60] = [(30, data-30), ..., (60, data-60)]  ← 只用叶子链表！

步骤 2: Mini DB Index
  age=25 的用户: user_id=[1, 3]
  age 在 [25,30]: [(25,3), (28,5), (30,2)]
```

---

## 9. 思考题

1. **B 树和 B+ 树有什么区别？** B 树在内部节点也存数据，B+ 树只在叶子存。这对范围查询有什么影响？为什么不直接在内部节点也存数据？

2. **为什么 B+ 树的 order 通常设得很大（100~500）？** 如果 order=4（像本章演示），1 亿条数据需要多少层？和 order=500 差了多少倍 IO？

3. **B+ 树在内存中比跳表慢还是快？** 如果数据全在内存里，你会选 B+ 树还是跳表？为什么数据库在内存模式下也用 B+ 树（如 MySQL InnoDB buffer pool）？

4. **叶子节点的链表是单向的。** 反向范围查询（`ORDER BY age DESC`）怎么办？需要双向链表吗？

5. **打开 `mini_db_index.py`**，实现 `range_query()`。如果数据库表有 100 万行，`WHERE age BETWEEN 20 AND 25` 正好匹配 3 行，B+ 树需要多少次 IO？

---

## 10. 本章总结

| 概念 | 一句话 |
|------|--------|
| B+ 树 | 多路平衡搜索树——每个节点存几百个 key |
| Order | 最大子节点数——决定树的「宽度」 |
| 内部节点 vs 叶子节点 | 内部只存索引（轻），叶子存数据 + 链表 |
| 叶子链表 | 范围查询不需要回溯内部节点 |
| 分裂 | 节点满时一分为二，保持绝对平衡 |
| 为什么磁盘友好 | 宽节点 = 矮树 = 少 IO |

> **核心收获**：B+ 树没有发明新的算法——它只是根据「数据在磁盘上」这个约束，重新设计了节点的结构。把节点变大，树就变矮，IO 就减少。这是「数据结构适配环境」的经典案例。

---

**上一章**: [s08: 内存 vs 磁盘 — ★ 过渡章](../s08_memory_vs_disk/)
**下一章**: [s10: Mini Search Engine — 倒排索引](../s10_mini_search/)
