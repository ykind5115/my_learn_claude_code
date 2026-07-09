# s04: List — 队列与栈

[s03](../s03_counter_atomic/) → `s04` → [s05](../s05_hash/) → ... → s18
> *"List 不是数组，是黑板上的一条传送带。你从左边推入，从右边弹出——天然的消息队列。"*
>
> **前提知识**: 做过 s01~s03（SET/GET/DEL, EXPIRE, INCR）。理解「共享黑板」模型。

---

## 1. 为什么需要 List？

先想一个真实场景：你的网站需要**异步发送邮件**。

用户注册后，后端需要发送一封欢迎邮件。如果直接在请求里发邮件，用户要等 3 秒才看到「注册成功」页面。

更好的做法：用户注册 → 把「发邮件任务」写入队列 → 立即返回「注册成功」 → 后台 worker 从队列取出任务慢慢发。

**没有 List 的世界**：

```python
# ❌ 用 String 模拟队列 — 极度痛苦
task_list = client.get("email_queue")  # 读出整个 JSON 数组
tasks = json.loads(task_list)          # 反序列化
tasks.append(new_task)                 # 追加
client.set("email_queue", json.dumps(tasks))  # 序列化写回
```

又慢又麻烦——每次都要读全部、写全部。

**用 List 的世界**：

```python
# ✅ 一行代码入队
client.lpush("email_queue", new_task)

# ✅ 一行代码出队
task = client.brpop("email_queue", timeout=5)
```

### List 解决了什么？

| 问题 | String 方案 | List 方案 |
|------|-----------|----------|
| 「队列尾部追加」 | 读取整个 JSON → 追加 → 写回 | `RPUSH` — 一行代码 |
| 「从队列头部取出」 | 同上 | `LPOP` — 一行代码 |
| 「只保留最新 100 条」 | 要手动截断 | `LTRIM` — 一行代码 |
| 「队列为空时等待」 | 轮询，浪费 CPU | `BLPOP` / `BRPOP` — 阻塞等待 |

> **List 的核心价值：两端操作，O(1) 时间复杂度。**
> 不需要读写全部元素——只在两端操作，快且省内存。

---

## 2. 黑板模型下的 List

### 传送带

把 List 想象成黑板上的一条**传送带**：

```
                      LPUSH              RPUSH
                      (左边推入)          (右边推入)
                         │                  │
                         ▼                  ▼
                    ┌──────────────────────────┐
              LPOP ←│  │  │  │  │  │  │  │  │  │→ RPOP
              (左边弹出)   有序元素               (右边弹出)
                    └──────────────────────────┘
```

- **左端 = 头部**（最新加入的一端）
- **右端 = 尾部**（最早加入的一端）
- 可以在两端推入（push）或弹出（pop）
- 元素**有序**且**可重复**

### 四种传送带用法

```
栈（Stack）— 后进先出（LIFO）:
  LPUSH + LPOP = 像一个叠盘子的弹簧——后放上去的先取走

队列（Queue）— 先进先出（FIFO）:
  RPUSH + LPOP = 像排队——先来的先服务

阻塞队列（Blocking Queue）:
  RPUSH + BLPOP = 队列为空时，等着，不轮询

裁剪列表（Cap List）:
  LPUSH + LTRIM = 只保留最新 N 条，自动丢弃旧数据
```

### 和 Python list 的区别

| | Python list | Redis List |
|--|-----------|-----------|
| **存储位置** | 进程内存 | 共享黑板（所有进程可见） |
| **两端操作** | `pop(0)` 是 O(n) | `LPOP` / `RPOP` 是 O(1) |
| **阻塞等待** | 没有内置支持 | `BLPOP` / `BRPOP` 原生支持 |
| **自动裁剪** | 没有 | `LTRIM` 原生支持 |

---

## 3. 怎么做 — 逐行解释

### 3.1 LPUSH + RPUSH — 从左右两端推入

List 的核心操作：推入（push）和弹出（pop）。

```bash
redis> LPUSH queue "任务A"    # 从左边推入
(integer) 1                    # 返回列表长度
redis> LPUSH queue "任务B"
(integer) 2
redis> RPUSH queue "任务C"    # 从右边推入
(integer) 3
```

现在的黑板：

```
queue: [ "任务B", "任务A", "任务C" ]  (3 items)
          ↑                ↑
        LPUSH"任务B"      RPUSH"任务C"
        最先推入"任务A"在中间
```

**顺序规律**：
- `LPUSH` 把新元素放到最左边（索引 0 的位置）
- `RPUSH` 把新元素放到最右边（索引 -1 的位置）
- `LPUSH` 多次后，最新的元素总是在左端

### 3.2 LRANGE — 查看传送带上的所有元素

```bash
redis> LRANGE queue 0 -1
1) "任务B"
2) "任务A"
3) "任务C"
```

`LRANGE` 接受两个索引参数：
- `LRANGE key start stop` — 从 `start` 到 `stop`（含两端）
- `0` = 第一个元素，`-1` = 最后一个元素
- `LRANGE queue 0 -1` = 查看全部

