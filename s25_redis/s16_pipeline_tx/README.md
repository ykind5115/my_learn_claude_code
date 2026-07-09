# s16: Pipeline 与事务 — 批量操作与原子执行

[s15](../s15_cluster/) → `s16` → [s17](../s17_pubsub_stream/) → s18
> *"你不需要在黑板前跑 100 次，把 100 个要写的内容列成清单，一次递过去。"*
>
> **前提知识**: 会用 SET/GET（s01），理解原子操作 INCR（s03），理解 Redis 是 TCP 网络请求（每个命令一次往返）。

---

## 1. 为什么需要 Pipeline？

Redis 是一个 TCP 服务。你的每一个命令，都需要经历一次完整的网络往返：

```
客户端                  Redis 服务端
  │                        │
  │──── SET name "小明" ──→│
  │←──────── OK ──────────│  一个 RTT (Round-Trip Time)
  │                        │
  │──── SET age "25" ─────→│
  │←──────── OK ──────────│  又一个 RTT
  │                        │
  │──── INCR counter ─────→│
  │←──────── 1 ───────────│  再一个 RTT
  │                        │
```

**如果一次操作需要执行 100 个命令，就是 100 个 RTT。** 即使每个 RTT 只有 1ms（局域网），100 个就是 100ms。如果 Redis 和客户端在不同机房（RTT 30~50ms），100 个命令就是 3~5 秒！

**Pipeline 的核心思想**：把多个命令打包在一起，一次性发送，一次性接收所有回复。

```
客户端                  Redis 服务端
  │                        │
  │──[命令1, 命令2, ...]──→│  一次发送
  │←───[回复1, 回复2,...]─│  一次接收
  │                        │
```

**瓶颈从「N 个 RTT」变成了「1 个 RTT」。**

---

## 2. 在黑板模型下理解 Pipeline

回到我们的共享黑板模型：

```
普通方式 — 逐条写:
  ① 在黑板上写 "name: 小明" → 等笔放下 → 再去拿笔写
  ② 在黑板上写 "age: 25"   → 等笔放下 → 再去拿笔写
  ③ 在黑板上写 "city: 北京" → 等笔放下
  效率低！你每次都要"走过去→写→走回来"。

Pipeline — 清单一次递:
  ① 在便签上列好清单:
     1. SET name "小明"
     2. SET age "25"
     3. SET city "北京"
  ② 把便签一次递给 Redis
  ③ Redis 一次性执行完，把结果一起给你
  效率高！一次递过去就行。
```

> **关键理解**：Pipeline 不是事务。它只是在传输层面做了优化——把多个请求合并为一个 TCP 包发送。Redis 仍然是逐个执行这些命令的，顺序不变。

---

## 3. Pipeline vs 逐个发送（性能对比）

### 什么时候 Pipeline 效果显著？

| 场景 | 逐个发送 | Pipeline | 提升倍数 |
|------|---------|----------|---------|
| 局域网 (RTT ~0.5ms)，10 个命令 | ~5ms | ~0.5ms | 10x |
| 跨机房 (RTT ~30ms)，100 个命令 | ~3000ms | ~30ms | 100x |
| 同机器 (RTT ~0.1ms)，1000 个命令 | ~100ms | ~0.2ms | 500x |

Pipeline 的**提升幅度由 RTT 决定**。延迟越高，Pipeline 的效果越明显。

### Pipeline 的注意事项

```
Pipeline 返回的结果是有序的 —— 顺序和命令发送顺序一致。

命令顺序:  [SET a 1] [GET a] [SET b 2] [GET b]
返回顺序:  [OK]     ["1"]   [OK]     ["2"]
            ↑ 第 1 个命令的结果
                    ↑ 第 2 个命令的结果
```

**Pipeline 不是原子性的** — 在 Pipeline 执行过程中，Redis 可能执行其他客户端的命令。

---

## 4. MULTI/EXEC 事务

如果 Pipeline 只是「批量发送」，那事务就是「打包执行」。

### 事务的工作方式

```bash
redis> MULTI
OK           ← Redis 说：好的，开始收集命令

redis> SET account:1001 100
QUEUED       ← Redis 说：收到，但先不执行，放进队列

redis> INCR counter
QUEUED       ← Redis 说：收到，放进队列

redis> EXEC
1) OK        ← 现在一次性执行所有命令！
2) (integer) 1
```

### 事务的三个阶段

```
MULTI        →  ① 开启事务（Redis 进入事务模式）
命令1...      →  ② 命令入队（Redis 不执行，只排队）
命令2...
命令3...
EXEC         →  ③ 执行队列中的所有命令（一次性、无中断）
```

