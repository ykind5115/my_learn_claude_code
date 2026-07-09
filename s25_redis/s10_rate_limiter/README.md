# s10: 限流与滑动窗口 — 黑板上写"第 N 次"

[s09](../s09_distributed_lock/) → `s10` → [s11](../s11_rdb/)
> *"黑板上画一个计数器，每分钟清零一次：第 1 次、第 2 次... 超过上限就拒绝。"*
>
> **前提知识**: INCR + EXPIRE（s03），ZSET 基础操作（s07），过期时间（s02）。

---

## 1. 为什么需要限流？

**场景 1：API 滥用**

```
你提供了一个免费 API，每分钟允许 100 次调用。

正常用户:  5 次/分钟                     ✅ 正常
爬虫程序:  10000 次/分钟                 ❌ 服务器压力暴增
恶意攻击:  100000 次/分钟                💀 服务器挂了
```

**场景 2：资源公平分配**

```
一个抢票系统：
  100 张票，10000 人同时抢
  如果不限流 → 服务器被打挂 → 所有人都买不了

限流后：
  每秒只放 1000 个请求进系统 → 服务器稳定运行
  其他人排队等待或重试 → 公平
```

**场景 3：第三方 API 调用**

```
你调用的第三方 API 有频率限制：
  每分钟最多 100 次
  超了就被封 IP

你需要在本地也做限流 → 保证不超过对方的限制
```

> **限流 = 控制单位时间内的请求次数，保护系统不被冲垮。**

---

## 2. 在黑板模型下理解限流

```
多个人共用一块黑板，你站在黑板前维护秩序：

┌─────────────────────────────────────────────┐
│  共享黑板（当前时间段记录）                    │
│                                              │
│  固定窗口:                                   │
│    rate:limit:api_user:2024-01-15-14:30 = 87 │
│    上限 = 100                                │
│    87 < 100 → 放行                           │
│                                              │
│  滑动窗口:                                   │
│    rate:sliding:api_user =                   │
│      (req1 @ 14:30:01, req2 @ 14:30:05, ...) │
│    统计最近 60 秒内的请求数 → 决定是否放行    │
│                                              │
│  ┌──────────────┐                            │
│  │ 还剩 13 次   │ ← 计数器 + 时间维度        │
│  └──────────────┘                            │
└─────────────────────────────────────────────┘
```

**三种限流算法的核心差异**：

| 算法 | 原理 | 精准度 | 内存开销 |
|------|------|--------|---------|
| 固定窗口 | 一分钟一个计数器 | 低（边界突刺） | 极低 |
| 滑动窗口 | ZSET 记录每次请求的时间 | 高 | 较高 |
| 令牌桶 | 匀速发放令牌 | 中等（可应对突发） | 低 |

---

## 3. 固定窗口 — 最简单，但有边界尖峰

### 实现原理

```python
# 每分钟一个计数器，到下一分钟自动重置
key = f"rate_limit:{user_id}:{datetime.now().minute}"
count = redis.incr(key)          # 计数器 +1
if count == 1:
    redis.expire(key, 60)        # 第一请求时设过期时间

if count > 100:
    return "rate limit exceeded"  # 超过限制
else:
    return "ok"                   # 正常放行
```

### 边界尖峰问题

```
把一分钟分成 60 秒：

固定窗口 1: [00:00:00 ───── 00:01:00)    上限 = 100
固定窗口 2: [00:01:00 ───── 00:02:00)    上限 = 100

如果请求集中在窗口边界：
  00:00:59 → 第 100 次请求（窗口 1 满）
  00:01:00 → 第 101 次请求（窗口 2 清空重置）

问题：在 00:00:59 ~ 00:01:01 这 2 秒内，通过了 200 个请求！
虽然每个窗口都没超限，但瞬时 QPS 高达 100/秒！

这就是「边界尖峰」(boundary burst) 问题。
```

> 固定窗口的问题在于**窗口切换的瞬间**。如果请求分布在整分钟内没问题，但如果集中在边界上，限流效果大打折扣。

---

## 4. 滑动窗口 — 精准但内存开销大

### 实现原理

用 ZSET 记录每次请求的时间戳，通过 ZREMRANGEBYSCORE 和 ZCARD 实现精确计数：

