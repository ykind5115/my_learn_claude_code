# s06: Set — 去重与集合运算

[s05](../s05_hash/) → `s06` → [s07](../s07_sorted_set/) → ... → s18
> *"Set 不是数组，是黑板上的一袋标签——每个标签独一无二，还能做交集、并集、差集。"*
>
> **前提知识**: 做过 s04（List 的两端操作）。理解「共享黑板」模型。

---

## 1. 为什么需要 Set？

先想几个真实场景：

| 场景 | 问题 |
|------|------|
| **文章标签** | 一篇文章可以有多个标签，同一个标签不能重复出现 |
| **点赞用户** | 一个用户只能给一篇文章点一个赞，不能重复点赞 |
| **共同好友** | 找出两个用户共同的好友——交集运算 |
| **抽奖池** | 从所有参与用户中随机抽取 N 个中奖者 |
| **IP 黑名单** | 封禁的 IP 集合，检查某个 IP 是否在集合中 |

### 用 List 能实现吗？

不太行。List 的元素是**有序的、可重复的**。

```bash
# List 不擅长去重
LPUSH tags "Redis"
LPUSH tags "Redis"      # 还能再推入一个——重复了！
LRANGE tags 0 -1
1) "Redis"
2) "Redis"              # 去重要自己处理
```

### Set 的优势

```bash
# Set 自动去重
SADD tags "Redis"
SADD tags "Redis"       # 返回 0——已经有了，不加
SMEMBERS tags
1) "Redis"              # 只有一份
```

| 特征 | List | Set |
|------|------|-----|
| **有序** | ✅ 按插入顺序 | ❌ 无序 |
| **可重复** | ✅ 可以重复 | ❌ 自动去重 |
| **集合运算** | ❌ 无 | ✅ 交/并/差 |
| **随机元素** | ❌ 索引访问 | ✅ SRANDMEMBER / SPOP |
| **成员检查** | O(n) 遍历 | O(1) 哈希表 |

> **Set 的核心价值：自动去重 + O(1) 成员检查 + 集合运算。**

---

## 2. 黑板模型下的 Set

### 一袋不重复的标签贴纸

把 Set 想象成黑板上贴着的一袋**小标签**：

```
┌─────────────────────────────────────────────┐
│  article:42:tags                             │
│                                              │
│    ┌─────────────┐                           │
│    │             │                           │
│    │  "Redis"    │  ← 每张标签独一无二       │
│    │             │                           │
│    │  "教程"     │                           │
│    │             │                           │
│    │  "NoSQL"    │                           │
│    │             │                           │
│    │  "缓存"     │                           │
│    │             │                           │
│    └─────────────┘                           │
│                                              │
│  每张标签 = 一个 member                      │
│  没有顺序，没有索引，只有「在不在袋子里」      │
│  袋子里的标签不重复——同一种标签不能贴两张     │
└─────────────────────────────────────────────┘
```

### 三种集合运算

```
文章 A 的标签:   {Redis, 教程, NoSQL}
文章 B 的标签:   {Redis, 实战, Python}

交集 SINTER:      {Redis}              ← 两篇文章的共同标签
并集 SUNION:      {Redis, 教程, NoSQL, 实战, Python}  ← 所有标签去重
差集 SDIFF:       {教程, NoSQL}        ← A 有但 B 没有的
```

---

## 3. 怎么做 — 逐行解释

### 3.1 SADD — 在袋子里加一张标签

```bash
redis> SADD tags "Redis" "教程" "NoSQL"
(integer) 3          # 成功添加了 3 个成员
redis> SADD tags "Redis"
(integer) 0          # "Redis" 已经在了——没有新增
```

`SADD` 返回**实际新增的成员数量**。如果所有成员都已存在，返回 0。

### 3.2 SMEMBERS — 看袋子里所有标签

```bash
redis> SMEMBERS tags
1) "Redis"
2) "教程"
3) "NoSQL"
```

> **⚠️ 注意**：SMEMBERS 返回所有成员，大集合时慎用（和 KEYS *、HGETALL 一样的风险）。

### 3.3 SISMEMBER — 检查某张标签在不在

```bash
redis> SISMEMBER tags "Redis"
(integer) 1          # 存在
redis> SISMEMBER tags "MySQL"
(integer) 0          # 不存在
```

O(1) 时间复杂度——不管集合有 10 个还是 1000 万个成员，检查速度一样快。

