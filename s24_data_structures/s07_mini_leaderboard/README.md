# s07: Mini Leaderboard — 跳表

> *"跳表 = 给有序链表加了高速公路。你在高层飙车，接近出口时降到低层——和开车导航一模一样。"*
>
> **前提知识**: 学过 s05（哈希表）和 s06（有序数组）。理解 O(n)、O(log n)、有序 vs 无序的 tradeoff。

---

## 1. 本章工程问题

经过 s06，你已经看到：游戏排行榜需要「插入快 + 能排序 + 能排名」——哈希表和有序数组各自只满足一半。

| 需求 | 哈希表 | 有序数组 | 我们要的 |
|------|--------|---------|---------|
| 插入/更新分数 | O(1) ✅ | O(n) ❌ | O(log n) |
| 查某人的排名 | ❌ | O(1) ✅ | O(log n) |
| Top 100 | ❌ | O(1) ✅ | O(log n) |
| 范围查询 | ❌ | O(log n + k) ✅ | O(log n + k) |

**Redis 的解决方案是跳表（Skip List）**——它的 sorted set 底层就是跳表。平衡树也能做到，但跳表更简单、代码更少、性能相当。

---

## 2. 核心思想：给链表加「高速公路」

### 普通有序链表

```
1 → 5 → 9 → 13 → 18 → 25 → 30 → 42 → 50 → 63 → 79 → 88 → 95
```

查找 79：要从 1 开始，一步一步走到 79——12 步。最坏情况 O(n)。

### 加一层索引

```
第 1 层: 1 ─────→ 9 ─────→ 18 ─────→ 30 ─────→ 50 ─────→ 79 ─────→ 95
         ↓         ↓         ↓         ↓         ↓         ↓         ↓
第 0 层: 1 → 5 → 9 → 13 → 18 → 25 → 30 → 42 → 50 → 63 → 79 → 88 → 95
```

查找 79：
1. 从第 1 层开始：1 → 9 → 18 → 30 → 50 → **79**（6 步！）
2. 第 1 层到了 79，下降

从 12 步降到 6 步。

### 再加一层

```
第 2 层: 1 ─────────────────→ 30 ─────────────────→ 79
         ↓                    ↓                      ↓
第 1 层: 1 ─────→ 9 ─────→ 18 ─────→ 30 ─────→ 50 ─────→ 79 ─────→ 95
         ↓         ↓         ↓         ↓         ↓         ↓         ↓
第 0 层: 1 → 5 → 9 → 13 → 18 → 25 → 30 → 42 → 50 → 63 → 79 → 88 → 95
```

查找 79：1 → 30 → 79——3 步！从 12 步降到 3 步。

### 这就是跳表的精髓

- 第 0 层：完整数据（保证不丢）
- 第 k 层：第 k-1 层的「索引」（每 2 个挑 1 个）
- 查找时从最高层开始，高层大步跳，低层精细找

---

## 3. 数据结构原理

### 跳表 vs 有序数组 vs 平衡树

| | 跳表 | 有序数组 | 平衡树（AVL/红黑） |
|------|------|---------|------------------|
| 插入 | O(log n) 期望 | O(n) | O(log n) 确定 |
| 查找 | O(log n) 期望 | O(log n) | O(log n) 确定 |
| 排名 | O(log n) | O(1) | O(log n)（需维护 size） |
| 实现难度 | **简单** | 最简单 | 复杂（旋转！） |
| 额外空间 | O(n)（多层索引） | O(1) | O(n) |

> 跳表的关键优势：实现比平衡树简单得多（不需要旋转），性能相当。Redis 选它是有原因的。

### 概率平衡

跳表不用强制平衡——它靠**抛硬币**决定新节点有多少层索引：

```python
def random_level():
    level = 0
    while random.random() < 0.5:  # 50% 概率再升一层
        level += 1
    return level
```

- 50% 概率：只有第 0 层（普通节点）
- 25% 概率：有第 0、1 层
- 12.5% 概率：有第 0、1、2 层
- ...

虽然每次插入是随机的，但**期望**上，高层节点恰好是低层的一半——自动保持了平衡。

---

## 4. 跳表操作详解

### 查找（search）

```
search(63):

从最高层(第 2 层)开始:
  1 → 30 → 79（79 > 63, 退回到 30）
  下降到第 1 层，从 30 继续:
  30 → 50 → 79（79 > 63, 退回到 50）
  下降到第 0 层，从 50 继续:
  50 → 63 → 找到！
```

### 插入（insert）

```
insert(55):

1. 找到每层的前驱节点（和查找类似）:
   update[2] = 30
   update[1] = 50
   update[0] = 50

2. 随机生成层数（假设抛硬币得了 1 层）
   new_node.level = 1

3. 在各层插入新节点:
   第 1 层: 50 → 55 → 79
   第 0 层: 50 → 55 → 63
```

### 排名（rank）

跳表节点多维护一个 `span`（跨度）——在第 i 层，从这个节点到下一个节点「跨越了多少个第 0 层节点」。

```
第 1 层: 1 ──(span=4)──→ 18 ──(span=4)──→ 50
第 0 层: 1 → 5 → 9 → 13 → 18 → 25 → 30 → 42 → 50

找 30 的排名:
  从 1 沿第 1 层走 → 1 到 18 跨了 4 个, 然后 18 到 50 跨了 4 个（走过了）
  下降到第 0 层 → 18 → 25 → 30（走了 3 步）
  排名 = 4 + 3 = 7（1-based: 第 7 个）
```

