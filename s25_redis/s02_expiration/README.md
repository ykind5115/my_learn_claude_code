# s02: 消失的墨水 — 让数据自动过期

[s01](../s01_first_read_write/) → `s02` → [s03](../s03_counter_atomic/) → ... → s18
> *"EXPIRE 不是定时器，是用消失墨水写字。"*
>
> **前提知识**: 做过 s01（会用 SET/GET/DEL/EXISTS）。知道 key 是什么。

---

## 1. 为什么需要过期时间？

先想两个真实场景：

| 场景 | 问题 | 如果不处理 |
|------|------|-----------|
| **短信验证码** | 验证码 5 分钟后过期 | 用户 1 小时前的验证码还能用 |
| **缓存** | 缓存数据 10 分钟后更新 | 用户看到 3 天前的旧数据 |
| **临时 Token** | 会话 Token 24 小时后失效 | 被盗的 Token 永远不过期 |
| **限时活动** | 红包 24 小时后过期 | 活动结束还能领 |

**如果你手动处理过期**，代码会变成这样：

```python
# ❌ 糟糕的做法：手动管理过期
data = {"value": "验证码1234", "created_at": time.time()}
# ...每隔 1 秒检查一次, 如果超时了手动删除...
```

太痛苦了。而且：
- 轮询浪费 CPU
- 时间判断有误差
- 删除延迟导致数据不一致

**Redis 的 EXPIRE 解决了这个问题**：你只需要告诉 Redis "这个 key 5 秒后作废"，剩下的 Redis 自动处理。

---

## 2. 在黑板模型下理解过期（消失墨水）

```
普通 SET：用普通马克笔写字
────────────────────────────────────────────────────────
  ┌─────────────────────────────────────────────┐
  │  name  "小明"      ← 永远不会消失           │
  │  cache "..."       ← 永远不会消失           │
  └─────────────────────────────────────────────┘


SET + EXPIRE：用"消失墨水"写字
────────────────────────────────────────────────────────
  ┌─────────────────────────────────────────────┐
  │  captcha  "4382"  ← 5 秒后自动消失  ⏳      │
  │  token    "abc"   ← 24 小时后自动消失 ⏳     │
  └─────────────────────────────────────────────┘
```

每个 key 都自带一个**倒计时器**：

- `TTL` = 看还剩多少秒消失（Time To Live）
- `PERSIST` = 把消失墨水换成普通墨水（撤销过期）
- `EXPIREAT` = 在指定时刻消失（某年某月某日某时消失）

---

## 3. 怎么做 — 逐行解释

### 3.1 EXPIRE — 给已有 key 加上消失墨水

```bash
redis> SET captcha "4382"
redis> EXPIRE captcha 10
(integer) 1    # 成功设置 10 秒过期
```

现在的黑板：

```
┌─────────────────────────────────────────────┐
│  captcha  "4382"  ← 10 秒后消失  (TTL: 10)  │
└─────────────────────────────────────────────┘
```

10 秒后：

```
┌─────────────────────────────────────────────┐
│  (黑板上什么都没有了 — 验证码自动消失)       │
└─────────────────────────────────────────────┘
```

`EXPIRE` 的参数是**秒数**。10 = 10 秒后消失。

### 3.2 TTL — 看还剩多少秒消失

```bash
redis> SET captcha "4382"
redis> EXPIRE captcha 60

redis> TTL captcha
(integer) 58    # 还剩 58 秒
redis> TTL captcha
(integer) 55    # 过了 3 秒，还剩 55 秒
```

TTL 的三个返回值：

| 返回值 | 含义 |
|--------|------|
| `TTL > 0` | 还剩 N 秒消失 |
| `TTL = -1` | key 存在，但没有设置过期（永久） |
| `TTL = -2` | key 不存在或已过期被删了 |

### 3.3 PERSIST — 恢复成普通墨水

