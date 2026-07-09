# s05: Hash — 对象存储

[s04](../s04_list/) → `s05` → [s06](../s06_set/) → ... → s18
> *"Hash 不是嵌套 Map，是黑板上的一个表格——一个 key 对应多个字段，每个字段存一个值。"*
>
> **前提知识**: 做过 s01~s03（String 基础操作）。理解 key-value 模型。

---

## 1. 为什么需要 Hash？

先想一个问题：怎么在 Redis 里存一个**用户对象**？

```json
{
  "name": "张三",
  "age": 28,
  "city": "北京",
  "level": "VIP"
}
```

### 方案 A：用多个 String key

```bash
SET user:1001:name "张三"
SET user:1001:age  "28"
SET user:1001:city "北京"
SET user:1001:level "VIP"
```

**问题**：
- 一个用户用了 4 个 key，100 万用户 = 400 万个 key——浪费内存
- 要查用户信息需要 4 次 GET（或一次 MGET），但没法方便地「查所有字段」
- 要删掉这个用户需要 4 次 DEL
- key 的命名越来越长

### 方案 B：存 JSON String

```bash
SET user:1001 '{"name":"张三","age":28,"city":"北京","level":"VIP"}'
```

**问题**：
- 想改一个字段（比如 age 从 28 改成 29）——必须读整个 JSON → 反序列化 → 改 → 序列化 → 写回
- 如果另一个请求同时改了 name，你的修改会覆盖别人的——并发问题
- 想只读 age 一个字段——也必须读整个 JSON

### 方案 C：用 Hash ✅

```bash
HSET user:1001 name "张三"
HSET user:1001 age  "28"
HSET user:1001 city "北京"
```

**优势**：
- 一个 key 存所有字段——内存效率高
- 可以只读/写一个字段——省网络
- 修改单个字段是原子操作——不会覆盖其他字段
- 可以一次性读取所有字段（HGETALL）
- 可以只读部分字段（HMGET）

| 场景 | String 多 key | JSON String | Hash |
|------|-------------|------------|------|
| 存一个用户 | 4 个 key | 1 个 key | 1 个 key |
| 读所有字段 | 4 次 GET | 1 次 GET | 1 次 HGETALL |
| 改一个字段 | 1 次 SET | 读+改+写（非原子） | 1 次 HSET |
| 删除用户 | 4 次 DEL | 1 次 DEL | 1 次 DEL |
| 内存效率 | 低 | 中 | **高**（底层压缩） |

> **Hash = 专门为「对象存储」设计的数据结构。**

---

## 2. 黑板模型下的 Hash

### 表格

把 Hash 想象成黑板上的一张**表格**：

```
┌─────────────────────────────────────────────────┐
│  KEY: user:1001                                  │
│  ┌─────────────┬───────────────────────────┐     │
│  │  字段 (field)  │  值 (value)              │     │
│  ├─────────────┼───────────────────────────┤     │
│  │  name        │  "张三"                   │     │
│  │  age         │  "28"                     │     │
│  │  city        │  "北京"                   │     │
│  │  level       │  "VIP"                    │     │
│  │  login_count │  "42"                     │     │
│  └─────────────┴───────────────────────────┘     │
│                                                   │
│  整张表 = 一个 Redis key                          │
│  每一行 = 一个 field-value pair                   │
│  可以独立增、删、改、查每一行                      │
└─────────────────────────────────────────────────┘
```

### 和 String 的对比

```
String:
  key1 → value1     ← 一个 key 只能存一个值

Hash:
  key1 → field1 → value1    ← 一个 key 存多组值
       → field2 → value2
       → field3 → value3
```

### 和 Python dict / Java Map 的类比

```
Hash  = 一个 Redis key 对应一个 dict
field = dict 的 key
value = dict 的 value

HSET user:1001 name "张三"     →   user[1001]["name"] = "张三"
HGET user:1001 name            →   user[1001]["name"]
HGETALL user:1001              →   user[1001]  # 返回整个 dict
```

---

## 3. 怎么做 — 逐行解释

### 3.1 HSET — 写入/更新一个字段

```bash
redis> HSET user:1001 name "张三"
(integer) 1        # 1 = 新增了一个字段
redis> HSET user:1001 age "28"
(integer) 1
redis> HSET user:1001 city "北京"
(integer) 1
```

现在的黑板：

