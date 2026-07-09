# s17: Pub/Sub 与 Stream — 消息传递的两种方式

[s16](../s16_pipeline_tx/) → `s17` → [s18](../s18_internals/)
> *"Pub/Sub 是站在广场中央喊话，只有在场的人能听到。Stream 是在黑板上贴公告，后来的也能看到历史记录。"*
>
> **前提知识**: 理解 List 的阻塞操作 BLPOP/BRPOP（s04），理解基本的 key-value 操作。

---

## 1. 为什么需要消息传递？

到目前为止，你学到的所有 Redis 操作都有一个共同模式：**客户端主动去读**。

```
GET user:1001        → 你去黑板上看 user:1001 写了什么
LRANGE queue 0 -1    → 你去队列里看有哪些消息
ZRANGE leaderboard   → 你去看排行榜
```

这种模式叫 **Pull（拉）模式** — 你是主动请求的一方。

但现实中有很多场景需要相反的 **Push（推）模式**：

```
场景 1: 实时聊天
  用户 A 发了一条消息 → 用户 B 需要立刻收到
  用户 B 不可能每毫秒都去检查"有没有新消息"

场景 2: 订单状态通知
  支付系统处理完订单 → 通知发货系统 → 通知通知系统
  支付系统不需要知道"谁在听"，只管发就行

场景 3: 监控告警
  服务器 CPU 超过 90% → 告警系统需要立刻收到
  延迟 1 秒都可能是灾难
```

**Pub/Sub 和 Stream 就是为"推"模式设计的。** 生产者只管发消息，消费者被动接收（订阅）。

---

## 2. 在黑板模型下理解 Pub/Sub 和 Stream

### Pub/Sub = 对着广场喊话

```
┌─────────────────────────────────────────────┐
│             广场（Redis Pub/Sub）              │
│                                               │
│  主播： "重大消息！明天放假！"                 │
│                                               │
│  ┌─听众 A──┐  ┌─听众 B──┐  ┌─听众 C──┐      │
│  │ "收到！" │  │ "收到！" │  │ "收到！" │      │
│  └─────────┘  └─────────┘  └─────────┘      │
│                                               │
│  ┌─听众 D（来晚了）─┐                          │
│  │ "咦？刚才说什么？" │   ← 听不到了！          │
│  └─────────────────┘                          │
└─────────────────────────────────────────────┘
```

- 主播喊话 → 所有在听的人都能听到
- 中途来的听众听不到之前的内容
- 消息不保存，喊完就消失在空气中

### Stream = 黑板上贴公告栏

```
┌─────────────────────────────────────────────┐
│           公告栏（Redis Stream）               │
│                                               │
│  ┌──────────────────────────────────┐         │
│  │ ID: 123  内容: "明天放假"         │         │
│  │ ID: 124  内容: "后天加班"         │         │
│  │ ID: 125  内容: "下周团建"         │         │
│  └──────────────────────────────────┘         │
│                                               │
│ 新人小王来了 → 从头阅读公告栏 → 全都能看到！   │
└─────────────────────────────────────────────┘
```

- 每条消息都保存在黑板上（Stream 里）
- 后来的消费者可以看历史消息
- 消息消费后需要手动确认（ACK）才能标记为已处理

---

## 3. Pub/Sub 详解

### 基本命令

```bash
# 订阅者（Subscriber）— 在一个终端中
redis> SUBSCRIBE news:sports
Reading messages... (press Ctrl-C to quit)
1) "subscribe"
2) "news:sports"
3) (integer) 1

# 发布者（Publisher）— 在另一个终端中
redis> PUBLISH news:sports "火箭队赢了！"
(integer) 1    # 有 1 个订阅者收到了

# 订阅者的终端自动显示：
1) "message"
2) "news:sports"
3) "火箭队赢了！"
```

### 模式订阅：PSUBSCRIBE

```bash
# 订阅所有 news: 开头的频道
redis> PSUBSCRIBE news:*
Reading messages... (press Ctrl-C to quit)

# 发布到任意 news: 频道都能收到
redis> PUBLISH news:sports "体育新闻"
redis> PUBLISH news:tech "科技新闻"
redis> PUBLISH news:weather "天气预报"
```

### Pub/Sub 的工作流程

```
发布者                      Redis                     订阅者
  │                          │                          │
  │   PUBLISH channel msg    │                          │
  │ ──────────────────────→  │                          │
  │                          │ SUBSCRIBE channel        │
  │                          │ ←─────────────────────── │
  │                          │                          │
  │                          │ ───── message ─────────→ │
  │                          │                          │
  │   PUBLISH channel msg2   │                          │
  │ ──────────────────────→  │ ───── message2 ────────→ │
  │                          │                          │
```

### Pub/Sub 的特点

