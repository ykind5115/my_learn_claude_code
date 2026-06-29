# s03: Mini Message Queue — 队列

> *"栈是后进先出，队列是先进先出。一个像一摞盘子，一个像排队买咖啡。"*
>
> **前提知识**: 学过 s02（理解栈和 LIFO）。队列就是栈的「反义词」——FIFO。

---

## 1. 本章工程问题

想象你运营一个电商网站。用户下单后，系统需要：

1. 扣减库存
2. 生成订单
3. 发送确认邮件
4. 通知仓库发货

如果这些操作串行执行，用户要等 5 秒才能看到「下单成功」。更好的方式是：**把任务放进一个队列，后台慢慢处理**。

```
用户下单 → [订单队列] → 库存服务取走处理
                       → 邮件服务取走处理
                       → 仓库服务取走处理
```

**核心需求**：
1. **先来的订单先处理**（不能插队）
2. **生产者和消费者解耦**（下单的不需要知道谁在处理）
3. **消费者慢时消息排队等待**（不会丢失）

这就是消息队列。而消息队列的底层数据结构——就是队列（Queue）。

---

## 2. 为什么普通方法不够好

### 如果用一个 list 当队列

```python
queue = []

# 入队（生产者）
queue.append("订单1")  # O(1)
queue.append("订单2")

# 出队（消费者）
first = queue.pop(0)   # O(n)！因为要移动所有剩余元素
```

`list.pop(0)` 是 O(n)——每次出队要移动整个 list。每秒处理 1000 个订单 = 1000 次 O(n) 操作 = 灾难。

### 如果用栈代替队列

栈是 LIFO——后进的订单先处理。这意味着：
- 最后一个下单的客户最先收到货
- 第一个下单的客户永远等不到

> 栈和队列的核心区别：**公平性**。栈不公平（后来居上），队列公平（先来后到）。

---

## 3. 数据结构是如何解决问题的

### 队列（Queue）= FIFO

```
入队 (enqueue): 加到队尾
出队 (dequeue): 从队头取出

  队头                 队尾
  ┌────┬────┬────┬────┐
  │ A  │ B  │ C  │ D  │
  └────┴────┴────┴────┘
    ↑               ↑
  dequeue         enqueue
   (取出A)         (加入E)
```

### 消息队列 = 队列 + 主题（Topic）

真实的消息队列（RabbitMQ、Kafka）给每个主题分配一个队列：

```
Topic: "orders"       →  Queue(["订单1", "订单2", ...])
Topic: "emails"       →  Queue(["欢迎邮件", "重置密码", ...])
Topic: "notifications" →  Queue(["新消息", ...])
```

生产者往某个 Topic 发消息，消费者从某个 Topic 取消息——互不干扰。

### 循环队列：固定大小的数组队列

当你不希望队列无限增长时（比如嵌入式系统内存有限），用循环队列：

```
数组: [A][B][ ][ ][ ]
       ↑  ↑
      head tail

dequeue → A 被取出, head 前移:
      [ ][B][ ][ ][ ]
          ↑  ↑
         head tail

enqueue(C):
      [ ][B][C][ ][ ]
          ↑     ↑
         head  tail

tail 到了数组末尾 → 绕回开头:
      [D][B][C][ ][ ]
       ↑        ↑
      tail     head
```

> head 和 tail 在数组上循环移动，空间重复利用。就像时钟——指针走到 12 后回到 1。

---

## 4. 数据结构原理

### 队列的核心操作

| 操作 | 含义 | 时间复杂度 |
|------|------|-----------|
| `enqueue(item)` | 元素加到队尾 | O(1) |
| `dequeue()` | 取出队头元素 | O(1) |
| `peek()` | 查看队头（不取出） | O(1) |
| `is_empty()` | 判断队列是否为空 | O(1) |

### 为什么用 `deque` 而不是 `list`？

Python 的 `collections.deque` 是双向链表实现——头部和尾部操作都是 O(1)。而 `list.pop(0)` 是 O(n)。

```python
from collections import deque

# deque 的做法: 双向链表, 头尾操作都 O(1)
q = deque()
q.append("A")        # O(1) 尾部
q.popleft()          # O(1) 头部 ← 关键！

# list 的做法: 
lst = ["A"]
lst.pop(0)           # O(n) — 不推荐！
```

### 队列 vs 栈

| | 栈（Stack） | 队列（Queue） |
|------|-----------|-------------|
| 原则 | LIFO（后进先出） | FIFO（先进先出） |
| 类比 | 一摞盘子 | 排队买咖啡 |
| 插入 | push（压入栈顶） | enqueue（加入队尾） |
| 删除 | pop（弹出栈顶） | dequeue（取出队头） |
| 适用场景 | 撤销、后退、递归 | 消息系统、任务调度、BFS |

---

## 5. Python 从零实现

打开 `queue.py`，核心代码：

### 基础队列（基于 deque）

