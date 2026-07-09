# s12: AOF 日志 — 记录每一次写字

[s11](../s11_rdb/) → `s12` → [s13](../s13_replication/)
> *"AOF 不是备份，是把每次在黑板上写的动作记在本子上。断电后按本子重做一遍。"*
>
> **前提知识**: 理解 s11 的 RDB 快照。知道 RDB 会丢数据。

---

## 1. RDB 有什么缺陷？

从 s11 我们知道：RDB 是定时拍快照。在两次快照之间写入的数据，Redis 崩溃后全部丢失。

```
RDB 的时间线：

  08:00 ──── 📸 BGSAVE 拍照 ──── 08:15 ──── 📸 BGSAVE 拍照 ────
                      ↑                      ↑
            key1 ~ key100 已保存    key101 ~ key200 已保存

        08:10 写入 key88           08:20 写入 key201
        (拍照时已包含 key88)       (还没到拍照时间)

                        💥 Redis 在 08:22 崩溃！

  崩溃后恢复：
    key1 ~ key200 恢复 ✓
    key201 丢失 ✗              ← 两次快照之间写入的数据！
```

**如果丢数据的代价很高**（比如支付订单、用户操作日志），该怎么办？

答案：**AOF（Append Only File）**——不是等下一张照片，而是**把每一次写字动作都记下来**。

---

## 2. 在黑板模型下理解 AOF

AOF = Append Only File，追加写文件。

### 类比

```
RDB（拍照）：
  ┌─────────────────────────────────────┐
  │  📸 拍一张照片，照片里包含了        │
  │     黑板上所有的内容                │
  │                                     │
  │  优点：恢复快 ✅                     │
  │  缺点：上次拍照之后写的内容会丢 ❌  │
  └─────────────────────────────────────┘

AOF（记日志）：
  ┌─────────────────────────────────────┐
  │  📓 准备一个本子，每次在黑板上写字  │
  │     就把写的内容记在本子上          │
  │                                     │
  │  SET user:1001 "张三"   → 本子 +1行 │
  │  INCR visits            → 本子 +1行 │
  │                                     │
  │  优点：几乎不丢数据 ✅               │
  │  缺点：本子越来越厚，恢复慢 ❌      │
  └─────────────────────────────────────┘
```

### AOF 的工作流程

```
正常运行时 Redis：

  ┌──────────────┐    命令     ┌──────────────────┐
  │  客户端       │ ──────────→ │  Redis 服务器      │
  │  SET A "1"   │             │                   │
  └──────────────┘             └────────┬─────────┘
                                        │
                       ┌────────────────┼────────────────┐
                       │                │                │
                       ▼                ▼                ▼
                ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
                │ 更新内存       │ │ 写入 AOF 文件  │ │ （可选）写入  │
                │ (黑板的值变了) │ │ (记在本子上)  │ │ RDB 快照     │
                └──────────────┘ └──────────────┘ └──────────────┘
```

### 断电恢复

```
Redis 重启时：

  ① 读取 AOF 文件
  ② 从第一行到最后一行的命令依次执行

  ┌─────────────────────────────────────┐
  │  AOF 文件内容:                       │
  │  *3                                  │
  │  $3                                  │
  │  SET                                 │
  │  $10                                 │
  │  user:1001                           │
  │  $6                                  │
  │  张三                                │
  │  ...                                 │
  │                                     │
  │  逐条执行 → 内存恢复到断电前的状态   │
  └─────────────────────────────────────┘
```

AOF 文件保存的不是「值」，而是**写命令本身**。格式是 RESP（Redis 序列化协议）——每个命令被编码成多行文本，以 `*` 开头表示数组长度，`$` 开头表示字符串长度。

---

## 3. AOF 的三种 fsync 策略

### 3.1 什么是 fsync？

写入文件时，操作系统的流程：

```
写文件时：

  Redis 调用 write()          → 数据写入操作系统 Page Cache
      ↓
  操作系统在适当时候          → 把 Page Cache 写入硬盘
      ↓
  fsync() 强制刷盘            → 立即将 Page Cache 写入硬盘

  write() 很快，但数据还在系统缓冲区——如果断电，缓冲区数据丢失
  fsync() 强制写盘——慢，但安全
```

AOF 的 `appendfsync` 配置决定什么时候调 fsync：

### 3.2 三种策略

| 策略 | 配置值 | 行为 | 安全性 | 性能 |
|------|--------|------|--------|------|
| 每次写入都 fsync | `always` | 每执行一个写命令，立即 fsync | ⭐⭐⭐ 最安全，最多丢一个命令 | ⭐ 最慢（频繁磁盘 IO） |
| 每秒 fsync 一次 | `everysec` | 每秒将缓冲区数据 fsync 到硬盘 | ⭐⭐ 最多丢 1 秒的数据 | ⭐⭐⭐ 推荐，兼顾安全与性能 |
| 让操作系统决定 | `no` | 不主动 fsync，由 OS 决定刷盘时机 | ⭐ 可能丢几十秒的数据 | ⭐⭐⭐ 最快 |

