# s07: Sorted Set — 排行榜

[s06](../s06_set/) → `s07` → [s08](../s08_cache_patterns/) → ... → s18
> *"Sorted Set 不是 Set + 排序。Sorted Set 是一块积分榜——每个成员自带分数，永远按分数排好序。"*
>
> **前提知识**: 做过 s06（Set 的概念）。理解集合（不重复、成员检查）。

---

## 1. 为什么需要 Sorted Set？

先想一个经典需求：**游戏排行榜**。

```
玩家 张三   分数 1500
玩家 李四   分数 2200
玩家 王五   分数 1800
玩家 赵六   分数 950

需求：
  1. 查询排名（张三排第几？）
  2. 查询 Top 3（前三名是谁？）
  3. 分数更新（张三又赢了，加 50 分）
  4. 查询分数在 1000~2000 之间的人
```

### 用 List 实现？

```bash
# ❌ 用 List 存排行榜——要自己排序
RPUSH leaderboard "张三:1500" "李四:2200" "王五:1800"
# 要排序？自己写代码排序……
# 要查排名？遍历 List……
# 更新分数？找到元素 → 删除 → 插入新位置……
```

太痛苦了——每次更新都要 O(n) 遍历 + O(n log n) 排序。

### 用 Set 实现？

```bash
# ❌ 用 Set——没有分数概念
SADD players "张三" "李四" "王五"
# Set 不存分数，没法排序
# 要在外部维护一个分数表
```

### 用 Sorted Set ✅

```bash
ZADD leaderboard 1500 "张三"
ZADD leaderboard 2200 "李四"
ZADD leaderboard 1800 "王五"

# 查询 Top 3（按分数从高到低）
ZREVRANGE leaderboard 0 2 WITHSCORES
1) "李四"
2) "2200"
3) "王五"
4) "1800"
5) "张三"
6) "1500"

# 查询张三的排名
ZREVRANK leaderboard "张三"
(integer) 2    # 倒数第三名（分数最低）

# 张三赢了，加 50 分
ZINCRBY leaderboard 50 "张三"

# 查 1000~2000 分之间的人
ZCOUNT leaderboard 1000 2000
(integer) 2
```

**Sorted Set = Set（不重复）+ 分数 + 自动排序。**

---

## 2. 黑板模型下的 Sorted Set

### 积分榜

把 Sorted Set 想象成黑板上的一张**积分榜**：

```
┌─────────────────────────────────────┐
│  leaderboard                         │
│                                     │
│  排名 │  成员  │  分数              │
│  ─────────────────────────           │
│   1   │  李四  │  2200  ← 最高分    │
│   2   │  王五  │  1800              │
│   3   │  张三  │  1500  ← 最低分    │
│   4   │  赵六  │   950              │
│                                     │
│  每个成员只有一行（名字不重复）      │
│  永远按分数从小到大排好序            │
│  更新分数 = 自动重新排序（O(log n)）│
└─────────────────────────────────────┘
```

### 和 Set 的对比

```
Set:       { "张三", "李四", "王五" }      ← 只有成员，没有分数
Sorted Set: { "张三": 1500, "李四": 2200, "王五": 1800 }  ← 成员 + 分数
                   ↑           ↑           ↑
              每个成员都带着一个分数（score）
```

### 核心特性

| 特性 | 说明 |
|------|------|
| **成员唯一** | 和 Set 一样，每个成员只能出现一次 |
| **自带分数** | 每个成员关联一个浮点数分数（score） |
| **自动排序** | 永远按分数从小到大排序 |
| **O(log n) 操作** | 插入、更新、删除、查询排名都是对数复杂度 |
| **范围查询** | 按分数范围、按排名范围查询 |

> **Sorted Set 的内部实现是「跳跃表（skiplist）+ 哈希表」**——既保证有序，又保证 O(1) 的成员查找。

---

## 3. 怎么做 — 逐行解释

### 3.1 ZADD — 往积分榜添加成员

