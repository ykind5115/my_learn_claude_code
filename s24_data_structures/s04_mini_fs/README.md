# s04: Mini File System — 树

> *"Linux 的目录结构不是平坦的列表，而是一棵倒置的树。根在上，枝叶在下。"*
>
> **前提知识**: 学过 s01（链表）。树是链表从「一对一」到「一对多」的推广。

---

## 1. 本章工程问题

打开你的电脑，文件系统长这样：

```
/
├── home/
│   └── user/
│       ├── documents/
│       │   └── resume.pdf
│       └── Downloads/
│           └── ubuntu.iso
├── etc/
│   └── nginx.conf
└── tmp/
```

**你需要做的操作**：
- `cd /home/user/documents` — 从根目录找到深层目录
- `ls` — 列出当前目录下有什么
- `mkdir new_folder` — 创建新目录
- `rm -rf /home/user/Downloads` — 删除目录（先删里面的文件，再删空目录）

**核心问题**：文件和目录之间是**层级关系**——不是平坦的 list 能表示的。你需要一种能表达「一对多」的数据结构。

---

## 2. 为什么普通方法不够好

### 如果用 list 存所有文件路径

```python
files = [
    "/home/user/documents/resume.pdf",
    "/home/user/Downloads/ubuntu.iso",
    "/etc/nginx.conf",
]
```

| 操作 | list 的做法 | 问题 |
|------|-----------|------|
| 列出 `/home/user/` 下的文件 | 遍历所有路径，找前缀匹配的 | O(n)，n = 所有文件数 |
| 创建目录 | `files.append(new_path)` | 无法表达「目录是目录」——和文件混在一起 |
| 删除目录（含子内容） | 找到所有前缀匹配的，逐个删除 | O(n)，且「找到所有子内容」很麻烦 |
| 从 `/` 找到深层文件 | 遍历 | 没有「路径导航」的概念 |

**根本问题**：list 是线性的——所有文件平铺在一起。但文件系统是**层级**的——目录套目录。你需要一个能表达「父子关系」的结构。

---

## 3. 数据结构是如何解决问题的

### 树 = 一对多层级结构

```
          [/]              ← 根节点 (root)
         / | \
      [home] [etc] [tmp]   ← 内部节点
       /
    [user]                 ← 内部节点
     /    \
[docs]  [downloads]        ← 内部节点
  |          |
resume.pdf  ubuntu.iso     ← 叶子节点 (文件)
```

每个节点：
- 一个 **parent**（父节点是谁）——根节点除外
- 多个 **children**（子节点有哪些）——叶子节点除外
- 一个 **name**（自己叫什么）

### 路径导航 = 从根开始沿树遍历

```
cd /home/user/documents

过程:
  1. 从根 "/" 开始
  2. 在 "/" 的 children 中找 "home" → 找到
  3. 在 "home" 的 children 中找 "user" → 找到
  4. 在 "user" 的 children 中找 "documents" → 找到
  5. 切换到 "documents"

每一步 = O(branching_factor)，总复杂度 = O(depth × branching_factor)
```

> 和链表一样，这是「沿着指针走」——区别是链表只有一条路，树在每个节点有**多条分叉路**。

### 三种遍历 = 三种使用场景

```
前序遍历 (preorder):  先访问父节点，再访问子节点
  → 复制目录树: 先建父目录，再往里面放文件

后序遍历 (postorder): 先访问子节点，再访问父节点
  → 删除目录树: 先删子内容，再删空目录

层序遍历 (levelorder): 从上到下逐层访问
  → ls -R: 按层级展示
```

---

## 4. 数据结构原理

### 树的核心概念

```
节点 (Node):
  - name: 节点名
  - parent: 指向父节点的引用 (根节点为 None)
  - children: 子节点列表

树 (Tree):
  - root: 根节点 (唯一的没有 parent 的节点)

和链表的对比:
  链表:  Node { value, next }           — 每个节点 1 个出口
  二叉树: Node { value, left, right }   — 每个节点 2 个出口
  树:    Node { value, children[] }     — 每个节点 N 个出口
```

### 树的几种特殊形式

| 类型 | 约束 | 例子 |
|------|------|------|
| 链表 | 每个节点最多 1 个 child | commit chain |
| 二叉树 | 每个节点最多 2 个 child | BST, 堆 |
| N 叉树 | 每个节点任意个 child | 文件系统, DOM |
| B 树/B+ 树 | 节点有多 key + 平衡 | 数据库索引（s09） |

> 树是一个**家族**，每种变体解决不同的问题。s04 的通用树是基础，s09 的 B+ 树是高级变体。

---

## 5. Python 从零实现

打开 `tree.py`，核心代码：

### TreeNode

```python
class TreeNode:
    def __init__(self, name, data=None):
        self.name = name
        self.parent = None     # ← 指向父节点（树和链表的本质区别）
        self.children = []     # ← 可以有多个子节点

    def add_child(self, child_node):
        child_node.parent = self
        self.children.append(child_node)

    def path(self):
        """从根到当前节点的完整路径"""
        parts = []
        node = self
        while node:
            parts.append(node.name)
            node = node.parent    # 向上走到根
        return "/" + "/".join(reversed(parts))
```