### 事务在黑板模型下的理解

```
普通写（非事务）:
  ① 在黑板上写 "counter = 1"
  ② 另一个人走过来写 "counter = 99"    ← 中间插入了！
  ③ 在黑板上写 "flag = done"

事务方式（MULTI/EXEC）:
  ① 对黑板说："我要开始写了，别人别打扰"
  ② 写下 "counter = 1"
  ③ 写下 "flag = done"
  ④ 对黑板说："我写完了"
  ①~③ 之间不会被插入其他操作！
```

### 事务的关键特性

| 特性 | 说明 |
|------|------|
| **原子性** | 事务中的所有命令要么全部执行，要么全部不执行 |
| **隔离性** | 事务执行期间，其他客户端的命令不会被插入 |
| **非回滚** | 如果事务中的某个命令执行失败，之前的命令不会回滚 |
| **不阻塞** | 事务中的命令仍然在事件循环中执行，只是不被其他命令中断 |

> **非常重要**：Redis 事务**不支持回滚**。如果 EXEC 后某个命令执行出错，正确的命令不会回滚。这和关系型数据库的事务不同。

---

## 5. WATCH 乐观锁

WATCH 是一种**乐观锁（Optimistic Locking）**机制。它的作用是：

> "我想修改某个 key，但如果在我修改之前，别人已经改了它，那我的事务就不执行。"

### 典型场景：转账

```
假设 account:A 有 100 元，account:B 有 50 元。
你要把 A 的 30 元转给 B。

正常流程:
  ① GET account:A → 100
  ② GET account:B → 50
  ③ 计算: A = 100 - 30 = 70
         B = 50 + 30 = 80
  ④ SET account:A 70
  ⑤ SET account:B 80

并发问题:
  ① 你 GET account:A → 100
  ② 另一个人 GET account:A → 100
  ③ 你 SET account:A 70
  ④ 另一个人 SET account:A 90  ← 覆盖了你的结果！
  ⑤ 你 SET account:B 80
```

### WATCH 解决并发问题

```
WATCH account:A           ← ① 监视 A
GET account:A → 100       ← ② 读当前值

--- 此时其他人修改了 account:A ---

MULTI                     ← ③ 开启事务
SET account:A 70
SET account:B 80
EXEC                      ← ④ 执行事务 → (nil)！
                              因为 WATCH 发现 account:A 被改了
                              事务被放弃，什么都不做
```

### WATCH 在黑板模型下的理解

```
WATCH = 在黑板前盯着某一行说：
  "如果在我写之前，有人改了这一行，我就不写了。"

  ① WATCH counter          → "我盯着 counter 这一行"
  ② GET counter → 10       → "看到了，是 10"
  
  ③ 有人 SET counter 99    → "counter 被改了！"

  ④ MULTI
     SET counter 11        → 准备好新值
  ⑤ EXEC → (nil)           → "被人改过了，我不写了"
```

### WATCH 之后必须 UNWATCH？

- 如果事务执行成功（EXEC），WATCH 自动取消
- 如果不想执行事务了，可以用 `UNWATCH` 取消监视
- 连接断开后 WATCH 也会自动取消

---

## 6. Lua 脚本简介（EVAL）

虽然 Pipeline 和事务已经很强大，但有时候你需要在 Redis 内部执行更复杂的逻辑——比如：

```
需求：检查一个 key 是否存在，如果存在就更新，否则什么都不做。

普通方式（两条命令，不原子）:
  EXISTS key → 返回 1
  SET key value → 如果中间有别的客户端操作了 key，就有问题

事务方式（原子，但不能做条件判断）:
  MULTI
  SET key value
  EXEC
  → 但事务不能做 IF-THEN-ELSE 逻辑！
```

### Lua 脚本：在 Redis 内部运行代码

```bash
redis> EVAL "return redis.call('SET', KEYS[1], ARGV[1])" 1 name "小明"
OK
```

这是一个简单的例子。更复杂的脚本可以包含条件判断、循环等：

```bash
redis> EVAL "
  local val = redis.call('GET', KEYS[1])
  if val == false then
    return 'NOT_EXISTS'
  else
    redis.call('SET', KEYS[1], ARGV[1])
    return 'UPDATED'
  end
" 1 counter 100
```

### Lua 脚本的优点

| 特性 | 说明 |
|------|------|
| **原子性** | 脚本执行期间不会被其他命令中断 |
| **减少网络** | 复杂的逻辑一次发送，一次返回 |
| **可复用** | 可以用 `SCRIPT LOAD` + `EVALSHA` 缓存脚本 |
| **条件判断** | 支持 if/else、循环等流程控制 |

