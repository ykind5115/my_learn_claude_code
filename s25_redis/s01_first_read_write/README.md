# s01: 第一次读写 — 在黑板上写下第一行字

[s00](../s00_mental_model/) → `s01` → [s02](../s02_expiration/) → ... → s18
> *"SET 不是插入，是在黑板上写字。GET 不是查询，是看黑板上写了什么。"*
>
> **前提知识**: 看过 s00（知道 Redis = 共享黑板模型）。安装了 Redis，会启动 `redis-cli` 或准备运行 Python 脚本。

---

## 1. 为什么需要 SET / GET / DEL / EXISTS？

如果你有一个变量存在 Python 或者 Java 的内存里，这个变量**只属于你的进程**。关闭程序它就没了。换一台机器就访问不到了。

Redis 解决了三个问题：

| 问题 | 怎么办 |
|------|--------|
| "数据存在哪，所有进程都能读到？" | SET / GET — 写/读共享黑板 |
| "怎么确认某个键已经存在？" | EXISTS — 看黑板上有没有这行字 |
| "写错了怎么擦掉？" | DEL — 擦掉黑板上的一行字 |
| "怎么知道黑板上总共写了什么？" | KEYS — 列出黑板上所有内容 |

这些是 Redis **最基础的操作**。理解它们 = 理解 Redis 的"读写"到底是什么。

---

## 2. 在黑板模型下理解这些命令

Redis 的共享黑板模型在 s00 里详细介绍过。简单来说：

```
┌─────────────────────────────────────────────┐
│            Redis = 共享黑板                    │
│                                              │
│   ┌───────────────────────────────────┐      │
│   │  KEY1     "hello"                 │      │
│   │  KEY2     "world"                 │      │
│   │  name     "张三"                   │      │
│   │  counter  "42"                    │      │
│   │                                   │      │
│   └───────────────────────────────────┘      │
│                                              │
│   任何人（任何进程）都可以读写这块黑板         │
└─────────────────────────────────────────────┘
```

每个命令对应一个黑板动作：

| 命令 | 黑板动作 | 类比 |
|------|---------|------|
| `SET key value` | 在黑板的 `key` 这一行写上 `value` | 用马克笔写一行字 |
| `GET key` | 看黑板上的 `key` 这一行写了什么 | 看某一行 |
| `DEL key` | 把黑板上 `key` 这一行擦掉 | 用板擦擦掉一行 |
| `EXISTS key` | 看 `key` 这一行有没有字 | 确认某行是否有内容 |
| `KEYS *` | 看黑板上所有行 | 扫视整个黑板 |
| `TYPE key` | 看 `key` 这一行是用什么记号写的 | 确认笔的类型（马克笔/粉笔/...） |
| `FLUSHDB` | 把整块黑板擦干净 | 用大板擦全部擦掉 |

---

## 3. 怎么做 — 逐行解释

下面用 Python 演示（你也可以同时在 `redis-cli` 里敲同样的命令）。

### 3.1 连接 Redis — 站在黑板前

```python
import redis
client = redis.Redis(host="localhost", port=6379, decode_responses=True)
client.ping()  # 如果返回 True，说明黑板就在你面前
```

`ping()` 就像在黑板上轻轻敲一下——如果 Redis 活着，它会说 `PONG`。

> **为什么要 `decode_responses=True`？** 默认 Redis 返回的是字节（`b"hello"`），加上这个参数自动转成字符串（`"hello"`），新手友好。

### 3.2 SET — 在黑板上写第一行字

```bash
redis> SET name "小明"
OK
```

这是 Redis **最基本的写操作**。效果：

```
┌─────────────────────────────────────┐
│  name     "小明"                     │
└─────────────────────────────────────┘
```

SET 的完整语法：

```bash
SET key value [NX | XX] [EX seconds | PX milliseconds]
```

- `NX` — 只在键不存在时设置（后面 s03 的 SETNX 就是它）
- `XX` — 只在键已经存在时设置
- `EX / PX` — 设置过期时间（后面 s02 会讲）

对于第一次接触 Redis，你只需要记住：**`SET key value`** 就够了。

### 3.3 GET — 看看黑板上写了什么

```bash
redis> GET name
"小明"
```

如果这个 key 不存在：

```bash
redis> GET nothing
(nil)
```

`nil` 在 Redis 里表示"没有值"。不是空字符串，是什么都没有。

### 3.4 SET 覆盖写 — 同一行，换一句话

```bash
redis> SET name "小红"
OK
redis> GET name
"小红"
```

**SET 是覆盖写**。同一个 key 第二次 SET，旧值就没了。黑板上同一行写了新字，旧字自然被覆盖。

### 3.5 一次性写入多个 key

```bash
redis> SET age "25"
redis> SET city "北京"
redis> SET language "Python"
```

现在黑板上有多个 key：

```
┌─────────────────────────────────────┐
│  age       "25"                      │
│  city      "北京"                    │
│  language  "Python"                  │
│  name      "小红"                    │
└─────────────────────────────────────┘
```

### 3.6 KEYS — 看黑板上所有的内容

```bash
redis> KEYS *
1) "name"
2) "age"
3) "city"
4) "language"
```