```python
import time

def sliding_window_rate_limit(user_id, max_requests=100, window_seconds=60):
    key = f"rate:sliding:{user_id}"
    now = time.time()
    window_start = now - window_seconds

    pipe = redis.pipeline()
    # 移除窗口外的时间戳
    pipe.zremrangebyscore(key, 0, window_start)
    # 添加当前请求
    pipe.zadd(key, {str(now): now})
    # 设置过期时间（防止内存泄漏）
    pipe.expire(key, window_seconds + 10)
    # 统计窗口内请求数
    pipe.zcard(key)
    results = pipe.execute()

    count = results[-1]  # zcard 的结果
    return count <= max_requests
```

```
时间维度展开：

请求序列（每分钟上限 5 次）：
  T=0s   第 1 次 → ZSET: [0]
  T=10s  第 2 次 → ZSET: [0, 10]
  T=20s  第 3 次 → ZSET: [0, 10, 20]
  T=30s  第 4 次 → ZSET: [0, 10, 20, 30]
  T=40s  第 5 次 → ZSET: [0, 10, 20, 30, 40]  → 已达上限
  T=50s  第 6 次 → ❌ 拒绝

  T=70s  清理窗口外 → [10, 20, 30, 40, 70]
  T=70s  第 7 次 → ZSET: [10, 20, 30, 40, 70]  → 已达上限（还在窗口内的旧请求有 4 个）
  T=80s  第 8 次 → 清理 [10] → [20, 30, 40, 70, 80] → 已达上限
  T=90s  第 9 次 → 清理 [20] → [30, 40, 70, 80, 90] → 已达上限
  T=100s 第 10 次 → 清理 [30] → [40, 70, 80, 90, 100] → 已达上限
```

> **滑动窗口 = 固定窗口的升级版**。不再用整分钟切割，而是以"当前时间往前推 N 秒"作为窗口，边界尖峰问题自然消失。

### 优化：降低内存开销

如果每秒请求量极大（如 10000 QPS），ZSET 会塞入大量元素。可以**降低精度**来减少内存：

```python
# 不记录每毫秒的请求，而是按秒/百毫秒聚合
# 用时间戳的整数秒作为 member，INCR 累加同秒的计数

def sliding_window_optimized(user_id, max_requests=100, window_seconds=60):
    key = f"rate:opt:{user_id}"
    now_second = int(time.time())
    window_start = now_second - window_seconds

    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zincrby(key, 1, str(now_second))      # 同秒的请求聚合计数
    pipe.expire(key, window_seconds + 10)
    # 统计时需要遍历计算
    pipe.zrange(key, 0, -1, withscores=True)
    results = pipe.execute()

    members = results[-1]
    total = sum(int(score) for _, score in members)
    return total <= max_requests
```

---

## 5. 令牌桶算法 — 匀速放行

### 算法思想

```
用一个桶，匀速往里放令牌：

         ┌────────────────────────┐
         │        令牌桶           │
         │   🪙 🪙 🪙 🪙 🪙      │  ← 每秒放 10 个令牌（匀速）
         │   🪙 🪙 🪙 🪙        │
         └────────────────────────┘
                │               ↘
        请求来了 ↓              桶满了？→ 多出的令牌丢弃
        ┌──────────────┐
        │ 有令牌 → 放行 │  ← 拿走一个令牌
        │ 无令牌 → 拒绝 │
        └──────────────┘
```

### 用 Redis 实现令牌桶

不需要真的"放令牌"，而是用时间差计算最近生成了多少令牌：

```python
import time

def token_bucket_rate_limit(user_id, capacity=100, refill_rate=10):
    """
    capacity: 桶容量（最大积攒的请求数）
    refill_rate: 每秒补充的令牌数
    """
    key = f"rate:token:{user_id}"
    now = time.time()

    # 用 Hash 存储：上次检查时间、剩余令牌数
    data = redis.hgetall(key)
    if not data:
        # 第一次请求，初始化
        redis.hset(key, "tokens", capacity - 1)    # 消耗一个令牌
        redis.hset(key, "last_refill", now)
        redis.expire(key, 60)
        return True

    last_tokens = float(data.get(b"tokens", capacity))
    last_time = float(data.get(b"last_refill", now))

    # 计算从上次到现在应该补充多少令牌
    delta = now - last_time
    new_tokens = min(capacity, last_tokens + delta * refill_rate)

    if new_tokens >= 1:
        # 有令牌
        redis.hset(key, "tokens", new_tokens - 1)
        redis.hset(key, "last_refill", now)
        return True
    else:
        # 没令牌
        redis.hset(key, "tokens", 0)
        redis.hset(key, "last_refill", now)
        return False
```