```python
from collections import deque

class Queue:
    def __init__(self):
        self._items = deque()

    def enqueue(self, item):
        """入队 — O(1)"""
        self._items.append(item)

    def dequeue(self):
        """出队 — O(1)"""
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self._items.popleft()  # ← 关键：从头部取，O(1)

    def peek(self):
        """查看队头 — O(1)"""
        return self._items[0]
```

### 循环队列

```python
class CircularQueue:
    def __init__(self, capacity=8):
        self._data = [None] * capacity
        self._head = 0   # 队头位置
        self._tail = 0   # 下一个入队位置
        self._size = 0

    def enqueue(self, item):
        if self._size == self._capacity:
            raise OverflowError("队列已满")
        self._data[self._tail] = item
        self._tail = (self._tail + 1) % self._capacity  # ← 循环
        self._size += 1

    def dequeue(self):
        item = self._data[self._head]
        self._head = (self._head + 1) % self._capacity   # ← 循环
        self._size -= 1
        return item
```

**`% self._capacity` 就是循环的关键**——当指针走到数组末尾，自动绕回开头。

---

## 6. 时间复杂度分析

| 操作 | 基础队列（deque） | 循环队列 | list（不推荐） |
|------|-----------------|---------|--------------|
| enqueue | O(1) | O(1) | O(1) |
| dequeue | O(1) | O(1) | **O(n)** |
| peek | O(1) | O(1) | O(1) |
| 空间 | O(n) 动态 | O(capacity) 固定 | O(n) 动态 |

> 核心区别就在 dequeue——队列必须保证头部删除是 O(1)，否则失去了意义。

---

## 7. 小型项目实践

### Mini Message Queue 框架

打开 `mini_mq.py`——`MessageQueue` 类有两个 TODO 方法：

| 方法 | 你的任务 |
|------|---------|
| `publish(topic, body)` | 创建 Message → 找到 topic 的队列 → enqueue |
| `consume(topic)` | 从 topic 的队列 dequeue → 返回 Message |

关键设计：
- 每个 topic 一个独立的 Queue（topic → Queue 用 dict 映射）
- 消费失败的消息可以重试（`retry()` 方法已实现）
- 重试次数用完的消息进入死信队列

### 你的任务

1. 读懂 `queue.py`（两个实现加起来不到 60 行）
2. 打开 `mini_mq.py`，实现 2 个 TODO 方法
3. 思考扩展：如果想让消息有优先级（VIP 用户的消息先处理），该怎么改？

---

## 8. 可视化运行过程

运行 `python s24_data_structures/s03_mini_mq/code.py`：

```
步骤 1: 队列基础
  队头 → A | B | C | D → 队尾
  dequeue → 'A' → 'B' → 'C' → 'D' (FIFO: 先进先出)

步骤 2: 循环队列
  入队 4 个任务，队列满了
  dequeue → '任务0' — 腾出空间
  现在可以入队了——循环利用数组空间

步骤 3: Mini Message Queue
  发布: Msg(1, topic=orders, body='用户 #42 下单了')
  发布: Msg(2, topic=orders, body='用户 #99 下单了')
  
  消息队列状态:
    [orders] 2 条消息待处理
    [notifications] 1 条消息待处理
    
  消费: 订单1 被处理
  消费: 订单2 被处理
```

---

## 9. 思考题

1. **对比 s02 的栈和本章的队列**：浏览器导航用栈，消息系统用队列。为什么不能反过来？如果用队列做浏览器导航会发生什么？

2. **循环队列满的时候怎么办？** 是让生产者等待（阻塞队列）还是丢弃旧消息（有界队列）？不同的业务场景选哪个？

3. **如果消费者处理速度永远跟不上生产者怎么办？** 队列会无限增长吗？Kafka 的解决方案是什么？（提示：磁盘 + 分片）

4. **如何实现一个「优先队列」？** VIP 用户的消息应该先处理，但普通用户的消息不能永远等着。你有什么思路？

5. **打开 `mini_mq.py`**，实现 `publish()` 方法。你的实现中，如果 topic 不存在，是自动创建还是报错？两种选择各有什么优缺点？

---

## 10. 本章总结

| 概念 | 一句话 |
|------|--------|
| 队列 | FIFO — 先进先出，公平的数据结构 |
| enqueue / dequeue | 加到队尾 / 从队头取出 — 都是 O(1) |
| deque vs list | deque 头部操作 O(1)，list 头部操作 O(n) |
| 循环队列 | 固定大小数组 + head/tail 指针循环移动 |
| 消息队列 | 队列 + Topic + 解耦生产者消费者 |
| 队列 vs 栈 | LIFO（不公平）vs FIFO（公平） |

> **核心收获**：队列的「公平性」（先来后到）完美匹配消息系统、任务调度等场景。如果栈是「后来居上」，那队列就是「先到先得」。选择 LIFO 还是 FIFO，取决于你的业务需要公平还是需要效率。

---

**上一章**: [s02: Mini Browser — 栈](../s02_mini_browser/)
**下一章**: [s04: Mini File System — 树](../s04_mini_fs/)