```bash
redis> LRANGE queue 0 1       # 只看前两个
1) "任务B"
2) "任务A"
```

### 3.3 LPOP + RPOP — 从两端弹出

弹出（pop）= 取出元素 + 从列表中删除。

```bash
redis> LPOP queue              # 从左边弹出一个
"任务B"                        # 返回被弹出的元素
redis> LPOP queue
"任务A"
redis> RPOP queue              # 从右边弹出一个
"任务C"
redis> LPOP queue              # 队列空了
(nil)                          # 返回 nil，不是报错
```

**关键理解**：`LPOP` 取出来就删掉了——传送带上的元素不会重复出现。

### 3.4 LLEN — 看传送带多长

```bash
redis> LPUSH queue "A" "B" "C"    # 一次推入多个
(integer) 3
redis> LLEN queue
(integer) 3
```

`LLEN` 返回列表长度，O(1) 时间复杂度——Redis 内部维护了长度计数器。

### 3.5 栈和队列的两种模式

把上面的操作组合起来，就得到了两种经典数据结构：

**栈（Stack）— 后进先出**：

```bash
redis> LPUSH stack "1"
redis> LPUSH stack "2"
redis> LPUSH stack "3"

redis> LRANGE stack 0 -1
1) "3"    ← 最后推入的在最前面
2) "2"
3) "1"

redis> LPOP stack    # 3（后进先出）
redis> LPOP stack    # 2
redis> LPOP stack    # 1
```

**队列（Queue）— 先进先出**：

```bash
redis> RPUSH queue "1"
redis> RPUSH queue "2"
redis> RPUSH queue "3"

redis> LRANGE queue 0 -1
1) "1"    ← 最先推入的在最前面
2) "2"
3) "3"

redis> LPOP queue    # 1（先进先出）
redis> LPOP queue    # 2
redis> LPOP queue    # 3
```

### 3.6 LTRIM — 裁剪，只保留最新 N 条

```bash
redis> RPUSH recent "文章1" "文章2" "文章3" "文章4" "文章5"
(integer) 5

redis> LTRIM recent 0 2       # 只保留索引 0 到 2（前 3 条）
OK

redis> LRANGE recent 0 -1
1) "文章1"
2) "文章2"
3) "文章3"                    # 文章 4 和 5 被删了
```

**实际用法**：每次 LPUSH 后立即 LTRIM，确保列表不超过 N 条。

```bash
redis> LPUSH recent:posts "最新文章"
redis> LTRIM recent:posts 0 99    # 最多保留 100 条
```

这就是「最新 100 条评论」「热门文章 TOP 100」的实现方式。

### 3.7 LINDEX — 通过索引访问

```bash
redis> RPUSH mylist "A" "B" "C" "D" "E"
(integer) 5

redis> LINDEX mylist 0        # 索引 0 = 第一个
"A"
redis> LINDEX mylist -1       # 索引 -1 = 最后一个
"E"
redis> LINDEX mylist 10       # 越界返回 nil
(nil)
```

### 3.8 BLPOP / BRPOP — 阻塞弹出（等不到就等着）

这是 List 最强大的特性——**阻塞队列**。

```bash
# 终端 1（消费者）
redis> BLPOP task_queue 10    # 从左边弹出一个，最多等 10 秒
# ...阻塞等待中...

# 终端 2（生产者）
redis> RPUSH task_queue "发邮件任务"
(integer) 1

# 终端 1 瞬间收到：
1) "task_queue"               # 返回 [key, value]
2) "发邮件任务"
```

**超时**：

```bash
redis> BLPOP empty_queue 5    # 空队列，等 5 秒
# ...5 秒后...
(nil)                         # 超时返回 nil
```

`BLPOP` = **B**locking **L**ist **POP**。和 `LPOP` 的区别：

| 普通 Pop | 阻塞 Pop |
|---------|---------|
| 队列为空时立即返回 nil | 队列为空时阻塞等待 |
| 不等待 | 最多等 timeout 秒 |
| 适合「有就处理，没有拉倒」 | 适合「来了就处理，一直等到有」 |

> **BRPOP 和 BLPOP 的区别**：BRPOP 从右边弹出，BLPOP 从左边弹出。
> 经典消息队列模式：**生产者 RPUSH，消费者 BLPOP**。

---

## 4. 两个经典实战模式

### 模式 1：消息队列

```
生产者（你的 Web 服务）:
  RPUSH email:queue "发邮件给 user@example.com"

消费者（后台 Worker）:
  BLPOP email:queue 0    # 0 表示永远等待，不超时
```

```bash
# 生产端
redis> RPUSH email:queue '{"to":"user@example.com","subject":"欢迎！"}'

# 消费端
redis> BLPOP email:queue 0
1) "email:queue"
2) '{"to":"user@example.com","subject":"欢迎！"}'
```

**优势**：
- 不需要轮询——`BLPOP` 阻塞等待，零 CPU 消耗
- 天然解耦——生产者和消费者不需要知道对方的存在
- 多消费者自动负载均衡——多个 worker 同时 `BLPOP`，谁先抢到谁处理