### 令牌桶 vs 漏桶

```
令牌桶（Token Bucket）:
  特点: 允许一定的突发流量
  场景: 大部分 API 限流
  如果桶里积攒了 100 个令牌 → 瞬间可以处理 100 个请求

漏桶（Leaky Bucket）:
  特点: 强制平滑输出，不允许突发
  场景: 数据库写入、消息队列
  无论请求进来多快 → 出去的速度始终固定
```

---

## 6. 三种方案对比

| 特性 | 固定窗口 | 滑动窗口 | 令牌桶 |
|------|---------|---------|--------|
| 实现难度 | ★☆☆ 极简单 | ★★☆ 中等 | ★★★ 稍复杂 |
| 内存开销 | 极低（1个 key） | 较高（每个请求存 ZSET） | 低（1个 Hash） |
| 边界尖峰 | 有 | 无 | 无 |
| 允许突发 | 窗口内都允许 | 窗口内都允许 | 积攒令牌后允许 |
| 平滑控制 | 无 | 无 | 匀速放行 |
| 适用场景 | 粗略限流、非关键场景 | 精确限流、安全场景 | 流量整形、API 限流 |

---

## 7. 常见错误（新手必读）

### ❌ 错误 1：INCR 后忘记设过期时间

```python
# ❌ 只 INCR 不设过期
count = redis.incr(f"rate:{user_id}")
# 没有 expire！这个 key 永远不会重置 → 计数器只增不减

# ✅ 正确做法
count = redis.incr(f"rate:{user_id}")
if count == 1:
    redis.expire(f"rate:{user_id}", 60)
```

### ❌ 错误 2：固定窗口的边界时间不统一

```python
# ❌ 如果多台服务器的系统时间不一致...
# 服务器 A 的时间是 14:30:02 → 窗口 key = "rate:user:30"
# 服务器 B 的时间是 14:29:58 → 窗口 key = "rate:user:29"
# 两个窗口各自计数 → 限流失效

# ✅ 用统一的 Redis 时间（或 NTP 同步）
redis_time = redis.time()[0]   # 获取 Redis 服务器的时间
```

### ❌ 错误 3：窗口边界突刺

理解固定窗口的局限性，在需要精准限流的场景不要用固定窗口。

### ❌ 错误 4：滑动窗口的 ZSET 不设过期时间

```python
# 如果不设过期时间
redis.zadd(key, {str(time.time()): time.time()})
# 当用户不再请求时，这个 ZSET 永远留在 Redis 中 → 内存泄漏

# ✅ 每次操作都设置过期时间
redis.zadd(key, {str(time.time()): time.time()})
redis.expire(key, window_seconds + 10)   # 多给 10 秒容差
```

---

## 8. 你学到了什么

| 概念 | 一句话 |
|------|--------|
| 固定窗口 | INCR + EXPIRE，每分钟一个计数器，实现简单但有边界尖峰 |
| 滑动窗口 | ZSET 记录请求时间戳，精确限流，无边界尖峰 |
| 令牌桶 | 匀速放令牌，允许一定突发流量 |
| 漏桶 | 强制匀速输出，不允许突发 |
| 边界尖峰 | 固定窗口在窗口切换瞬间可以通过两倍流量 |
| 降精度优化 | 按秒聚合来降低 ZSET 的内存开销 |

---

## 9. 自己动手

1. **实现固定窗口限流**：用 INCR + EXPIRE 实现每分钟限制 5 次请求
2. **演示边界尖峰问题**：在窗口边界连续发请求，观察通过量超过限制
3. **实现滑动窗口限流**：用 ZSET 实现精确限流，验证无边界尖峰
4. **降低滑动窗口精度**：改为按秒聚合，对比内存开销差异
5. **实现令牌桶**：用 Hash 存储令牌数 + 时间戳，按时间差补充令牌
6. **对比三种方案**：在同样的限流条件下（100 次/分钟），观察三种方案的行为差异

---

> **下一章：[s11: 持久化（上）— RDB](../s11_rdb/)** — 怎么给黑板拍快照？
