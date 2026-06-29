# s02: Mini Browser — 栈

> *"浏览器的后退按钮，就是栈的最直观应用。你每访问一个新页面，就像往一摞盘子上放一个新盘子。"*
>
> **前提知识**: 学过 s01（理解链表即可）。不需要其他数据结构基础。

---

## 1. 本章工程问题

打开浏览器，访问几个页面：

```
首页 → 搜索页 → 商品详情 → 购物车
```

现在点**后退**：

```
购物车 → 商品详情 → 搜索页 → 首页
```

然后点**前进**：

```
首页 → 搜索页 → 商品详情 → 购物车
```

**关键问题**：如果你在「搜索页」访问了一个新页面「新闻」，再点前进——应该去哪？

```
正确行为: 「前进」按钮变灰——旧的前进历史被清空了。
```

这不是一个简单的「记住所有访问过的页面」的问题。你需要：

1. 按**访问顺序的逆序**返回（后访问的先回去）
2. 支持「前进」回到刚才离开的页面
3. 「后退后访问新页面」要能**清空**旧的前进历史

---

## 2. 为什么普通方法不够好

### 方案 A：用 list 存所有历史

```python
history = ["首页", "搜索页", "商品详情", "购物车"]
current_index = 3  # 当前在"购物车"

def back():
    current_index -= 1
    return history[current_index]
```

**问题**：后退到「搜索页」后访问「新闻」——怎么处理？list 里「购物车」还在 `history[3]`，但实际上它应该被清掉。你需要额外逻辑管理「哪些是有效的」。

### 方案 B：只用 list，后退就删掉后面的

```python
history = ["首页", "搜索页", "商品详情", "购物车"]

def back():
    history.pop()  # 删掉"购物车"
    return history[-1]  # 回到"商品详情"
```

**问题**：「前进」功能怎么办？你把后面的页面删了，就没法前进了。

### 为什么这些方案都不对

根本原因是：**你需要同时维护「后退历史」和「前进历史」两条独立的序列**。list 是单序列，天然不适合这个「双序列」场景。

---

## 3. 数据结构是如何解决问题的

### 用两个栈

```
后退栈 (back_stack)          前进栈 (forward_stack)
┌────────────┐              ┌────────────┐
│ 购物车      │ ← TOP        │            │
│ 商品详情    │              │            │
│ 搜索页      │              │            │
│ 首页        │              │            │
└────────────┘              └────────────┘

当前页面: 购物车
```

### 后退操作

```
后退:
  1. 当前页面 "购物车" → push 到前进栈
  2. 从后退栈 pop → "商品详情" 成为新当前页面

后退栈                      前进栈
┌────────────┐              ┌────────────┐
│ 商品详情    │ ← TOP        │ 购物车      │ ← TOP
│ 搜索页      │              │            │
│ 首页        │              │            │
└────────────┘              └────────────┘

当前页面: 商品详情
```

### 前进操作

```
前进:
  1. 当前页面 "商品详情" → push 到后退栈
  2. 从前进栈 pop → "购物车" 成为新当前页面

后退栈                      前进栈
┌────────────┐              ┌────────────┐
│ 购物车      │ ← TOP        │            │
│ 商品详情    │              │            │
│ 搜索页      │              │            │
│ 首页        │              │            │
└────────────┘              └────────────┘

当前页面: 购物车
```

### 访问新页面（关键操作）

```
当前在「搜索页」，访问「新闻」:

  1. 当前页面 "搜索页" → push 到后退栈
  2. 清空前进栈！（为什么？因为旧的前进历史没意义了）
  3. 设置当前页面 = "新闻"

后退栈                      前进栈
┌────────────┐              ┌────────────┐
│ 搜索页      │ ← TOP        │ (空)        │
│ 首页        │              │            │
└────────────┘              └────────────┘

当前页面: 新闻
```

> 这就是栈的力量：两个栈的 push/pop 协作，完美模拟了浏览器的导航行为。特别是「清空前进栈」——只需要连续 pop 直到栈空，不需要管理复杂的索引。

---

## 4. 数据结构原理

### 栈（Stack）

栈是**只在一端操作**的受限数据结构。操作端叫「栈顶」。

```
操作:
  push(item)  — 压入栈顶
  pop()       — 弹出栈顶
  peek()      — 查看栈顶（不弹出）

特性: LIFO — Last In, First Out
```

```
push('A'):          push('B'):          pop() → 'B':
┌───┐              ┌───┐              ┌───┐
│ A │ ← TOP        │ B │ ← TOP        │ A │ ← TOP
└───┘              │ A │              └───┘
                   └───┘
```

### 为什么栈的操作都是 O(1)？

因为只在栈顶操作——不需要遍历、不需要移动其他元素。不管是基于数组还是链表实现，`push` 和 `pop` 都只需要一次操作。

### 栈 vs 链表

| | 栈 | 链表 |
|------|----|-----|
| 操作位置 | 只能栈顶 | 任意位置 |
| push/append | O(1) | O(1) 头部 / O(n) 尾部 |
| pop | O(1)（栈顶） | O(n)（需要找到前一个节点） |
| 访问中间元素 | ❌ 不支持 | O(n) |

> 栈的「限制」恰恰是它的「优势」：因为只能在一端操作，所以实现简单、操作极快、逻辑清晰。

---

## 5. Python 从零实现

打开 `stack.py`，核心代码：