> **⚠️ 生产环境慎用**：`KEYS *` 会遍历所有 key，在 key 数量大的时候阻塞 Redis 几秒甚至几十秒。生产环境用 `SCAN` 代替（s02 里会介绍）。

### 3.7 EXISTS — 确认某行有没有字

```bash
redis> EXISTS name
(integer) 1    # 存在
redis> EXISTS nothing
(integer) 0    # 不存在
```

### 3.8 DEL — 擦掉某一行

```bash
redis> DEL city
(integer) 1    # 删除了 1 个 key
redis> GET city
(nil)          # 没有了
```

DEL 可以一次删除多个：

```bash
redis> DEL age language
(integer) 2    # 删除了 2 个 key
```

### 3.9 TYPE — 看什么笔写的

```bash
redis> SET name "小明"
redis> TYPE name
string         # 用马克笔写的
```

虽然目前所有值都是 String，但 Redis 有 5 种核心数据结构（String / List / Hash / Set / Sorted Set），`TYPE` 告诉我们这一行是用什么"记号"写的——后面几章会一一展开。

### 3.10 FLUSHDB — 擦掉整块黑板

```bash
redis> FLUSHDB
OK
```

> **⚠️ 极其危险！** 生产环境用 `FLUSHDB` 等于把整块黑板擦得干干净净，所有数据都没了。

---

## 4. 再做两次练习，感受写和读

### 练习 A：搭建用户信息

```bash
redis> SET user:1001 "张三"
redis> SET user:1002 "李四"
redis> SET user:1003 "王五"
redis> KEYS user:*
1) "user:1001"
2) "user:1002"
3) "user:1003"
```

注意 `user:1001` 这种命名方式——冒号在 Redis 里没有特殊含义，只是**约定俗成的命名风格**，用来表示"命名空间"。

### 练习 B：计数器（后面 s03 会深入）

```bash
redis> SET visits "0"
redis> GET visits
"0"
```

虽然 INCR 才是计数器的最佳工具（s03 会讲），但先用 SET/GET 也能实现——只是并发不安全。

---

## 5. 常见错误（新手必读）

### ❌ 错误 1：key 命名不规范

```
❌ 混乱命名:
  SET "My Name" "value"    # 有空格，要加引号
  SET 姓名 "value"         # 可以用中文，但不建议
  SET a "value"            # 太短，不知道什么意思

✅ 好的命名（用冒号分隔命名空间）:
  SET user:1001:name "张三"
  SET article:42:title "Redis 教程"
  SET config:max_connections "100"
```

**规则**：key 应该让三周后的你能看懂。用冒号 `:` 分隔层次，就像文件路径。

### ❌ 错误 2：生产环境用 `KEYS *`

```python
# ❌ 危险！如果有 1000 万个 key，Redis 会阻塞几十秒
client.keys("*")
```

后面 s02 会教你用 `SCAN` 替代。演示环境随便用，生产环境想想再说。

### ❌ 错误 3：连接不上 Redis

```
redis.exceptions.ConnectionError: Error 10061 connecting to localhost:6379.
```

检查三件事：

1. Redis 启动了没？`redis-cli ping` 试试
2. 端口对不对？默认 6379
3. 是不是 Docker 但忘了映射端口？
   ```bash
   docker run -d --name redis-demo -p 6379:6379 redis:7-alpine
   ```

### ❌ 错误 4：认为 GET 获取不存在的 key 会报错

```python
result = client.get("nothing")
# result 是 None，不是报错
# 做判断时要慎重:
if result:          # ❌ None 和 "" 都会被判 False
if result is None:  # ✅ 正确做法
```

### ❌ 错误 5：SET 中 value 包含特殊字符

Redis 的 String 是二进制安全的——你可以存任何内容（图片、JSON、序列化对象）。但在 `redis-cli` 中直接输入特殊字符要小心，推荐用引号包裹。

```bash
# ✅ 好的做法
redis> SET greeting "Hello, world!"
redis> SET json '{"name": "小明"}'
```

---

## 6. 你学到了什么

| 概念 | 你做了什么 |
|------|----------|
| `SET` | 在黑板上写一行字——存 key-value |
| `GET` | 读黑板上某一行的内容——查 key |
| `DEL` | 擦掉黑板上的一行——删 key |
| `EXISTS` | 确认某行有没有字——判断 key 存在 |
| `KEYS` | 扫视整个黑板——列出所有 key |
| `TYPE` | 看某行是用什么笔写的——查 key 类型 |
| `FLUSHDB` | 整块黑板擦干净——清空所有数据 |
| 黑板模型 | Redis = 所有人共享的一块黑板，读写都是即时可见 |

---

## 7. 自己动手

1. **启动 redis-cli**：`redis-cli`，然后执行 `SET hello "world"` 和 `GET hello`
2. **写三个 key**：存你喜欢的三个东西（书名、电影、食物），用 `KEYS *` 查看
3. **体验覆盖写**：同一个 key SET 两次不同的值，GET 看最终结果
4. **体验 DEL**：删掉一个 key，用 EXISTS 确认它不存在了
5. **用 TYPE** 检查你创建的每个 key 的类型
6. **运行 code.py**：`python s25_redis/s01_first_read_write/code.py`，看每一步的黑板状态变化

---

> **下一章：[s02: 消失的墨水](../s02_expiration/)** — 学会让数据自动过期，用"消失墨水"写字