### Lua 脚本的注意事项

```
⚠ 脚本应该尽量简短 — 长时间运行的 Lua 脚本会阻塞 Redis
⚠ 脚本执行期间，所有其他客户端都被阻塞
⚠ 不要在脚本中执行可能会很慢的操作（如 KEYS *）
⚠ 脚本产生的错误不会回滚前面已经执行的操作
```

---

## 7. 常见错误（新手必读）

### ❌ 错误 1：Pipeline 返回顺序搞混

```python
# 你以为返回顺序和发送顺序不同？
pipeline = client.pipeline()
pipeline.set("a", 1)
pipeline.get("a")
pipeline.set("b", 2)
pipeline.get("b")
results = pipeline.execute()
# results[0] = SET a 的结果
# results[1] = GET a 的结果  ← 顺序和命令顺序一致！
# results[2] = SET b 的结果
# results[3] = GET b 的结果
```

### ❌ 错误 2：以为事务会回滚

```bash
MULTI
SET a "hello"
INCR a          ← 错误！a 是字符串，不能 INCR
EXEC
1) OK
2) (error) ERR value is not an integer

GET a
"hello"         ← a 被 SET 成功，没有回滚！
```

Redis 事务不会回滚。INCR 失败不会让 SET 也撤销。

### ❌ 错误 3：WATCH 后忘记处理失败

```python
# WATCH 后 EXEC 返回 None（事务被放弃）
# 但没有重试机制！！！
client.watch("key")
val = client.get("key")
pipe = client.pipeline(transaction=True)
pipe.multi()
pipe.set("key", int(val) + 1)
result = pipe.execute()   # 如果返回 None，表示事务失败

# 正确做法：检查结果，需要时重试
if result is None:
    # 说明 key 被改了，需要重试整个操作
    retry_logic()
```

### ❌ 错误 4：事务中混用 WATCH 和 MULTI 的顺序

```bash
WATCH key       ← ✅ 正确：WATCH 必须在 MULTI 之前
MULTI
SET key value
EXEC
```

```bash
MULTI
WATCH key       ← ❌ 错误：WATCH 不能在事务内部使用
SET key value
EXEC
```

### ❌ 错误 5：认为 Lua 脚本是银弹

Lua 脚本虽然强大，但：
- 过度使用会使 Redis 变成"脚本执行器"，失去了简单的命令式模型
- 调试困难（没有 Redis 的 Lua 调试器）
- 如果脚本中有 bug，会导致生产事故

---

## 8. 你学到了什么

| 概念 | 理解 | 核心命令 |
|------|------|----------|
| Pipeline | 批量发送命令，减少网络往返 | `pipeline()` / `.execute()` |
| 事务 | 一组命令打包执行，中间不插入其他命令 | `MULTI` / `EXEC` / `DISCARD` |
| WATCH | 乐观锁：key 被改过就不执行事务 | `WATCH` / `UNWATCH` |
| Lua 脚本 | 在 Redis 内部执行复杂逻辑，原子性 | `EVAL` / `SCRIPT LOAD` / `EVALSHA` |
| Pipeline ≠ 事务 | Pipeline 优化网络，事务保证原子执行 | — |

---

## 9. 自己动手

1. **Pipeline 实践**：写一个脚本，往 Redis 里写入 1000 个 key，用 Pipeline 和不用 Pipeline 分别计时，对比差距
2. **事务原子性**：在 redis-cli 中开两个窗口。窗口 A：MULTI → INCR counter → EXEC。窗口 B：在 A 的 EXEC 之前执行 SET counter 99。观察结果
3. **WATCH 乐观锁**：在 redis-cli 中开两个窗口。窗口 A：WATCH stock → GET stock → MULTI。窗口 B 修改 stock。窗口 A 执行 EXEC，看是否返回 nil
4. **Lua 脚本**：写一个 Lua 脚本实现"检查并设置"（check-and-set），用 EVAL 执行
5. **WATCH + 重试**：写一个 Python 函数，用 WATCH 实现原子 INCR，如果事务被放弃就自动重试
6. **对比 Pipeline 和事务**：同样 5 个命令，分别用 Pipeline 和 MULTI/EXEC 执行，观察行为差异（Pipeline 在发送后可以插入其他命令，事务不行）

---

> **下一章：[s17: Pub/Sub 与 Stream](../s17_pubsub_stream/)** — 发布订阅与可靠消息队列
