# s05: Mini Redis — 哈希表

> *"如果链表是走楼梯（一层一层），哈希表就是坐电梯（直达目标楼层）。代价是你不知道每层楼里有什么。"*
>
> **前提知识**: 学过 s01（链表查找 O(n)）。理解 Python dict 的基本用法。

---

## 1. 本章工程问题

你正在写一个用户系统。需要根据用户名快速查到用户信息：

```python
# 需求: 给定 username，返回 user info
users = [...]
def get_user(username):
    for user in users:       # ← 遍历所有用户
        if user.name == username:
            return user
    return None
```

100 个用户？还行。100 万个用户？每次查找平均遍历 50 万个——不可接受。

**你需要的**：给定一个 key（用户名），**瞬间**（O(1)）返回 value（用户信息）。不管数据库里有多少数据。

这就是哈希表。Redis 的整个数据库本质上就是一个巨大的哈希表。

---

## 2. 为什么普通方法不够好

| 方法 | 查找复杂度 | 为什么不够 |
|------|-----------|-----------|
| 数组（按索引） | O(1) | key 必须是整数索引，不能用字符串当 key |
| 链表 | O(n) | 必须从头遍历 |
| 有序数组 + 二分查找 | O(log n) | 比 O(1) 慢，而且要保持有序 |

> 核心矛盾：我们要的是**任意 key 类型的 O(1) 查找**。数组有 O(1) 但 key 被限制为整数；链表 key 可以是任意类型但查找是 O(n)。

---

## 3. 数据结构是如何解决问题的

### 哈希表的魔法：把任意 key 变成数组索引

```
key ──→ [哈希函数] ──→ 整数 ──→ 数组[整数] = value

例如:
  "Alice"  → hash("Alice") → 7  → bucket[7] = {"name": "Alice", "age": 30}
  "Bob"    → hash("Bob")   → 2  → bucket[2] = {"name": "Bob", "age": 25}
  "Eve"    → hash("Eve")   → 7  → ⚡ 冲突！"Alice" 和 "Eve" 都映射到了 bucket[7]
```

### 处理冲突：链地址法

```
bucket[7]: ("Alice", data1) → ("Eve", data2) → None
               ↑
         一个小链表！

查找 "Eve":
  1. hash("Eve") → 7
  2. 在 bucket[7] 的链表中遍历 → 找到 "Eve"
  
  → 冲突少 = 链表短 = O(1)
  → 冲突多 = 链表长 = 退化到 O(n)
```

### 动态扩容：保持 O(1) 的关键

```
负载因子 = 存储元素数 / 桶数量

负载因子低（0.3）:
  [A][ ][B][ ][ ][C][ ][ ]   ← 大部分桶空着，浪费空间但冲突少
  
负载因子高（0.9）:
  [A→D→G][B→E][C→F→H→I]     ← 链表变长了！查找退化

扩容: 负载因子 > 0.75 时，桶数量 × 2，重新哈希所有元素。
      空间换时间——更多空桶 = 更少冲突 = 更快查找。
```

---

## 4. 数据结构原理

### 一个好哈希函数的三个要求

1. **确定性**：同一个 key 永远得到同一个 hash（否则你存进去就找不到了）
2. **均匀分布**：不同的 key 尽量分散到不同的 bucket（否则都在一个桶里，退化成链表）
3. **快速计算**：O(1) 的哈希函数（否则 O(1) 查找就失去意义了）

Python 内置的 `hash()` 函数满足这三个条件。

### 哈希表的完整生命周期

```
初始化: buckets = [ [], [], [], [] ]  (4 个空桶)
        
put("A", 1):  hash("A")→2,  buckets[2] = [("A",1)]
put("B", 2):  hash("B")→0,  buckets[0] = [("B",2)]
put("C", 3):  hash("C")→2,  buckets[2] = [("A",1),("C",3)]  ← 冲突！
put("D", 4):  hash("D")→3,  buckets[3] = [("D",4)]
              → 负载 = 4/4 = 1.0 > 0.75 → 扩容!
              
扩容后: buckets = [ [], [], ..., [] ]  (8 个空桶)
        重新哈希所有 4 个元素到新桶中
```

---

## 5. Python 从零实现

打开 `hash_table.py`，核心代码：

### 哈希函数 + 冲突处理

```python
class HashTable:
    def __init__(self, initial_capacity=8):
        self._capacity = initial_capacity
        self._size = 0
        self._buckets = [[] for _ in range(initial_capacity)]

    def _hash(self, key):
        """把 key 变成 [0, capacity) 范围内的整数"""
        return abs(hash(key)) % self._capacity

    def put(self, key, value):
        idx = self._hash(key)
        bucket = self._buckets[idx]
        
        # 检查 key 是否已存在（更新）
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        
        # 新 key，追加到 bucket 链表
        bucket.append((key, value))
        self._size += 1
        
        # 负载过高 → 扩容
        if self._size / self._capacity > 0.75:
            self._resize(self._capacity * 2)
```

### 扩容（rehash）