```bash
redis> SET token "abc123"
redis> EXPIRE token 300      # 5 分钟后消失
redis> TTL token
(integer) 297                # 正在倒计时

redis> PERSIST token         # 取消过期！
(integer) 1                  # 成功
redis> TTL token
(integer) -1                 # 永久保存了
```

`PERSIST` 把消失墨水擦掉，换回普通墨水——key 不再过期。

### 3.4 EXPIREAT — 指定具体消失时间

```bash
# 让 key 在 2026 年 7 月 10 日 00:00:00 消失
redis> EXPIREAT coupon 1720656000    # Unix 时间戳
(integer) 1
```

`EXPIREAT` 接受 Unix 时间戳（秒级）。适合「今晚 12 点整过期」这种场景。

如果时间戳已经过了：

```bash
redis> EXPIREAT old_data 1000000000    # 2001 年的时间戳
(integer) 0                            # 设置失败！
# 这个 key 会被立即删除
```

### 3.5 SETEX — 写 + 消失一步到位

```bash
redis> SETEX captcha 10 "4382"
OK
# 等价于:
#   SET captcha "4382"
#   EXPIRE captcha 10
```

这是最常用的方式——SET 和 EXPIRE 合并成一个命令，省一次网络往返。

> SETEX 是原子操作（后续 s03 会讲原子性的意义）。用 SET + EXPIRE 两条命令也有同样的效果，但 SETEX 更安全——不会出现 SET 成功但 EXPIRE 失败的情况。

### 3.6 PSETEX — 毫秒级精度

```bash
redis> PSETEX captcha 5000 "4382"    # 5000 毫秒 = 5 秒
OK
```

`PSETEX` 和 `SETEX` 一样，但过期时间以毫秒为单位。

---

## 4. 再做两次练习，理解消失墨水

### 练习 A：观察 TTL 递减

```bash
redis> SETEX demo "hello" 10
redis> TTL demo
(integer) 8
redis> TTL demo
(integer) 5
redis> TTL demo
(integer) 2
redis> TTL demo
(integer) -2    # key 已消失
redis> GET demo
(nil)
```

睁眼看着 TTL 从 10 减到 -2——这就是"消失墨水在挥发"。

### 练习 B：多层过期

```bash
redis> SETEX session:user1 "data" 30
redis> SETEX session:user2 "data" 60
redis> SETEX session:user3 "data" 120
```

每个 session 有不同的过期时间——有些 30 秒消失，有些 2 分钟消失。

---

## 5. Redis 怎么删除过期键？

这个问题理解清楚了，你就超过了 90% 的 Redis 使用者。

Redis 用**两种策略**配合删除过期 key：

### 5.1 惰性删除（Lazy Deletion）

```
当你 GET 一个 key 时，Redis 检查一下：
  "这个 key 过期了吗？"
  过期 → 删掉，返回 nil
  没过期 → 正常返回
```

**类比**：你打开冰箱，发现牛奶过期了，你顺手扔掉。

**优点**：不浪费额外 CPU
**缺点**：如果没人访问这个 key，它会一直存在（占用内存）

### 5.2 定期删除（Periodic Deletion）

```
每 100ms，Redis 做一次"巡逻"：
  从所有过期 key 中随机抽一批
  把过期的删掉
  如果还有大量过期 key，继续抽下一批
```

**类比**：每周六清理冰箱——把过期的食物扔掉，不管有没有人翻冰箱。

**优点**：防止过期 key 一直占着内存不被清理
**缺点**：浪费一些 CPU 在巡逻上

### 5.3 如果还是没删完怎么办？

当过期 key 太多，惰性删除 + 定期删除都来不及处理时，内存会一直被占用。这时候 Redis 启动**内存淘汰策略**（后面章节会讲）——主动删一些 key 来腾出空间。

```
三个防线：
① 惰性删除  ← 默认、最快
② 定期删除  ← 兜底，每 100ms 一次
③ 内存淘汰  ← 内存满了才触发
```

---

## 6. 常见错误（新手必读）