```
user:1001:
  name → "张三"
  age  → "28"
  city → "北京"
```

第二次写入同一个字段——字段已存在，更新值：

```bash
redis> HSET user:1001 name "张三三"    # 更新已有字段
(integer) 0                             # 0 = 没有新增字段，只是更新
```

> HSET 的返回值：1 表示新增了一个字段，0 表示更新了已有字段的值。

### 3.2 HGET — 读取一个字段

```bash
redis> HGET user:1001 name
"张三"
redis> HGET user:1001 age
"28"
redis> HGET user:1001 not_exist    # 字段不存在
(nil)
```

### 3.3 HGETALL — 读取所有字段

```bash
redis> HGETALL user:1001
1) "name"
2) "张三"
3) "age"
4) "28"
5) "city"
6) "北京"
```

返回格式是**交替的 field-value 列表**：field1, value1, field2, value2, ...

在 Python 客户端里自动转为 dict：

```python
result = client.hgetall("user:1001")
# 结果: {"name": "张三", "age": "28", "city": "北京"}
```

### 3.4 HEXISTS — 检查字段是否存在

```bash
redis> HEXISTS user:1001 name
(integer) 1        # 存在
redis> HEXISTS user:1001 email
(integer) 0        # 不存在
```

### 3.5 HDEL — 删除一个字段

```bash
redis> HDEL user:1001 city
(integer) 1        # 删除了 1 个字段
redis> HGETALL user:1001
1) "name"
2) "张三"
3) "age"
4) "28"
```

### 3.6 HINCRBY — 原子递增某个字段

这是 Hash 的隐藏大招——在存储对象的同时，可以原子地对某个数字字段做增减：

```bash
redis> HINCRBY user:1001 login_count 1
(integer) 1        # 首次登录，自动创建 login_count 并 +1
redis> HINCRBY user:1001 login_count 1
(integer) 2
redis> HGET user:1001 login_count
"2"
```

**不需要先初始化**——`HINCRBY` 自动创建不存在的字段，默认从 0 开始。

```bash
redis> HINCRBY user:1001 score 50
(integer) 50       # 自动创建 score 字段，初始 0，加 50
redis> HINCRBY user:1001 score -20
(integer) 30       # 加负数 = 减
```

### 3.7 HINCRBYFLOAT — 浮点数递增

```bash
redis> HINCRBYFLOAT user:1001 balance 99.9
"99.9"
redis> HINCRBYFLOAT user:1001 balance 0.1
"100.0"
```

### 3.8 HMGET — 一次读取多个字段

```bash
redis> HMGET user:1001 name age login_count
1) "张三"
2) "28"
3) "2"
```

比连续 3 次 `HGET` 少 2 次网络往返。

### 3.9 HLEN, HKEYS, HVALS

```bash
redis> HLEN user:1001               # 有几个字段？
(integer) 3

redis> HKEYS user:1001              # 所有字段名
1) "name"
2) "age"
3) "login_count"

redis> HVALS user:1001              # 所有字段值
1) "张三"
2) "28"
3) "2"
```

---

## 4. Hash 的内存效率

Hash 有一个很重要的特性：**当某个 Hash 的字段数量较少（默认 < 512 个）且每个字段的值较短时，Redis 内部用 ziplist（紧凑列表）编码**，而不是普通的 dict 结构。

这意味着：

```bash
# 同样的数据，Hash 可能比 String 省 50%~80% 的内存

# ❌ 用 String
SET user:1001:name "张三"    # key 本身就有开销
SET user:1001:age  "28"      # 每个 key 约 50-100 字节额外开销

# ✅ 用 Hash（同一个 key，多个 field）
HSET user:1001 name "张三"   # key 只存一次
HSET user:1001 age  "28"     # field 在 ziplist 里连续存储
```

当字段数超过 512 或某个字段值超过 64 字节时，Hash 会自动转为 dict 编码——读/写性能仍然是 O(1)，只是内存不那么省了。

---

## 5. 经典实战：用户信息缓存

```bash
# 用户注册时
HSET user:1001 name "张三"
HSET user:1001 age 28
HSET user:1001 city "北京"
HSET user:1001 created_at "2026-07-09"

# 用户登录时，递增登录次数
HINCRBY user:1001 login_count 1

# 用户更新资料（只更新一个字段）
HSET user:1001 city "上海"

# 页面展示用户信息（一次读取全部）
HGETALL user:1001

# 检查用户是否存在
EXISTS user:1001

# 七天未登录，清理
DEL user:1001
```