### 3.3 appendfsync everysec 是默认推荐

```
时间轴：

  第 0.0 秒: SET A 1     → 写入 AOF 缓冲区
  第 0.1 秒: SET B 2     → 写入 AOF 缓冲区
  第 0.5 秒: SET C 3     → 写入 AOF 缓冲区

  第 1.0 秒: fsync!      → 缓冲区内容全部刷到硬盘
                          → AOF 文件记录了三行！

  第 1.2 秒: SET D 4     → 写入 AOF 缓冲区
  第 1.8 秒: SET E 5     → 写入 AOF 缓冲区

  💥 第 1.9 秒: Redis 崩溃！

  恢复后：
    AOF 文件只有 3 行（A、B、C），D 和 E 丢失了

  丢失窗口 ≈ 0.9 秒（上一次 fsync 到崩溃之间的数据）
```

### 3.4 配置建议

- **`appendfsync always`**：对数据完整度要求极高的场景——金融交易、支付流水、订单状态
- **`appendfsync everysec`**：绝大多数场景——默认推荐，每秒刷一次，最多丢 1 秒数据
- **`appendfsync no`**：对数据丢失容忍度较高、追求极致性能——比如纯缓存场景

```bash
# 查看当前 fsync 策略
redis> CONFIG GET appendfsync
1) "appendfsync"
2) "everysec"

# 修改 fsync 策略（运行时）
redis> CONFIG SET appendfsync everysec
```

---

## 4. AOF 重写（Rewrite）— 日志文件太大怎么办？

### 4.1 问题：AOF 文件无限增长

AOF 记录的是每一次写操作，不是最终状态。所以 AOF 文件会越来越臃肿：

```
假设你做了这些操作：

  INCR counter  → AOF 多一行
  INCR counter  → AOF 多一行
  INCR counter  → AOF 多一行
  ...（重复 10000 次）
  INCR counter  → AOF 记录 10000 行！

实际上，最终状态只是：counter = 10000
但 AOF 文件里有 10000 行 INCR，恢复时就要执行 10000 次 INCR！

还有更极端的例子：
  SET cart "手机"
  SET cart "充电器"
  SET cart "耳机"
  SET cart "手机壳"

最终状态是 cart = "手机壳"
但 AOF 文件记录了 4 行 SET，而恢复时前 3 行的 SET 完全是浪费！
```

### 4.2 Rewrite 做了什么？

AOF 重写（Rewrite）= 把 AOF 日志「压缩」。不是原地修改旧文件，而是**创建一个新的、更精简的 AOF 文件**。

```
重写前（AOF 文件 5 MB，记录了 100 万行）：
  SET user:1001:visited 1
  SET user:1001:visited 2
  SET user:1001:visited 3
  ...（每个用户的 100 次访问记录都在）
  INCR page_views
  INCR page_views
  INCR page_views
  ...（10000 次 INCR）

重写过程：
  Redis 读取内存中所有 key 的当前值
  为每个 key 生成一条 SET 命令

重写后（AOF 文件 10 KB，压缩了 500 倍！）：
  SET user:1001:visited 100       ← 最终值就是 100
  SET page_views 10000            ← 最终值就是 10000
  ...（总共只有 N 条命令，N = key 的数量）
```

### 4.3 手动触发 Rewrite

```bash
redis> BGREWRITEAOF
Background append only file rewriting started
```

### 4.4 自动触发 Rewrite 的配置

```bash
# AOF 文件增长到上次重写大小的 100% 时触发重写
auto-aof-rewrite-percentage 100

# AOF 文件至少达到 64 MB 才触发重写（防止小文件频繁重写）
auto-aof-rewrite-min-size 64mb
```

**举例**：

```
上次重写后 AOF 文件大小：100 MB
当前 AOF 文件大小：      200 MB  → 增长 100%，≥ 64 MB → 触发重写！
当前 AOF 文件大小：       80 MB  → 增长不到 100%    → 不触发
当前 AOF 文件大小：      250 MB  → 增长 150%，≥ 64 MB → 触发重写！
```

### 4.5 Rewrite 也是 fork 子进程执行

```
BGREWRITEAOF 的执行流程：

  ┌──────────────────────────────────────────────┐
  │  ① 用户执行 BGREWRITEAOF                      │
  │                                                │
  │  ② Redis fork 子进程                           │
  │                                                │
  │  ③ 子进程读取内存中所有 key 的当前值            │
  │     生成精简的 AOF 内容写入临时文件              │
  │                                                │
  │  ④ 主进程同时把新的写操作记录到「重写缓冲区」    │
  │     （Rewrite Buffer）                         │
  │                                                │
  │  ⑤ 子进程完成后通知主进程                       │
  │                                                │
  │  ⑥ 主进程把重写缓冲区的内容追加到临时文件末尾    │
  │                                                │
  │  ⑦ 用临时文件原子替换旧 AOF 文件               │
  └──────────────────────────────────────────────┘
```