### 3.4 SREM — 从袋子里拿走一张标签

```bash
redis> SREM tags "NoSQL"
(integer) 1          # 删除了 1 个成员
redis> SREM tags "MySQL"
(integer) 0          # 不存在，没删掉
redis> SMEMBERS tags
1) "Redis"
2) "教程"
```

### 3.5 SCARD — 袋子里有几张标签？

```bash
redis> SCARD tags
(integer) 2          # 2 个成员
```

O(1) 操作——和 LLEN、HLEN 一样，内部维护了计数器。

### 3.6 SINTER — 交集（共同部分）

```bash
redis> SADD set_a "A" "B" "C"
redis> SADD set_b "B" "C" "D"

redis> SINTER set_a set_b
1) "B"
2) "C"               # 两个集合共有的元素
```

**实战场景 —— 共同好友**：

```bash
redis> SADD user:1001:friends "user:1002" "user:1003" "user:1004"
redis> SADD user:1002:friends "user:1001" "user:1003" "user:1005"

redis> SINTER user:1001:friends user:1002:friends
1) "user:1003"       # 共同好友
```

### 3.7 SUNION — 并集（全部去重）

```bash
redis> SUNION set_a set_b
1) "A"
2) "B"
3) "C"
4) "D"               # 两个集合合在一起，去重
```

**实战场景 —— 所有标签**：

```bash
redis> SADD article:1:tags "Redis" "教程"
redis> SADD article:2:tags "Python" "教程"

redis> SUNION article:1:tags article:2:tags
1) "Python"
2) "Redis"
3) "教程"            # 所有标签去重合并
```

### 3.8 SDIFF — 差集（我有你没有）

```bash
redis> SDIFF set_a set_b
1) "A"               # set_a 有但 set_b 没有的
redis> SDIFF set_b set_a
1) "D"               # set_b 有但 set_a 没有的
```

**实战场景 —— 推荐关注**：推荐 user:1001 关注「他的好友中有但 user:1002 没有的好友」：

```bash
redis> SDIFF user:1001:friends user:1002:friends
1) "user:1004"       # 1001 有但 1002 没有的好友
```

### 3.9 SRANDMEMBER — 随机抽一张标签（不删除）

```bash
redis> SADD pool "用户A" "用户B" "用户C" "用户D" "用户E"

redis> SRANDMEMBER pool       # 随机抽一个（不删）
"用户C"
redis> SRANDMEMBER pool 3     # 随机抽 3 个（不删）
1) "用户A"
2) "用户D"
3) "用户E"
```

### 3.10 SPOP — 随机弹出一张标签（删除）

```bash
redis> SPOP pool               # 随机弹出一个（删除）
"用户B"
redis> SPOP pool 2             # 随机弹出 2 个（删除）
1) "用户C"
2) "用户E"
redis> SMEMBERS pool
1) "用户A"
2) "用户D"
```

`SRANDMEMBER` vs `SPOP`：

| | SRANDMEMBER | SPOP |
|--|-----------|------|
| 是否删除 | 不删 | 删掉 |
| 用途 | 抽奖展示（不减少名额） | 抽奖发奖（减少名额） |
| 可以重复抽到 | ✅ 可以（不删就能再抽到） | ❌ 不会（删了就没了） |

---

## 4. 经典实战：文章标签系统

```bash
# 给文章 42 打标签
SADD article:42:tags "Redis" "教程" "NoSQL" "缓存"

# 给文章 43 打标签
SADD article:43:tags "Redis" "Python" "教程"

# 文章 42 的所有标签
SMEMBERS article:42:tags

# 两篇文章的共同标签（交）
SINTER article:42:tags article:43:tags
→ "Redis", "教程"

# 所有标签（并）
SUNION article:42:tags article:43:tags
→ "Redis", "教程", "NoSQL", "缓存", "Python"

# 文章 42 独有标签（差）
SDIFF article:42:tags article:43:tags
→ "NoSQL", "缓存"

# 检查文章 42 是否有 "Redis" 标签
SISMEMBER article:42:tags "Redis"
→ 1 (是)

# 删掉一个标签
SREM article:42:tags "NoSQL"
```

---

## 5. 常见错误（新手必读）

### ❌ 错误 1：SMEMBERS 用于大集合