### 模式 2：最新 N 条记录

```
每次有新内容：
  LPUSH recent:posts "新文章"
  LTRIM recent:posts 0 99    # 只保留 100 条
```

```bash
redis> LPUSH recent:posts "文章1"
redis> LTRIM recent:posts 0 99
redis> LPUSH recent:posts "文章2"
redis> LTRIM recent:posts 0 99
# ...持续这样操作...
```

无论 push 了多少次，列表永远不超过 100 条——旧数据自动丢弃。

---

## 5. 常见错误（新手必读）

### ❌ 错误 1：对空列表 Pop 以为会报错

```bash
redis> LPUSH mylist "test"
redis> LPOP mylist
"test"
redis> LPOP mylist          # 列表已经是空的
(nil)                       # 不是报错，是 nil
```

很多人写代码时会这样：

```python
task = client.lpop("queue")
if task:                    # ❌ 如果任务内容是空字符串，这里会有 bug
    process(task)

if task is not None:        # ✅ 正确：用 is not None 判断
    process(task)
```

### ❌ 错误 2：BLPOP 超时时间设置为 0 但忘了要处理超时

```python
# BLPOP timeout=0 表示永久等待
task = client.blpop("queue", timeout=0)   # 等到天荒地老
```

如果队列永远不会被写入，这个 worker 会永远卡住。生产环境建议设一个合理的超时时间（如 30 秒），超时后可以做一些健康检查或重连。

### ❌ 错误 3：阻塞超时了但没处理

```python
result = client.blpop("queue", timeout=5)
if result:                    # ❌ 如果超时，result 是 None
    key, value = result       # 这里会报 TypeError！
```

正确做法：

```python
result = client.blpop("queue", timeout=5)
if result is not None:
    key, value = result
    process(value)
else:
    # 超时了，做其他事
    print("队列为空，稍后再试")
```

### ❌ 错误 4：LTRIM 的索引搞反了

```bash
redis> RPUSH mylist "A" "B" "C" "D" "E"
redis> LTRIM mylist 0 2     # 保留索引 0, 1, 2 → A, B, C
```

`LTRIM key start stop` 保留的是**从 start 到 stop**（含两端）的元素：
- `LTRIM mylist 0 99` = 保留前 100 条（索引 0 到 99）
- `LTRIM mylist 1 0` = 全部删光（空列表）——因为 start > stop

### ❌ 错误 5：大量数据下用 LRANGE 0 -1

```bash
redis> LRANGE huge_list 0 -1   # ❌ 如果列表有 100 万个元素，Redis 会卡住
```

和 KEYS * 一样——LRANGE 返回所有元素，大列表时会产生巨大的网络传输和内存占用。用 `LRANGE` + 分页或者 `LTRIM` 控制列表大小。

---

## 6. 你学到了什么

| 命令 | 黑板动作 | O |
|------|---------|---|
| `LPUSH key value` | 从传送带左端推入 | O(1) |
| `RPUSH key value` | 从传送带右端推入 | O(1) |
| `LPOP key` | 从传送带左端弹出 | O(1) |
| `RPOP key` | 从传送带右端弹出 | O(1) |
| `LRANGE key start stop` | 查看传送带上某一段 | O(n) |
| `LLEN key` | 看传送带上有多少元素 | O(1) |
| `LTRIM key start stop` | 裁剪传送带，只留某一段 | O(n) |
| `BLPOP key timeout` | 传送带空了就等着，来了再弹出 | 阻塞 |
| `BRPOP key timeout` | 同上，但从右边弹 | 阻塞 |
| `LINDEX key index` | 通过索引看某个位置的元素 | O(n) |

### 一句话总结

```
LPUSH + LPOP = 栈（后进先出）
RPUSH + LPOP = 队列（先进先出）
RPUSH + BLPOP = 阻塞队列（消息队列）
LPUSH + LTRIM = 最新 N 条记录
```

---

## 7. 自己动手

1. **栈体验**：用 `LPUSH` 推入 5 个元素（"A"到"E"），然后用 `LPOP` 全部弹出来——感受后进先出

2. **队列体验**：用 `RPUSH` 推入 5 个元素，然后用 `LPOP` 全部弹出来——感受先进先出

3. **LTRIM 练习**：推入 10 个元素，用 `LTRIM` 只保留前 3 个，然后用 `LRANGE` 确认

4. **阻塞队列体验**：
   - 打开两个终端
   - 终端 1 执行 `BLPOP test_queue 0`
   - 终端 2 执行 `RPUSH test_queue "hello"`
   - 观察终端 1 瞬间收到消息

5. **最新消息列表**：连续 `LPUSH` 5 条消息，每次 `LPUSH` 后都执行 `LTRIM 0 2`——确认列表永远不超过 3 条

6. **运行 code.py**：`python s25_redis/s04_list/code.py`，看每一步的黑板状态变化

---

> **下一章：[s05: Hash — 对象存储](../s05_hash/)** — 学会用 Hash 存储对象，像操作 Python 字典一样操作 Redis