### 4.6 查看 AOF 相关信息

```bash
# AOF 文件大小
redis> INFO persistence
aof_current_size:12345678      # 当前 AOF 文件大小（字节）
aof_base_size:5000000          # 上次重写后的 AOF 大小（字节）

# 重写状态
aof_last_rewrite_time_sec:12   # 上次重写耗时（秒）
aof_last_bgrewrite_status:ok   # 上次重写状态
```

---

## 5. RDB + AOF 混合持久化（Redis 4.0+）

### 5.1 为什么需要混合模式？

| 方案 | 恢复速度 | 数据安全 |
|------|---------|---------|
| 纯 RDB | ⭐⭐⭐ 极快 | ⭐ 可能丢数据 |
| 纯 AOF | ⭐ 慢（需要重放所有命令） | ⭐⭐⭐ 几乎不丢 |
| **RDB + AOF 混合** | ⭐⭐ 快 | ⭐⭐ 好 |

### 5.2 混合模式的原理

```
混合持久化（aof-use-rdb-preamble yes）：

  AOF 文件结构：

  ┌──────────────────────────────────────────────┐
  │  ┌──────────────────────────────────┐        │
  │  │  RDB 格式的数据快照              │ ← 先加载这部分（二进制，很快）
  │  │  (压缩二进制，包含所有 key)       │       │
  │  └──────────────────────────────────┘        │
  │  ┌──────────────────────────────────┐        │
  │  │  AOF 格式的增量命令              │ ← 再执行这些命令（补齐最新数据）
  │  │  SET keyA value                  │       │
  │  │  INCR counter                    │       │
  │  │  ...                             │       │
  │  └──────────────────────────────────┘        │
  └──────────────────────────────────────────────┘

  恢复流程：
    Step 1: 检测到文件开头是 RDB 格式 → 快速加载 RDB 部分（速度接近纯 RDB）
    Step 2: 加载完 RDB 后，继续执行后面的 AOF 命令（补齐最新变化）
    Step 3: 恢复完成！

  速度 ≈ RDB（因为有 RDB 快速加载）
  安全 ≈ AOF（因为后面的增量日志记录了最新数据）
```

### 5.3 开启混合模式

```bash
# redis.conf
aof-use-rdb-preamble yes

# 或运行时配置（Redis 5.0+ 默认开启）
redis> CONFIG SET aof-use-rdb-preamble yes
```

### 5.4 什么时候 Rewrite 生成 RDB 头？

当混合模式开启时，每次 `BGREWRITEAOF` 生成的 AOF 文件都会以 RDB 格式开头：

```
重写前（纯 AOF）：
  SET k1 v1
  SET k2 v2
  INCR c
  SET k3 v3

重写后（混合格式）：
  ┌──────────────────┐
  │ RDB (k1=v1,      │  ← 二进制，压缩过
  │       k2=v2,      │
  │       c=1,        │
  │       k3=v3)      │
  └──────────────────┘
  ┌──────────────────┐
  │ （无增量命令——    │  ← 重写那瞬间没有新写入
  │  如果重写过程中  │
  │  有写入，会追加  │
  │  到这个地方）    │
  └──────────────────┘
```

---

## 6. RDB vs AOF 对比

| 特性 | RDB | AOF |
|------|-----|-----|
| **记录方式** | 定时全量快照（拍照） | 逐条记录写操作（记日志） |
| **数据安全** | 可能丢两次快照间的数据 | everysec 最多丢 1 秒数据 |
| **恢复速度** | ⭐⭐⭐ 极快 | ⭐ 慢（尤其是未重写时） |
| **文件体积** | 小（压缩二进制） | 大（文本日志，需重写） |
| **可读性** | 不可读（二进制） | 可读（文本，可以用 less 看） |
| **写入性能** | 不影响写（fork 子进程） | always 策略磁盘 IO 较重 |
| **备份传输** | 适合（文件小） | 不太适合（文件大） |

### 什么时候用哪个？

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| 缓存（session、验证码） | RDB 即可 | 丢了可以从数据库重新加载 |
| 用户购物车 | RDB + AOF everysec | 可以丢一点，但不能全丢 |
| 计数器 / 排行榜 | RDB | 丢了可以重新计算 |
| 支付订单 / 交易流水 | AOF always + RDB | 几乎不能丢数据 |
| 消息队列 | AOF everysec | 不能丢消息 |
| **大多数场景** | **RDB + AOF everysec** | 兼顾安全和性能 |