```bash
redis> ZADD leaderboard 1500 "张三"
(integer) 1          # 新增了 1 个成员
redis> ZADD leaderboard 2200 "李四"
(integer) 1
redis> ZADD leaderboard 1800 "王五"
(integer) 1
redis> ZADD leaderboard 950 "赵六"
(integer) 1
```

一次性添加多个：

```bash
redis> ZADD leaderboard 1500 "张三" 2200 "李四" 1800 "王五"
```

格式：`ZADD key score member [score member ...]`

如果成员已存在，ZADD 会**更新它的分数**：

```bash
redis> ZADD leaderboard 2000 "张三"    # 张三的分数从 1500 改成 2000
(integer) 0                             # 0 = 没有新增，只是更新
```

> ZADD 返回值：**新增的成员数量**。如果只是更新已有成员的分数，返回 0。

### 3.2 ZRANGE — 按排名范围查看（分数从低到高）

```bash
redis> ZRANGE leaderboard 0 -1         # 全部成员（分数从低到高）
1) "赵六"         # 950 分——最低分排第一
2) "张三"         # 1500 分
3) "王五"         # 1800 分
4) "李四"         # 2200 分——最高分排最后

redis> ZRANGE leaderboard 0 -1 WITHSCORES    # 带分数
1) "赵六"
2) "950"
3) "张三"
4) "1500"
5) "王五"
6) "1800"
7) "李四"
8) "2200"

redis> ZRANGE leaderboard 0 1          # 只看最低分的两个
1) "赵六"
2) "张三"
```

### 3.3 ZREVRANGE — 按排名范围查看（分数从高到低）

这是排行榜最常用的命令——从高到低看：

```bash
redis> ZREVRANGE leaderboard 0 2 WITHSCORES    # Top 3（分数从高到低）
1) "李四"         # 第 1 名——2200 分
2) "2200"
3) "王五"         # 第 2 名——1800 分
4) "1800"
5) "张三"         # 第 3 名——1500 分
6) "1500"
```

> **ZRANGE vs ZREVRANGE**：
> - `ZRANGE` = 分数从低到高（升序）
> - `ZREVRANGE` = 分数从高到低（降序）——排行榜的核心命令

### 3.4 ZRANK / ZREVRANK — 查排名

```bash
redis> ZRANK leaderboard "张三"        # 升序排名（从 0 开始）
(integer) 1                            # 排第 2（分数第二低）

redis> ZREVRANK leaderboard "张三"     # 降序排名（从 0 开始）
(integer) 2                            # 排第 3（分数第三高）
```

> **ZRANK vs ZREVRANK**：
> - `ZRANK` = 分数从低到高的排名（最低分 = 0）
> - `ZREVRANK` = 分数从高到低的排名（最高分 = 0）
> - 排名从 0 开始——排名 0 表示第一名

### 3.5 ZSCORE — 查某个成员的分数

```bash
redis> ZSCORE leaderboard "张三"
"1500"           # 张三的当前分数
redis> ZSCORE leaderboard "不存在的人"
(nil)            # 成员不存在
```

### 3.6 ZINCRBY — 原子增减分数

```bash
redis> ZINCRBY leaderboard 50 "张三"    # 张三加 50 分
"1550"                                   # 返回新分数
redis> ZINCRBY leaderboard -100 "王五"   # 王五减 100 分
"1700"
```

每次 ZINCRBY 后，Sorted Set 自动重新排序——不需要手动调整位置。

### 3.7 ZREM — 删除成员

```bash
redis> ZREM leaderboard "赵六"
(integer) 1          # 删除了 1 个成员
```

### 3.8 ZCARD — 看有多少成员

```bash
redis> ZCARD leaderboard
(integer) 3          # 3 个成员（赵六被删了）
```

### 3.9 ZCOUNT — 按分数范围统计人数

```bash
redis> ZCOUNT leaderboard 1000 2000    # 分数在 1000~2000 之间的人
(integer) 2                             # 张三和王五
redis> ZCOUNT leaderboard 2000 +inf    # 分数 ≥ 2000
(integer) 1                             # 李四
redis> ZCOUNT leaderboard -inf 1500    # 分数 ≤ 1500
(integer) 1                             # 张三
```