> span 让跳表在 O(log n) 时间内计算排名——这是有序数组做不到的（有序数组查排名是 O(1)，但插入是 O(n)）。

---

## 5. Python 从零实现

打开 `skip_list.py`，核心代码：

### 查找 + 插入

```python
class SkipList:
    def search(self, key):
        current = self.head
        # 从最高层往下
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]  # 在这一层往前走
        current = current.forward[0]  # 下降到第 0 层
        if current and current.key == key:
            return current.value
        return None

    def insert(self, key, value):
        update = [None] * (MAX_LEVEL + 1)  # 每层的前驱
        current = self.head
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current  # 记录这一层在哪里插入
        
        new_level = self._random_level()
        new_node = SkipNode(key, value, new_level)
        for i in range(new_level + 1):
            # 标准链表插入: newNode.next = prev.next; prev.next = newNode
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node
```

---

## 6. 时间复杂度分析

| 操作 | 期望复杂度 | 最坏复杂度 | 备注 |
|------|-----------|-----------|------|
| `search(key)` | O(log n) | O(n) | 最坏：运气极差，所有节点都在第 0 层 |
| `insert(key, val)` | O(log n) | O(n) | 同上 |
| `delete(key)` | O(log n) | O(n) | 同上 |
| `get_rank(key)` | O(log n) | O(n) | 依赖 span 计算 |
| `top_n(n)` | O(n) | O(n) | 需要遍历第 0 层尾部 |

期望 O(log n) 的前提：概率平衡正常工作。在 Redis 实际使用中，跳表表现非常稳定。

### 空间复杂度

每个节点期望有 2 个 forward 指针（因为每层 50% 概率）= 2n 个指针 = O(n)。这比平衡树的每个节点 2 个指针略多，但实现简单得多。

---

## 7. 小型项目实践

### Mini Leaderboard 框架

打开 `mini_leaderboard.py`——`Leaderboard` 类有 2 个 TODO 方法：

| 方法 | 你的任务 |
|------|---------|
| `update_score(player, new_score)` | 如果玩家已有分数 → 删除旧分数 → 插入新分数 |
| `get_rank(player)` | 从 `players` dict 拿到分数 → `scores.get_rank(score)` |

**设计要点**：
- `scores`（SkipList）：score → player_name，负责排序和排名
- `players`（dict）：player_name → score，负责 O(1) 查找玩家的分数（反向索引）

这两个结构**互补**——dict 快速找到分数，SkipList 把分数变为排名。

### 你的任务

1. 读懂 `skip_list.py`（重点是 `search` 的「从高层往下走」逻辑）
2. 打开 `mini_leaderboard.py`，实现 2 个 TODO 方法
3. 思考：如果两个玩家分数相同，排名应该一样吗？怎么处理？

---

## 8. 可视化运行过程

运行 `python s24_data_structures/s07_mini_leaderboard/code.py`：

```
步骤 1: 跳表结构
  Lv2: 92:Bob
  Lv1: 78:Charlie → 92:Bob
  Lv0: 78:Charlie → 85:Alice → 88:Eve → 92:Bob → 95:Diana

  search(88) = 'Eve'
  rank(88)  = 第 3 名（从低到高: 78, 85, 88 → 第 3）

步骤 2: Mini Leaderboard
  #1 Diana: 2500
  #2 Bob: 2200
  #3 Frank: 1900
  
  Eve 分数更新为 2600 后:
  新的 #1: Eve (2600)
```

---

## 9. 思考题

1. **跳表的「概率平衡」和平衡树的「强制平衡」有什么区别？** 如果运气极差——每次 random_level() 都返回 0——跳表会变成什么？这种情况在工程中需要担心吗？

2. **为什么 Redis 选跳表而不是红黑树？** 从实现复杂度、调试难度、可维护性三个角度分析。

3. **span（跨度）是跳表排名查询的关键。** 如果不维护 span，get_rank 的复杂度是多少？和 span 版本差了多少倍？

4. **跳表能支持范围查询吗？** 和 s06 的有序数组的范围查询比，跳表有什么优势？

5. **打开 `mini_leaderboard.py`**，实现 `update_score()`。如果玩家从 1500 分更新到 1500 分（没变），你的实现会怎么处理？应该怎么优化？

---

## 10. 本章总结

| 概念 | 一句话 |
|------|--------|
| 跳表 | 多层索引的有序链表——每层是下层的「高速公路」 |
| 概率平衡 | 抛硬币决定层数——平均 O(log n)，不需要旋转 |
| 查找 | 从高层大步跳，接近目标时降层——O(log n) |
| 排名 | span 记录跨度——O(log n) 计算排名 |
| 和平衡树对比 | 实现更简单，性能相当 |
| 和有序数组对比 | 插入从 O(n) 降到 O(log n)，排名多了 O(log n) 成本 |

> **核心收获**：跳表在「插入速度」和「有序访问」之间取得了平衡——O(log n) 两边都不极致，但两边都够用。Redis 用它做排行榜，就是看重了「简单」+「够快」。

---

**上一章**: [s06: 有序 vs 无序 — ★ 过渡章](../s06_ordered_world/)
**下一章**: [s08: 内存 vs 磁盘 — ★ 过渡章](../s08_memory_vs_disk/)