| 特性 | 说明 |
|------|------|
| **实时推送** | 消息一发布，所有在线订阅者立即收到 |
| **一对多** | 一个发布者，多个订阅者 |
| **频道模式** | 支持 PSUBSCRIBE 通配符订阅 |
| **不持久** | 消息不保存，离线就收不到 |
| **不确认** | 没有 ACK 机制，Redis 不关心你是否收到了 |
| **"火即忘"** | 没有订阅者时消息直接丢弃 |

---

## 4. Pub/Sub 的致命缺陷

Pub/Sub 虽然简单，但有三个严重缺陷：

### 缺陷 1：消息不持久

```bash
# 场景：订阅者还没上线，消息就已经发布了
# 订阅者在 10:00 才 SUBSCRIBE
# 但消息在 09:55 就 PUBLISH 了

redis> PUBLISH alerts "服务器挂了！"    # 09:55 发布
(integer) 0                           # 0 个订阅者 → 消息直接丢弃！

# 10:00 订阅者上线
redis> SUBSCRIBE alerts
# ⚠ 消息已经丢了！根本不知道 09:55 服务器挂过
```

### 缺陷 2：没有 ACK 确认

```bash
# 订阅者收到了消息，但处理过程中崩溃了
# Redis 不会重发——它认为"你已经收到了"

redis> PUBLISH orders "新订单 #1001"
(integer) 1    # 订阅者 1 收到了

# 订阅者 1 的处理逻辑抛异常了
# 这条订单信息永远丢失了！
```

### 缺陷 3：缓冲区溢出

```
如果发布者速度 > 订阅者处理速度：
  - Redis 为每个订阅者维护一个输出缓冲区
  - 缓冲区满了 → 连接被强制断开
  - 订阅者重新连接后 → 中间的消息全部丢失
```

> **结论**：Pub/Sub 适合对可靠性要求不高的场景（如实时日志广播），不适合做消息队列。

---

## 5. Stream — Redis 的可靠消息队列

Stream 是 Redis 5.0 引入的数据结构，专门用来弥补 Pub/Sub 的缺陷。

### 5.1 XADD — 往 Stream 里加消息

```bash
redis> XADD mystream * sensor-id 1234 temperature 19.8
"1712300000000-0"    ← Redis 自动生成的消息 ID（时间戳-序号）
```

`*` 告诉 Redis 自动生成 ID。ID 的格式是 `时间戳毫秒-序号`。

### 5.2 XREAD — 从 Stream 里读消息

```bash
# 从 Stream 的开头读取
redis> XREAD COUNT 10 STREAMS mystream 0
1) 1) "mystream"
   2) 1) 1) "1712300000000-0"
         2) 1) "sensor-id"
            2) "1234"
            3) "temperature"
            4) "19.8"

# 只读最新的消息（阻塞等待）
redis> XREAD BLOCK 0 STREAMS mystream $
```

### 5.3 在黑板模型下理解 Stream

```
Stream = 黑板上的一条「滚动公告栏」：

  ┌──────────┬──────────┬──────────┬──────────┐
  │ msg-001  │ msg-002  │ msg-003  │ msg-004  │
  │ "a"      │ "b"      │ "c"      │ "d"      │
  └──────────┴──────────┴──────────┴──────────┘
     ↑                               ↑
  最早的消息                        最新的消息

  读取的方式：
  - XREAD COUNT 2 STREAMS mystream 0
    → 从 ID=0 开始读 2 条 → msg-001, msg-002

  - XREAD COUNT 2 STREAMS mystream msg-002
    → 从 msg-002 之后读 2 条 → msg-003, msg-004
```

### 5.4 消费组（Consumer Group）

消费组允许多个消费者**分摊**处理 Stream 中的消息：

```
Stream: [msg1] [msg2] [msg3] [msg4] [msg5] [msg6]

消费组 "workers"（3 个消费者）:
  ┌───────────────────────────────────────────┐
  │  Consumer A: 处理 msg1, msg4              │
  │  Consumer B: 处理 msg2, msg5              │
  │  Consumer C: 处理 msg3, msg6              │
  │                                            │
  │  每条消息只分配给一个消费者！               │
  └───────────────────────────────────────────┘
```

```bash
# 创建消费组
redis> XGROUP CREATE mystream mygroup $

# 消费者从消费组中读取（未处理的消息）
redis> XREADGROUP GROUP mygroup consumer1 COUNT 1 STREAMS mystream >

# 处理完后确认
redis> XACK mystream mygroup 1712300000000-0
```

### 5.5 Stream 的核心特性

| 特性 | 说明 |
|------|------|
| **消息持久化** | 消息保存在 Redis 内存中（可配合 RDB/AOF 持久化） |
| **消息 ID 自动生成** | 基于时间戳，天然有序 |
| **消费组** | 多消费者分摊处理消息 |
| **ACK 确认** | 消费后必须 ACK，否则消息一直存在 |
| **消息回溯** | 可以从任意 ID 开始重新读取历史消息 |
| **范围查询** | 可以按时间范围查询消息 |
| **阻塞读取** | 支持 BLOCK 参数，没有消息时阻塞等待 |