```bash
redis> SMEMBERS all_users    # 如果集合有 1000 万个用户 ID...
```

和 KEYS *、LRANGE 0 -1、HGETALL 一样的陷阱——数据量大时会阻塞 Redis。

**替代方案**：用 `SSCAN` 分批迭代：

```python
cursor = 0
while True:
    cursor, members = client.sscan("all_users", cursor)
    for member in members:
        process(member)
    if cursor == 0:
        break
```

### ❌ 错误 2：以为 SADD 的返回值是集合大小

```bash
redis> SADD myset "A" "B"
(integer) 2        # 这是「新增了几个」，不是集合大小
redis> SADD myset "A"
(integer) 0        # 没新增，但集合大小是 2
redis> SCARD myset
(integer) 2        # SCARD 才是集合大小
```

### ❌ 错误 3：集合运算在大数据量下的性能

```bash
SINTER set_a set_b    # 如果 set_a 有 100 万个，set_b 有 100 万个
```

集合运算（SINTER、SUNION、SDIFF）的时间复杂度是 **O(N)**——遍历较小的集合进行哈希表查找。虽然比 O(N*M) 好很多，但如果两个集合都很大，还是会消耗 CPU。

如果需要频繁对大数据集做集合运算，考虑：
- 把结果缓存起来
- 用 Bitmap 或 HyperLogLog 替代（特定场景）

### ❌ 错误 4：把「有序」的希望寄托在 Set 上

```bash
# Set 是无序的——别指望 SMEMBERS 的顺序
redis> SADD myset "A" "B" "C"
redis> SMEMBERS myset
1) "C"    # 有可能不是插入顺序
2) "A"
3) "B"
```

Set 不保证顺序。如果你需要有序的集合，用 Sorted Set（s07）。

### ❌ 错误 5：SRANDMEMBER 可能返回重复

```bash
# 集合只有 3 个元素，但你要抽 5 个
redis> SRANDMEMBER small_set 5
1) "A"      # 会重复——因为只有 3 个不重复的
2) "B"
3) "C"
4) "A"      # 重复了！
5) "B"      # 重复了！
```

当请求数量超过集合大小时，`SRANDMEMBER` 会允许重复。如果你需要绝对不重复的随机抽取，用 SPOP（但会改变集合）。

---

## 6. 你学到了什么

| 命令 | 黑板动作 | 时间复杂度 |
|------|---------|-----------|
| `SADD key member` | 往袋子里加一张标签（自动去重） | O(1) |
| `SMEMBERS key` | 看袋子里所有标签 | O(n) |
| `SISMEMBER key member` | 检查标签是否在袋子里 | O(1) |
| `SREM key member` | 从袋子里拿走一张标签 | O(1) |
| `SCARD key` | 看袋子里有几张标签 | O(1) |
| `SINTER key1 key2` | 交集——两个袋子共有的标签 | O(n) |
| `SUNION key1 key2` | 并集——两个袋子合起来去重 | O(n) |
| `SDIFF key1 key2` | 差集——key1 有但 key2 没有的 | O(n) |
| `SRANDMEMBER key` | 随机看一张标签（不删除） | O(1) |
| `SPOP key` | 随机弹出一张标签（删除） | O(1) |
| `SSCAN key cursor` | 分批迭代（代替 SMEMBERS） | O(n) |

### 一句话总结

```
Set = 自动去重 + O(1) 成员检查 + 集合运算（交/并/差）
```

---

## 7. 自己动手

1. **标签系统**：创建 3 个 Set（每篇文章的标签），每个 Set 有 3-5 个标签，练习 SINTER 找共同标签

2. **点赞去重**：`SADD likes:article:42 "user:1001"`，然后再次 SADD 同一个用户——确认返回 0

3. **SCARD 练习**：创建 Set 后反复 SADD，同时用 SCARD 看集合大小变化

4. **SISMEMBER 练习**：检查某个元素是否在集合中，然后 SREM 后再检查

5. **随机抽奖**：创建 10 个用户的 Set，用 SRANDMEMBER 抽 3 个（不删除），再用 SPOP 抽 3 个（删除），比较两者的区别

6. **运行 code.py**：`python s25_redis/s06_set/code.py`，看每一步的黑板状态变化

---

> **下一章：[s07: Sorted Set — 排行榜](../s07_sorted_set/)** — 学会用 ZSet 做积分排行榜、延迟队列