```python
def _resize(self, new_capacity):
    old_buckets = self._buckets
    self._capacity = new_capacity
    self._buckets = [[] for _ in range(new_capacity)]
    self._size = 0
    
    # 把所有元素重新哈希到新桶中
    for bucket in old_buckets:
        for key, value in bucket:
            self.put(key, value)  # ← 重新计算 hash, 放到新位置
```

---

## 6. 时间复杂度分析

| 操作 | 平均 | 最坏 | 原因 |
|------|------|------|------|
| `put(k, v)` | O(1) | O(n) | 最坏：所有 key 碰撞在一个桶里 |
| `get(k)` | O(1) | O(n) | 同上 |
| `delete(k)` | O(1) | O(n) | 同上 |
| `_resize()` | O(n) | O(n) | 重新哈希所有元素 |

> 「平均 O(1)」的前提：好的哈希函数 + 合理的负载因子。Python dict 精心设计了这两者，所以日常使用中就是 O(1)。

### 哈希表 vs 之前学的数据结构

| | 哈希表 | 链表 | 有序数组 | 树 |
|------|--------|------|---------|-----|
| 插入 | **O(1)** | O(1) | O(n) | O(log n) |
| 查找 | **O(1)** | O(n) | O(log n) | O(log n) |
| 删除 | **O(1)** | O(n) | O(n) | O(log n) |
| 有序？ | **❌** | ✅ | ✅ | ✅ |
| 范围查询？ | **❌** | ❌ | ✅ | ✅ |

> 哈希表的 O(1) 是用「放弃顺序」换来的。这是贯穿 s05→s06→s07 的核心 tradeoff。

---

## 7. 小型项目实践

### Mini Redis 框架

打开 `mini_redis.py`——`MiniRedis` 类有 3 个 TODO 方法：

| 方法 | 你的任务 |
|------|---------|
| `set(key, value, ttl=None)` | 存入 HashTable + 处理过期时间 |
| `get(key, default=None)` | 检查是否过期 → 从 HashTable 取出 |
| `delete(key)` | 从 HashTable 和 expiry 中移除 |

**TTL（过期时间）的设计**：用一个单独的 dict 存储 `key → 过期时间戳`。get 时先检查是否过期——这是 Redis 真实使用的策略。

### 你的任务

1. 读懂 `hash_table.py`（重点：`_hash` 函数和 `_resize` 扩容逻辑）
2. 打开 `mini_redis.py`，实现 3 个 TODO 方法
3. 思考：如果要在 MiniRedis 上加一个 `keys_by_prefix("user:*")` 功能，哈希表能做到吗？复杂度是多少？

---

## 8. 可视化运行过程

运行 `python s24_data_structures/s05_mini_redis/code.py`：

```
步骤 1: 哈希表基础
  [ 2] ('age':30)
  [ 6] ('name':'Alice')
  [ 7] ('city':'Beijing')
  get('name') = 'Alice'  ← O(1)!

步骤 2: 动态扩容
  put('key-0') → 容量=4, 负载=0.25
  put('key-3') → 容量=8, 负载=0.50  ← 自动扩容了！
  put('key-6') → 容量=16, 负载=0.44

步骤 3: Mini Redis — TTL 过期
  set("temp:token", "abc123", ttl=1)
  等待 2 秒...
  get("temp:token") = 'EXPIRED'  ← 自动过期！
```

---

## 9. 思考题

1. **为什么负载因子选 0.75？** 选 0.5（更早扩容）或 0.9（更晚扩容）各有什么优缺点？时间和空间在这里是如何交换的？

2. **哈希表为什么不能做范围查询？** `get("A")` 是 O(1)，但「所有 key 在 A-M 之间的 value」要怎么做？这和 key 的存储方式有什么关系？

3. **Python 的 dict 和本章的 HashTable 有什么区别？** Python dict 用了开放地址法而不是链地址法——为什么？这两种策略各有什么适用场景？

4. **如果哈希函数特别慢（比如每次都计算 SHA-256），哈希表的性能会怎样？** 什么时候值得用慢但均匀的哈希函数？

5. **打开 `mini_redis.py`**，实现 `set()`。你的 TTL 逻辑中，如果对同一个 key 连续调用 `set("a", 1, ttl=100)` 和 `set("a", 2)`（没有 TTL），第二次调用应该清除 TTL 吗？

---

## 10. 本章总结

| 概念 | 一句话 |
|------|--------|
| 哈希函数 | 把任意 key 变成 [0, capacity) 范围内的整数 |
| 冲突 | 两个不同 key 映射到同一个 bucket |
| 链地址法 | 每个 bucket 是一个小链表，冲突时追加 |
| 负载因子 | 元素数/桶数量，决定何时扩容 |
| Rehash | 扩容后重新给所有元素分配桶 |
| O(1) 的代价 | 放弃顺序——无法范围查询、排序、排名 |

> **核心收获**：哈希表是「速度换顺序」的极致。O(1) 让你瞬间存取，但 key 之间的顺序关系完全丢失。下一章（s06）你会看到「有序」在工程中到底有多重要——以及哈希表面对这些需求时有多无力。

---

**上一章**: [s04: Mini File System — 树](../s04_mini_fs/)
**下一章**: [s06: 有序 vs 无序 — ★ 过渡章](../s06_ordered_world/)