---

## 6. Pub/Sub vs List vs Stream 对比表

| 特性 | Pub/Sub | List (BRPOP) | Stream |
|------|---------|-------------|--------|
| **消息持久化** | ❌ 不持久 | ✅ 持久 | ✅ 持久 |
| **ACK 确认** | ❌ 无 | ❌ 无 | ✅ 有 |
| **消费组** | ❌ 无 | ❌ 无 | ✅ 支持 |
| **消息回溯** | ❌ 不能 | ❌ 消费即删 | ✅ 可以 |
| **实时性** | ✅ 极高 | ✅ 高 | ✅ 高 |
| **一对多** | ✅ 广播 | ❌ 竞争消费 | ✅ 两者都支持 |
| **复杂度** | ⭐ 简单 | ⭐ 简单 | ⭐⭐⭐ 较复杂 |
| **适用场景** | 实时广播、日志流 | 简单任务队列 | 可靠消息队列、事件溯源 |

---

## 7. 常见错误（新手必读）

### ❌ 错误 1：用 Pub/Sub 做消息队列

```python
# ❌ 错误：Pub/Sub 不保证消息送达
import redis
r = redis.Redis()
r.publish("orders", "新订单 #1001")
# 如果这时候没有订阅者 → 消息就丢了
```

**应该用 Stream**：

```python
r.xadd("orders", {"order_id": "1001"})
# 消息存入 Stream，消费者不在线也不会丢
```

### ❌ 错误 2：Stream 消费者忘记 ACK

```python
# ❌ 错误：处理完不 ACK
def process_orders():
    while True:
        msgs = r.xreadgroup("orders_group", "consumer1",
                            {"orders": ">"}, count=1, block=5000)
        for msg_id, data in msgs[0][1]:
            process(data)          # 处理消息
            # 忘记 XACK！→ 下次重启，消息还在待处理列表
```

**正确做法**：

```python
def process_orders():
    while True:
        msgs = r.xreadgroup("orders_group", "consumer1",
                            {"orders": ">"}, count=1, block=5000)
        for msg_id, data in msgs[0][1]:
            process(data)
            r.xack("orders", "orders_group", msg_id)  # ✅ 别忘了 ACK
```

### ❌ 错误 3：消费组名搞混

```bash
# 不同业务应该用不同的消费组
XGROUP CREATE order_stream payment_group $    # 支付组
XGROUP CREATE order_stream notification_group $  # 通知组

# payment_group 和 notification_group 各自独立
# 订单消息会同时发给两个组！
```

### ❌ 错误 4：Stream 长度无限增长

```python
# Stream 消息不会自动删除！
r.xadd("sensor:data", {"temp": "25.3"})
r.xadd("sensor:data", {"temp": "25.4"})
# ... 100 万条后，内存暴涨！

# ✅ 使用 MAXLEN 限制长度
r.xadd("sensor:data", {"temp": "25.5"}, maxlen=1000)
# 只保留最近 1000 条，旧的自动裁剪
```

---

## 8. 你学到了什么

| 概念 | 一句话 |
|------|--------|
| Pub/Sub = 广播 | 发布 → 所有在线订阅者立刻收到，离线就错过 |
| PUBLISH / SUBSCRIBE | 发布消息 / 订阅频道 |
| PSUBSCRIBE | 订阅匹配模式的多个频道 |
| Pub/Sub 的缺陷 | 不持久、无 ACK、缓冲区溢出 |
| Stream | 持久化消息队列，支持消费组和 ACK |
| XADD / XREAD | 写消息 / 读消息 |
| XREADGROUP | 从消费组读消息（消息分摊） |
| XACK | 确认消息已处理 |
| 消费组 | 多个消费者分摊处理消息 |

---

## 9. 自己动手

1. **Pub/Sub 体验**：开两个 redis-cli 窗口，一个执行 `SUBSCRIBE chat`，另一个执行 `PUBLISH chat "你好"`，观察消息实时到达
2. **PSUBSCRIBE 练习**：订阅所有 `order:*` 频道，然后发布到 `order:new`、`order:cancel`、`order:ship`
3. **Stream 体验**：用 `XADD mystream * name "Alice" age 30` 添加几条消息，用 `XREAD` 读取
4. **消费组实践**：创建消费组，启动两个消费者，观察消息是否被均匀分摊
5. **ACK 实验**：不 ACK 一条消息，然后重新读取——看看消息是不是还在待处理列表
6. **对比 Pub/Sub 和 Stream**：先发布 Pub/Sub 消息，再开订阅者（消息丢了）。先 XADD 到 Stream，再开消费者读（消息还在）

---

> **下一章：[s18: 深入原理](../s18_internals/)** — RESP 协议、内存编码、单线程事件循环