---

## 6. 常见错误（新手必读）

### ❌ 错误 1：HGETALL 用于大 Hash

```bash
redis> HGETALL user:1001    # 如果这个 Hash 有 10 万个字段...
```

和 KEYS *、LRANGE 0 -1 一样——HGETALL 返回所有字段，大 Hash 时会阻塞 Redis、撑爆网络。

**替代方案**：用 `HSCAN` 分批迭代（类似 SCAN），或者确保 Hash 字段数在合理范围内。

### ❌ 错误 2：把 Hash 当嵌套对象用

```bash
# ❌ Hash 不支持嵌套
HSET article:42 author:name "张三"    # 字段名里用冒号假装嵌套
HSET article:42 author:age "28"       # 但 Redis 不识别嵌套结构
```

Hash 是**一层**的结构——field 就是字符串，value 也是字符串。如果需要复杂嵌套，用 JSON String。

```bash
# ✅ 嵌套数据用 JSON String
SET article:42 '{"author":{"name":"张三","age":28},"title":"Redis 教程"}'
```

### ❌ 错误 3：HSET 和 HGET 的返回值搞混

```bash
redis> HSET user name "张三"
(integer) 1        # 返回 1（成功/新增个数）
redis> HGET user name
"张三"             # 返回值
```

新手容易困惑：「HSET 返回 1 是什么意思？是值吗？」不是——HSET 返回的是「影响了几个字段」。

### ❌ 错误 4：HMSET（Redis 7.0 后已废弃）

```bash
# 旧版
HMSET user:1001 name "张三" age "28"    # Redis 4.0+ 中已标记为废弃

# 新版（HSET 已经支持多个 field-value 对）
HSET user:1001 name "张三" age "28"     # ✅ 推荐
```

从 Redis 4.0+ 开始，`HSET` 已经支持传入多个 field-value 对，`HMSET` 已经不需要了。

### ❌ 错误 5：对不存在的 hash 执行 HGET 不会报错

```bash
redis> HGET nonexistent key
(nil)               # 不是报错，是 nil
redis> HDEL nonexistent key
(integer) 0         # 不会报错
```

所有 Hash 操作对不存在的 key 都返回 nil 或 0——不需要先检查 key 是否存在。

---

## 7. 你学到了什么

| 命令 | 黑板动作 | 时间复杂度 |
|------|---------|-----------|
| `HSET key field value` | 在表格的 `field` 行写入 `value` | O(1) |
| `HGET key field` | 读表格的 `field` 行 | O(1) |
| `HGETALL key` | 读整个表格（所有 field-value） | O(n) |
| `HDEL key field` | 删除表格的一行 | O(1) |
| `HEXISTS key field` | 检查表格的某行是否存在 | O(1) |
| `HINCRBY key field n` | 表格某行的数字加 n | O(1) |
| `HINCRBYFLOAT key field n` | 表格某行的浮点数加 n | O(1) |
| `HMGET key field1 field2` | 一次读多行 | O(1) per field |
| `HLEN key` | 看表格有多少行 | O(1) |
| `HKEYS key` | 列出所有字段名 | O(n) |
| `HVALS key` | 列出所有字段值 | O(n) |

### 一句话总结

```
String = 一行文字（一个 key 存一个值）
Hash   = 一张表格（一个 key 存多个 field-value）
```

---

## 8. 自己动手

1. **创建你的用户信息**：用 HSET 存你的名字、年龄、城市、爱好，然后用 HGETALL 查看

2. **更新一个字段**：把年龄改成新值，用 HGET 确认只改了这一个字段

3. **登录计数器**：对同一个用户连续执行 5 次 `HINCRBY login_count 1`，观察 login_count 如何增长

4. **批量读取**：用 HMGET 一次读取 name、city 两个字段，感受比两次 HGET 更高效

5. **内存对比**：创建 100 个用户，分别用 String 方式（`SET user:1:name "..."`）和 Hash 方式（`HSET user:1 name "..."`）——用 `INFO memory` 看内存差异（可选）

6. **运行 code.py**：`python s25_redis/s05_hash/code.py`，看每一步的黑板状态变化

---

> **下一章：[s06: Set — 去重与集合运算](../s06_set/)** — 学会用 Set 做标签、去重、共同好友