### 3.10 ZRANGEBYSCORE — 按分数范围查成员

```bash
redis> ZRANGEBYSCORE leaderboard 1000 2000 WITHSCORES
1) "张三"
2) "1500"
3) "王五"
4) "1800"
```

### 3.11 ZREMRANGEBYRANK — 按排名范围删除

```bash
redis> ZREMRANGEBYRANK leaderboard 0 0    # 删除最后一名（最小分数）
(integer) 1
```

**实战用法**：排行榜只保留 Top 100：

```bash
# 如果有 1000 个人，删除排名第 100 名之后的（保留前 100）
# 注意：ZREMRANGEBYRANK 是按升序排名删，0 = 最低分
# 要保留分数最高的 100 个，先 ZREVRANK 确认范围
# 更简单：ZREMRANGEBYRANK leaderboard 0 -101 删掉除了前 100 之外的所有
# （删除从最小到倒数第 101 个，相当于保留最后 100 个最高分）
```

---

## 4. 三个经典实战模式

### 模式 1：游戏积分排行榜

```bash
# 玩家注册时加入排行榜
ZADD game:leaderboard 0 "玩家张三"      # 初始 0 分
ZADD game:leaderboard 0 "玩家李四"
ZADD game:leaderboard 0 "玩家王五"

# 玩家赢得一局，加 100 分
ZINCRBY game:leaderboard 100 "玩家张三"

# 查看 Top 3
ZREVRANGE game:leaderboard 0 2 WITHSCORES

# 查看自己的排名
ZREVRANK game:leaderboard "玩家张三"

# 查看自己的分数
ZSCORE game:leaderboard "玩家张三"
```

### 模式 2：延迟队列（按时间排序的任务）

用时间戳作为分数，分数越小（时间越早）的任务越先执行：

```bash
# 添加延迟任务——当前时间戳作为分数
ZADD delay:queue 1720512000 "发送邮件:user@example.com"
ZADD delay:queue 1720512600 "生成周报"
ZADD delay:queue 1720513200 "清理缓存"

# 查看当前时间之前的所有任务（应该执行的任务）
ZRANGEBYSCORE delay:queue -inf 1720512300 WITHSCORES

# 取出并删除——从最早的任务开始处理
ZRANGEBYSCORE delay:queue -inf <当前时间戳>
# 处理完后删除
ZREMRANGEBYRANK delay:queue 0 <处理到的位置>
```

### 模式 3：限流滑动窗口（s10 会详细展开）

```bash
# 每个用户维护一个时间戳 ZSet
# 分数 = 请求时间戳，成员 = 请求的唯一标识

# 当前时间
now = 1720512000
# 1 分钟前
one_minute_ago = 1720511940

# 移除 1 分钟前的记录（过期滑动窗口）
ZREMRANGEBYSCORE user:rate:1001 -inf one_minute_ago

# 统计当前窗口内的请求数
ZCARD user:rate:1001

# 如果 < 10，允许请求并记录
ZADD user:rate:1001 now request_<uuid>
```

---

## 5. 常见错误（新手必读）

### ❌ 错误 1：分数相同时的排序规则

```bash
ZADD leaderboard 100 "张三"
ZADD leaderboard 100 "李四"     # 和张三同分

# 同分时按字典序（lexicographical order）排序
ZRANGE leaderboard 0 -1
1) "李四"          # "李" < "张" 在 Unicode 编码中——但要注意中文字典序！
2) "张三"
```

同分时，Redis 按成员名的字典序（字符串比较）排序。如果是英文，就是字母顺序。如果是中文，按字节比较。

### ❌ 错误 2：ZRANGE 和 ZREVRANGE 的排序方向搞混

```bash
ZRANGE key 0 -1      # 分数从低到高（最低分 = 索引 0）
ZREVRANGE key 0 -1   # 分数从高到低（最高分 = 索引 0）
```

**记忆技巧**：
- `ZRANGE` → 就是正常范围（小 → 大）
- `ZREVRANGE` → REVERSE 范围（大 → 小）
- 做排行榜用 `ZREVRANGE 0 2` —— 返回 Top 3