```python
class Stack:
    def __init__(self):
        self._items = []    # 用 Python list 作为底层存储

    def push(self, item):
        """压入栈顶 — O(1)"""
        self._items.append(item)

    def pop(self):
        """弹出栈顶 — O(1)"""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()    # Python list 的 pop() 也是 O(1)

    def peek(self):
        """查看栈顶 — O(1)"""
        return self._items[-1]

    def is_empty(self):
        """判空 — O(1)"""
        return len(self._items) == 0
```

**为什么用 Python list 的尾部当栈顶？**
- `list.append()` 在尾部追加 → O(1)
- `list.pop()` 从尾部删除 → O(1)
- 如果用 list 头部（`list.insert(0)` / `list.pop(0)`）→ O(n)（因为要移动所有元素）

### 双栈浏览器核心逻辑

```python
class Browser:
    def __init__(self):
        self.back_stack = Stack()     # 后退栈
        self.forward_stack = Stack()  # 前进栈
        self.current_page = None

    def visit(self, url):
        """访问新页面"""
        if self.current_page:
            self.back_stack.push(self.current_page)
        # 关键：清空前进栈！
        while not self.forward_stack.is_empty():
            self.forward_stack.pop()
        self.current_page = url

    def back(self):
        """后退"""
        if self.back_stack.is_empty():
            return None
        self.forward_stack.push(self.current_page)
        self.current_page = self.back_stack.pop()
        return self.current_page

    def forward(self):
        """前进"""
        if self.forward_stack.is_empty():
            return None
        self.back_stack.push(self.current_page)
        self.current_page = self.forward_stack.pop()
        return self.current_page
```

---

## 6. 时间复杂度分析

| 操作 | 时间复杂度 | 原因 |
|------|-----------|------|
| `visit()` | O(n) | 清空前进栈需要逐个 pop（n = 前进栈大小） |
| `back()` | O(1) | push + pop 各一次 |
| `forward()` | O(1) | push + pop 各一次 |
| `can_go_back()` | O(1) | is_empty() |
| `can_go_forward()` | O(1) | is_empty() |

> 注意：`visit()` 中清空前进栈是 O(n)，但 n 通常是几十个页面——完全可以接受。

---

## 7. 小型项目实践

### Mini Browser 框架

打开 `mini_browser.py`——`Browser` 类有三个 TODO 方法：

| 方法 | 你的任务 |
|------|---------|
| `visit(url)` | 当前页面入后退栈 + 清空前进栈 + 设置新页面 |
| `back()` | 当前页面入前进栈 + 从后退栈 pop |
| `forward()` | 当前页面入后退栈 + 从前进栈 pop |

每个 TODO 都有伪代码提示。`DemoBrowser` 类提供了完整实现供参考——但建议你先自己写，遇到困难再看。

### 你的任务

1. 读懂 `stack.py`（不到 50 行核心代码）
2. 打开 `mini_browser.py`，实现 3 个 TODO 方法
3. 运行 `code.py` 验证——观察每一步两个栈的变化

---

## 8. 可视化运行过程

运行 `python s24_data_structures/s02_mini_browser/code.py`，你会看到：

```
步骤 1: 栈的基本操作
  ┌──────┐
  │ D    │ ← TOP
  │ C    │
  │ B    │
  │ A    │
  └──────┘
  pop → 'D' → 'C' → 'B' → 'A' (LIFO: 后进先出)

步骤 2-6: 双栈浏览器导航
  访问: google → github → stackoverflow
  后退: stackoverflow → github
  前进: github → stackoverflow
  后退后访问新页面 → 前进栈被清空！(关键行为)
```

---

## 9. 思考题

1. **为什么 `visit()` 要清空前进栈？** 不清空会怎样？想一想「后退到搜索页 → 访问新闻 → 点前进」应该发生什么。

2. **如果用户连续后退 100 次，后退栈还能撑住吗？** 内存会爆吗？为什么真实浏览器会限制后退步数（通常 50 步）？

3. **递归函数和栈有什么关系？** 写一个递归的 `factorial(1000)`，观察报错信息——为什么 Python 限制了递归深度？和栈有什么关系？

4. **栈和 s01 的链表有什么区别？** 如果让你用链表来实现栈，push 和 pop 应该在链表的头部还是尾部？为什么？

5. **打开 `mini_browser.py`**，实现 `back()` 方法。如果你的实现中 `back()` 和 `forward()` 代码完全对称（只是 push/pop 的目标栈对调），说明你理解对了。

---

## 10. 本章总结

| 概念 | 一句话 |
|------|--------|
| 栈 | 只能在一端（栈顶）操作的受限数据结构 |
| LIFO | Last In, First Out — 后进先出 |
| push/pop | 压入栈顶 / 弹出栈顶 — 都是 O(1) |
| 双栈模式 | 后退栈 + 前进栈 = 完整的浏览器导航 |
| `visit()` 清空前进栈 | 「后退后走新路，旧的前进方向没意义了」 |
| 真实应用 | 浏览器导航、函数调用栈、撤销(Ctrl+Z)、DFS |

> **核心收获**：栈的「限制」（只能操作栈顶）恰好匹配浏览器的导航模型——你只能回到「上一个」页面。两个栈协作，就让「后退/前进」变得自然。数据结构的价值不在于它多强大，而在于它**恰好匹配**真实问题的约束条件。

---

**上一章**: [s01: Mini Git — 链表 + 哈希 + DAG](../s01_mini_git/)
**下一章**: [s03: Mini Message Queue — 队列](../s03_mini_mq/) → LIFO 的反面：FIFO
