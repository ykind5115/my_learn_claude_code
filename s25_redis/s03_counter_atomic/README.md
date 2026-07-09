# s03: 计数器与原子操作 — 只有一个人能在同一个位置写字

[s02](../s02_expiration/) → `s03` → [s04](../s04_list/) → ... → s18
> *"INCR 不是 +1，是在黑板上把数字改写成新数字，而且只有一个人能改。"*
>
> **前提知识**: 做过 s01（SET/GET/DEL）。理解 s02 的过期概念。

---

## 1. 为什么需要原子操作？

先看一个经典问题：**并发 +1**

假设你在写一个网站计数器——用户每访问一次，`page_views` 加 1。

用 Python 实现大概是这样的：

```python
# ❌ 有并发问题的代码
count = int(client.get("page_views"))  # ① 读出
count += 1                             # ② 计算
client.set("page_views", str(count))   # ③ 写回
```

如果两个用户**同时访问**：

```
时间 →——————————————————————————————————————→

用户 A:  读出(0)  →  计算(0+1)  →  写回(1)
用户 B:  读出(0)  →  计算(0+1)  →  写回(1)
                                        ↑
                              最终结果是 1，应该是 2！
```

**因为「读 → 改 → 写」不是原子操作**——A 和 B 同时读到了 0，各自加 1 后写回 1，结果丢了 1 次访问。

### Redis 怎么解决？

```python
# ✅ 一行代码解决并发问题
client.incr("page_views")  # 原子 +1
```

`INCR` 是原子操作——"读出 → 加 1 → 写回"这三步在 Redis 内部一次性完成，**其他请求插不进来**。

---

## 2. 在黑板模型下理解原子操作

还记得 s00 的共享黑板模型吗？

```
普通操作（GET + 计算 + SET）：
────────────────────────────────────────────
  客户端 1:   看黑板 → "0" → 改成 "1" → 写回去
  客户端 2:          看黑板 → "0" → 改成 "1" → 写回去
                               ↑ 两个人都看到 0，
                                 导致最终是 1 而不是 2


原子操作（INCR）：
────────────────────────────────────────────
  客户端 1:   "把 page_views 加 1"（瞬间完成）
  客户端 2:   "把 page_views 加 1"（等 1 完成后执行）

              Redis 内部串行执行：
              ① 1 说"加 1" → 黑板 0 → 1
              ② 2 说"加 1" → 黑板 1 → 2
```

**关键理解**：Redis 是单线程处理命令的。

- 同一时刻，最多只有一个命令在执行
- 两个 `INCR` 不可能同时执行——它们是串行的
- 所以 `INCR` 天然是线程安全的

类比黑板上写字：**黑板前只能站一个人写。你写的时候别人必须等着。写完一个命令，下一个人再写。**

---

## 3. 怎么做 — 逐行解释

### 3.1 INCR — 黑板上的计数器加 1

```bash
redis> SET visits "0"
redis> INCR visits
(integer) 1      # 返回加 1 后的值
redis> INCR visits
(integer) 2
redis> INCR visits
(integer) 3
```

**如果 key 不存在呢？**

```bash
redis> INCR new_visits
(integer) 1      # 自动创建 key，从 0 开始加 1
```

`INCR` 会自动创建一个不存在的 key，默认值为 0，然后加 1。**不需要先 SET**。

### 3.2 DECR — 黑板上的计数器减 1

```bash
redis> DECR visits
(integer) 2
redis> DECR visits
(integer) 1
redis> DECR visits
(integer) 0
redis> DECR visits
(integer) -1     # 可以减到负数
```

### 3.3 INCRBY — 加任意数值

```bash
redis> SET score "100"
redis> INCRBY score 50
(integer) 150     # 加 50
redis> INCRBY score -30
(integer) 120     # 加负数 = 减
```

`INCRBY` 比连续调 `INCR` 50 次高效多了——一次网络往返搞定。

### 3.4 INCRBYFLOAT — 浮点数增量

```bash
redis> SET price "99.9"
redis> INCRBYFLOAT price 0.1
"100.0"
redis> INCRBYFLOAT price -9.99
"90.01"
```

**注意**：

- `INCRBYFLOAT` 返回的是字符串（不是浮点数）
- Redis 内部用双精度浮点（double）计算，可能有精度问题
- 金融场景建议用整数（存"分"而不是"元"）

### 3.5 SETNX — 如果不存在才写（首次写入保护）

```bash
redis> SETNX lock "1"
(integer) 1      # 设置成功 — 之前没有这个 key
redis> SETNX lock "1"
(integer) 0      # 设置失败 — key 已经存在了
```

`SETNX` = **SET** if **N**ot E**X**ists。

翻译成黑板动作：没有人写过这一行，你才能写。如果有人写过了，你就写不上去。

这是**分布式锁**的基础（s09 会深入展开）。

### 3.6 GETSET — 写新值，返回旧值

```bash
redis> SET counter "100"
redis> GETSET counter "200"
"100"            # 返回旧值
redis> GET counter
"200"            # 新值已生效
```

`GETSET` = 把黑板上的一行改成新内容，同时告诉你原来写了什么。

原子地完成"读取旧值 + 写入新值"两个操作。常用于计数器重置、状态切换等场景。

### 3.7 SET NX + EX — 带过期的首次写入

```bash
redis> SET lock "value" NX EX 10
OK               # 成功获取锁，10 秒后自动释放
redis> SET lock "value" NX EX 10
(nil)            # 锁还在，获取失败
```