### 三种遍历

```python
# 前序: 先父后子 → 用于创建
def traverse_preorder(self, node):
    yield node
    for child in node.children:
        yield from self.traverse_preorder(child)

# 后序: 先子后父 → 用于删除
def traverse_postorder(self, node):
    for child in node.children:
        yield from self.traverse_postorder(child)
    yield node

# 层序: 逐层 → 用于展示
def traverse_levelorder(self):
    queue = deque([self.root])
    while queue:
        node = queue.popleft()
        yield node
        for child in node.children:
            queue.append(child)   # ← 用到了 s03 的队列！
```

**注意**：层序遍历用到了队列（s03！）——这体现了数据结构的组合使用。

---

## 6. 时间复杂度分析

| 操作 | 复杂度 | 原因 |
|------|--------|------|
| `find_by_path("/a/b/c")` | O(depth × avg_branching) | 每层在 children 列表中线性查找 |
| `add_node(parent, name)` | O(1) | 追加到 children 列表 |
| `traverse_preorder()` | O(n) | 每个节点访问一次 |
| `traverse_postorder()` | O(n) | 每个节点访问一次 |
| `traverse_levelorder()` | O(n) | 每个节点访问一次 + 队列操作 O(1) 每节点 |

> 路径查找是 O(depth × branching)，在真实文件系统中，depth 通常不超过 20，branching 通常不超过几百——所以实际上很快。

---

## 7. 小型项目实践

### Mini File System 框架

打开 `mini_fs.py`——`FileSystem` 类有 5 个 TODO 方法：

| 方法 | 你的任务 | 树的对应操作 |
|------|---------|------------|
| `mkdir(name)` | 在当前目录下创建子节点 | `tree.add_node(current_dir, name)` |
| `touch(name, content)` | 创建文件节点 + 存储内容 | 同上 + 存入 `_files` dict |
| `cd(path)` | 沿树移动到目标节点 | 支持 `".."`（parent）、绝对路径、相对路径 |
| `ls()` | 列出当前目录的 children | 遍历 `current_dir.children` |
| `pwd()` | 返回完整路径 | `current_dir.path()` — 已实现 |

### 你的任务

1. 读懂 `tree.py`（重点是 TreeNode 和三种遍历）
2. 打开 `mini_fs.py`，实现 5 个 TODO 方法
3. 思考：真实的 Linux 文件系统不只一棵树——硬链接（hard link）让一个文件可以有多个「名字」。这让文件系统变成了什么数据结构？（提示：s01 的 DAG）

---

## 8. 可视化运行过程

运行 `python s24_data_structures/s04_mini_fs/code.py`：

```
步骤 1: 树的遍历
  目录树:
  /
  │   ├── home
  │       ├── user
  │       │   ├── docs (file)
  │           ├── pics (file)
      ├── etc (file)

  前序 (创建): ['/', 'home', 'user', 'docs', 'pics', 'etc']
  后序 (删除): ['docs', 'pics', 'user', 'home', 'etc', '/']
  层序 (BFS):  ['/', 'home', 'etc', 'user', 'docs', 'pics']

步骤 2: Mini FS 操作
  mkdir: ///home
  cd: ///home
  mkdir: ///home/user
  touch: ///home/user/README.md
  ls: user/
      README.md
      config.txt
```

---

## 9. 思考题

1. **为什么后序遍历适合删除目录树？** 如果前序遍历去删除——先删父目录再删子文件——会发生什么？

2. **树的深度和广度对性能有什么影响？** 极端情况：所有文件放在一个目录下（广度大深度小）vs 每层只有一个目录（深度大广度小）。哪种对 `find_by_path` 更友好？

3. **如果让你实现 `tree` 命令的 `--level` 选项**（只显示前 N 层），用哪种遍历最合适？为什么？

4. **链表、树、DAG、图的关系**：限制逐步放宽——链表（1 child）→ 树（多 children, 1 parent）→ DAG（多 children, 多 parent, 无环）→ 图（多 children, 多 parent, 可以有环）。这个演变过程中，哪个操作变得最复杂？

5. **打开 `mini_fs.py`**，实现 `cd("..")` ——回到上级目录。如果已经在根目录，`cd("..")` 应该做什么？

---

## 10. 本章总结

| 概念 | 一句话 |
|------|--------|
| 树 | 一对多的层级结构——每个节点有 N 个 children, 1 个 parent |
| 根节点 | 唯一没有 parent 的节点 |
| 叶子节点 | 没有 children 的节点（文件） |
| 路径 | 从根开始，沿 children 引用走到目标 |
| 前序遍历 | 先父后子 → 创建 |
| 后序遍历 | 先子后父 → 删除 |
| 层序遍历 | 逐层 → 展示（需要队列） |

> **核心收获**：文件系统、HTML DOM、公司组织架构——世界上充满了层级关系。树就是用来表达「整体由部分组成、部分还可以细分」的数据结构。从链表的「一对一」到树的「一对多」，你多了一个维度。

---

**上一章**: [s03: Mini Message Queue — 队列](../s03_mini_mq/)
**下一章**: [s05: Mini Redis — 哈希表](../s05_mini_redis/)