### Redis 的默认持久化配置是怎样的？

```bash
# 默认情况下，Redis 开启 RDB，不开启 AOF
save 900 1
save 300 10
save 60 10000

# AOF（默认关闭）
appendonly no
appendfsync everysec

# 混合模式（默认开启，Redis 5.0+）
aof-use-rdb-preamble yes
```

---

## 7. 常见错误

### 错误 1：AOF 文件损坏

Redis 在写 AOF 时如果崩溃，AOF 文件可能损坏。重启时 Redis 会尝试修复，如果修复失败：

```bash
# 手动修复 AOF 文件
redis-check-aof --fix appendonly.aof
```

AOF 是追加写的日志文件，如果最后一条不完整，Redis 可以丢掉这一条继续恢复。所以 AOF 文件损坏通常不会导致全部数据丢失。

### 错误 2：AOF 重写期间性能下降

BGREWRITEAOF 和 BGSAVE 类似，也是 fork 子进程执行。如果重写时内存写入量大：

- fork 引起毫秒级延迟（大内存时可能更长）
- 重写缓冲区膨胀（需要记录重写期间所有新写入）
- 磁盘 IO 变高（写入新 AOF 文件的同时可能还在写 RDB）

如果一个 BGSAVE 正在进行，再执行 BGREWRITEAOF，Redis 会让它们串行执行（不会同时跑两个 fork）。

### 错误 3：认为 AOF always 策略完全不会丢数据

`appendfsync always` 每次写命令后都 fsync，但如果 Redis 在 write() 成功但 fsync() 之前崩溃——最后一个命令还是可能丢。

不过在实际情况中，always 策略丢失的数据极少（最多一条命令），对大多数场景可以认为是"不丢"的。

### 错误 4：AOF 文件越来越大但不重写

如果 `auto-aof-rewrite-percentage` 设置得太高，或者 AOF 文件增长一直达不到触发条件，AOF 会变得巨大无比：

- 占用大量磁盘空间
- 恢复时非常慢（几 GB 甚至几十 GB 的 AOF 要逐条执行）
- 文件传输（cp/scp）很慢
- 磁盘读写压力增大

**建议**：开启自动重写，或定期手动执行 BGREWRITEAOF。

### 错误 5：RDB 和 AOF 同时启用时，Redis 用哪个恢复？

如果 RDB 和 AOF 同时开启，Redis 重启时**只使用 AOF 恢复**（AOF 包含更完整的数据）。

```bash
# 启动时 Redis 的恢复优先级
if AOF 开启（appendonly yes）:
    用 AOF 文件恢复
else 如果 RDB 文件存在:
    用 RDB 文件恢复
else:
    空数据库启动
```

> **注意**：虽然恢复时只用 AOF，但 RDB 在运行期间仍然有用——做定时备份、主从全量同步等。

---

## 8. 你学到了什么

| 概念 | 一句话 |
|------|--------|
| **AOF** | 把每次写操作记在本子上，断电后按本子重做 |
| **appendfsync always** | 每写一次就刷盘——最安全但最慢 |
| **appendfsync everysec** | 每秒刷一次盘——默认推荐，最多丢 1 秒数据 |
| **appendfsync no** | 让操作系统决定刷盘时机——最快但最不安全 |
| **AOF 重写（Rewrite）** | 读取内存当前状态，生成精简 AOF 文件，压缩日志 |
| **BGREWRITEAOF** | 手动触发 AOF 重写 |
| **RDB + AOF 混合** | AOF 文件 = RDB 快照头 + 增量 AOF 日志（Redis 4.0+） |
| **RDB vs AOF** | RDB = 拍照（快但可能丢数据）；AOF = 记日志（安全但慢） |

---

## 9. 自己动手

1. **查看当前 AOF 配置**：`redis-cli CONFIG GET appendonly` 检查是否开启
2. **查看 AOF 文件路径**：`redis-cli CONFIG GET appendfilename`（默认 appendonly.aof）
3. **手动开启 AOF**：`redis-cli CONFIG SET appendonly yes`（运行时开启，生产环境小心）
4. **查看 fsync 策略**：`redis-cli CONFIG GET appendfsync`
5. **写入一些数据**后检查 AOF 文件大小：`redis-cll INFO persistence | grep aof_current_size`
6. **触发 AOF 重写**：`redis-cli BGREWRITEAOF`，比较重写前后的 AOF 文件大小
7. **查看 AOF 文件内容**：`cat appendonly.aof`（纯文本，可以看到 RESP 协议格式）
8. **检查混合持久化配置**：`redis-cli CONFIG GET aof-use-rdb-preamble`
9. **运行 code.py**：`python s25_redis/s12_aof/code.py`，完整看 AOF 的工作流程

---

> **下一章：[s13: 主从复制](../s13_replication/)** — 从一块黑板到多块黑板，读写分离