这是分布式锁最经典的形式——`SET key value NX EX seconds` 一次性完成：
- `NX` = 只有 key 不存在才写入（首次写入保护）
- `EX 10` = 10 秒后自动过期（防止死锁）

---

## 4. 再做两次练习，感受原子性

### 练习 A：模拟并发场景

用两个终端同时跑：

```bash
# 终端 1
redis> INCR page_views
(integer) 1

# 终端 2（同时）
redis> INCR page_views
(integer) 2    # 不会出现两个都读到 0 的情况
```

试试用 GET + SET 模拟同样的场景，看看会不会丢数据。

### 练习 B：实现一个"首次运行"检查

```bash
redis> SETNX has_run "yes"
(integer) 1    # 第一次运行

# 第二次运行
redis> SETNX has_run "yes"
(integer) 0    # 已经运行过了，跳过
```

---

## 5. Redis 单线程模型与原子性

这是 Redis 面试最高频的问题之一。

### 5.1 为什么 Redis 是单线程的？

Redis 的核心是一个**单线程事件循环**（single-threaded event loop）：

```
            ┌─────────────────────┐
请求 1 ───→ │                     │
请求 2 ───→ │  单线程事件循环      │ ───→ 串行执行每个命令
请求 3 ───→ │  (一个线程)          │
            └─────────────────────┘
```

- 所有客户端请求到达后排队
- 同一时刻只处理一个命令
- 一个命令执行完，再处理下一个

### 5.2 单线程 = 天然原子

因为命令是串行执行的：

```python
# 多线程环境中，这三个操作之间可能有其他线程插进来
count = get("key")   # 可能另一个线程正在 SET 同一个 key！
count += 1
set("key", count)
```

但在 Redis 里：

```python
incr("key")  # 内部实现：在 Redis 服务器内部完成读 → 改 → 写
             # 这个过程没有其他命令可以插进来
             # 因为只有一个线程在处理所有命令
```

### 5.3 为什么单线程还这么快？

| 原因 | 说明 |
|------|------|
| **纯内存操作** | 数据全在内存，读写是纳秒级的 |
| **避免了锁开销** | 单线程没有上下文切换和锁竞争 |
| **I/O 多路复用** | 一个线程处理多个连接，epoll/kqueue 高效 |
| **数据结构优化** | 每种数据结构都有专门的内存编码 |

> **注意**：Redis 6.0+ 在网络 I/O 上用了多线程（多线程处理网络读写），但**命令执行仍然是单线程**的。这意味着原子性保证不变。

---

## 6. 常见错误（新手必读）

### ❌ 错误 1：对非整数用 INCR

```bash
redis> SET name "hello"
redis> INCR name
(error) ERR value is not an integer or out of range
```

`INCR` 只能在 String 类型且内容为整数的 key 上使用。如果存的是 "hello" 或 "3.14"，都会报错。

### ❌ 错误 2：用 GET + SET 代替 INCR

```python
# ❌ 并发不安全
count = int(client.get("counter"))
client.set("counter", count + 1)

# ✅ 原子操作
client.incr("counter")
```

GET + SET 之间可能插入其他操作。永远用 INCR 做加法。

### ❌ 错误 3：忘记 INCR 返回的是加完后的值

```python
client.incr("counter")  # 假设 counter 当前是 10
# INCR 返回 11
# 但如果写:
result = client.incr("counter")
print(result)  # 11（是加完后的值，不是旧值）
```

### ❌ 错误 4：INCR 的最大值

Redis 的 String 最大能存 512 MB。但如果存的数字太大，Redis 内部会从整数编码转为字符串编码。实际上你不太可能遇到上限——10^18 次方以内的整数都是高效存储的。

### ❌ 错误 5：认为 SETNX 是 SET + EXPIRE 一步到位

```bash
# ❌ 隐患：SETNX 只保证首次写入，但不保证过期
SETNX lock "value"
# 如果程序崩溃了，锁永远不释放！
```

安全做法：

```bash
# ✅ SET NX EX 一步到位
SET lock "value" NX EX 10
```

这个命令是 Redis 官方推荐的分布式锁实现方式。

---

## 7. 你学到了什么

| 概念 | 你做了什么 |
|------|----------|
| `INCR` | 原子加 1——即使 1000 个并发请求也不会丢数据 |
| `DECR` | 原子减 1 |
| `INCRBY` | 原子加任意整数 |
| `INCRBYFLOAT` | 原子加浮点数 |
| `SETNX` | 只有 key 不存在时才写入——首次写入保护 |
| `GETSET` | 写新值，同时返回旧值 |
| 原子性 | Redis 单线程处理命令，每个命令不可分割 |
| `SET NX EX` | 原子地实现"不存在才写 + 自动过期"——分布式锁基础 |

---

## 8. 自己动手

1. **INCR 连击**：`INCR page_views` 连续 5 次，看每次返回值
2. **DECR 到负数**：从 0 开始 DECR，确认 Redis 允许负数
3. **INCRBYFLOAT**：`SET pi "3.14"`，然后 `INCRBYFLOAT pi 0.01` 看结果
4. **SETNX 体验**：同一个 key 跑两次 SETNX，确认第二次返回 0
5. **模拟并发问题**：用两个终端同时 `GET counter` → 计算 → `SET counter`，看会不会丢数据
6. **运行 code.py**：`python s25_redis/s03_counter_atomic/code.py`，亲眼看到 INCR 在多线程下依然准确

---

> **下一章：[s04: List — 队列与栈](../s04_list/)** — 学会用 List 实现消息队列和最新消息列表