### ❌ 错误 1：搞混 TTL = -1 和 TTL = -2

```bash
# TTL = -1: key 存在，但没设过期（永久）
redis> SET key "value"
redis> TTL key
(integer) -1    # 永久，正常

# TTL = -2: key 不存在或已过期被删
redis> DEL key
redis> TTL key
(integer) -2    # key 已经没了
```

### ❌ 错误 2：对不存在的 key 设 EXPIRE

```bash
redis> EXPIRE nothing 60
(integer) 0    # 设置失败！key 不存在
```

EXPIRE 返回 0 表示失败——检查一下是不是 key 拼错了，或者已经过期了。

### ❌ 错误 3：认为过期精度是 1 毫秒

```bash
# 你以为的是准时的，但 EXPIRE 的精度：
EXPIRE key 10    # +- 几毫秒的误差
EXPIREAT key ts  # 秒级精度
PSETEX key 10000 # 毫秒级精度
```

如果业务要求毫秒级精准过期（比如高频交易），Redis 的过期机制不太适合。它更多用于：
- 缓存过期（分钟/小时级）
- 验证码过期（秒/分级）
- Token 过期（小时/天级）

### ❌ 错误 4：大 key 过期阻塞

如果一个 key 存了 100 MB 的数据，这个 key 过期时：

```bash
redis> SETEX huge_data 1 "...100 MB 的数据..."
# 1 秒后，这个 key 过期
```

问题在于：**删除一个大 key 会阻塞 Redis**。因为 DEL 是同步操作，删除 100 MB 的数据可能需要几十毫秒——这段时间 Redis 无法处理其他请求。

解决方法：用 `UNLINK` 代替 `DEL`（Redis 4.0+），后台异步删除：

```bash
redis> UNLINK huge_data
(integer) 1    # 后台删除，不阻塞
```

### ❌ 错误 5：SET 不带过期，后面想起来了再 EXPIRE

```python
# ❌ 有问题：两步操作不是原子的
client.set("key", "value")
# ... 程序崩溃了 ...
client.expire("key", 60)    # 这行没执行到
```

用 `SETEX` 一步到位：

```python
# ✅ 原子操作
client.setex("key", 60, "value")
```

---

## 7. 你学到了什么

| 概念 | 你做了什么 |
|------|----------|
| `EXPIRE` | 给已有 key 加上"消失墨水"——N 秒后自动删除 |
| `TTL` | 看消失墨水还剩多少秒挥发完 |
| `PERSIST` | 把消失墨水擦掉，恢复成普通墨水 |
| `EXPIREAT` | 指定在某个具体时刻消失 |
| `SETEX` | 写 + 消失一步到位（SET + EXPIRE 合并） |
| 惰性删除 | GET 时顺手检查并删除过期 key |
| 定期删除 | Redis 每隔一段时间巡逻清理过期 key |
| `TTL = -1` | key 存在，永久保存 |
| `TTL = -2` | key 不存在或已过期 |

---

## 8. 自己动手

1. **体验 TTL 递减**：`SETEX key 10 "hello"`，然后快速多次 `TTL key` 看数值减少
2. **PERSIST 练习**：设一个 30 秒过期的 key，然后 `PERSIST` 它，确认 TTL 变成 -1
3. **EXPIREAT 练习**：让一个 key 在 "2 分钟后" 过期（用 Python 或 `date` 命令算时间戳）
4. **惰性删除验证**：设一个 3 秒过期的 key，等 5 秒后再 GET——确认返回 nil
5. **用 `redis-cli` 的 `WAIT`**：设一个 1 秒过期的 key，`TTL` 看到 0 后再 GET 看效果
6. **运行 code.py**：`python s25_redis/s02_expiration/code.py`，看着 TTL 一秒一秒递减

---

> **下一章：[s03: 计数器与原子操作](../s03_counter_atomic/)** — 理解 Redis 的单线程模型为什么让并发安全变得如此简单