### ❌ 错误 3：大数据量 ZRANGE 阻塞

```bash
ZRANGE huge_zset 0 -1    # ❌ 如果 ZSet 有 100 万个成员……
```

和 SMEMBERS、HGETALL、LRANGE 0 -1 一样——返回全部成员，大数据量时导致阻塞和网络拥塞。

**替代方案**：用 `ZSCAN` 分批迭代，或限制每次查询的范围（如分页）。

### ❌ 错误 4：ZREMRANGEBYRANK 的参数理解

```bash
# 删除第一名到第三名？还是删除最后三名？
ZREMRANGEBYRANK leaderboard 0 2
```

`ZREMRANGEBYRANK` 是按**升序排名**删除（从低到高）。所以 `0 2` 删除的是分数最低的三个。

如果你要删除分数最高的三个：

```bash
# 先 ZCARD 获得总数，计算要删的起始位置
# 或者更直接：用 ZREMRANGEBYRANK 删除最后 N 个
ZREMRANGEBYRANK leaderboard -3 -1    # 删除最后三个（分数最高的三个）
```

### ❌ 错误 5：ZADD 和 ZINCRBY 混淆

```bash
# 假设张三当前 1500 分

ZADD leaderboard 2000 "张三"    # 直接把张三的分数设成 2000（覆盖）

ZINCRBY leaderboard 2000 "张三"  # 张三的分数变成 3500（1500 + 2000）
```

- `ZADD` = 设置/覆盖分数
- `ZINCRBY` = 在原有分数上增减

---

## 6. 你学到了什么

| 命令 | 黑板动作 | 时间复杂度 |
|------|---------|-----------|
| `ZADD key score member` | 在积分榜上写入一个成员 | O(log n) |
| `ZRANGE key start stop` | 按排名升序查看成员 | O(log n + m) |
| `ZREVRANGE key start stop` | 按排名降序查看（排行榜） | O(log n + m) |
| `ZRANK key member` | 查升序排名（最低分 = 0） | O(log n) |
| `ZREVRANK key member` | 查降序排名（最高分 = 0） | O(log n) |
| `ZSCORE key member` | 查某个成员的分数 | O(1) |
| `ZINCRBY key n member` | 成员分数加 n | O(log n) |
| `ZREM key member` | 删除成员 | O(log n) |
| `ZCARD key` | 看总成员数 | O(1) |
| `ZCOUNT key min max` | 统计分数在某个范围内的人数 | O(log n) |
| `ZRANGEBYSCORE key min max` | 按分数范围查成员 | O(log n + m) |
| `ZREMRANGEBYRANK key start stop` | 按排名范围删除 | O(log n + m) |

### 一句话总结

```
Sorted Set = Set（不重复）+ 分数 + 跳表（自动排序）
            = 排行榜、延迟队列、滑动窗口的天然解决方案
```

---

## 7. 自己动手

1. **创建排行榜**：用 ZADD 添加 5 个成员，分数分别为 100, 200, 300, 400, 500

2. **查 Top 3**：用 ZREVRANGE 0 2 WITHSCORES 查看前三名

3. **查排名**：用 ZRANK 和 ZREVRANK 查某个成员的排名，体会两者区别

4. **分数更新**：用 ZINCRBY 给最后一名加 500 分，然后用 ZREVRANGE 确认他变成了第一名

5. **分数范围查询**：用 ZCOUNT 和 ZRANGEBYSCORE 统计/查看 200~400 分之间的成员

6. **延迟队列练习**：用当前时间戳 + 10 秒作为分数，添加 3 个任务到 ZSet，然后用 ZRANGEBYSCORE -inf <当前时间戳> 查看哪些任务「已到期」

7. **运行 code.py**：`python s25_redis/s07_sorted_set/code.py`，看每一步的黑板状态变化

---

> **下一章：[s08: 缓存模式实战](../s08_cache_patterns/)** — 学完四种数据结构后，开始用它们解决真实世界的缓存问题
