# s25: Redis 实战 — 把数据放进共享黑板

[中文](README.md)

> *"Redis 不是一个数据库。Redis 是一块所有人都能读写的共享黑板。"*
>
> 本课程面向 **Redis 零基础**的学习者。不假设你用过任何缓存或 NoSQL 工具。
> 每一章只比上一章多一个概念，每一步都用「共享黑板」模型来解释「为什么」。
> 最终目标是：学完能用 Redis 解决缓存、队列、排行榜、分布式锁等真实场景问题，而且**真正理解每种数据结构在底层做了什么**。

---

## 为什么大多数 Redis 教程让人只会背命令？

传统的 Redis 教学是这样：

```
第 1 课: SET / GET / DEL          ← 你在背命令
第 2 课: LPUSH / RPOP / LRANGE    ← 你还在背命令
第 3 课: HSET / HGET / HGETALL    ← 你继续背命令
...
```

结果：背了 30 个命令，但一问「排行榜用什么数据结构？」「缓存穿透怎么解？」「持久化 RDB 和 AOF 什么时候用？」就懵了。

**本课程反其道而行之**：先用 s00 帮你建立一张「地图」——Redis 的共享黑板模型。这张图一旦刻在你脑子里，后面所有命令都会变得自然：

- `SET` = 在黑板上写一行字
- `EXPIRE` = 用消失墨水写字，到时间自动擦掉
- `LPUSH` + `BRPOP` = 黑板左边写、右边读，天然的消息队列
- `ZADD` + `ZRANGE` = 按分数排序的名单，天然的排行榜
- `RDB` = 给黑板拍一张照片存到硬盘
- `AOF` = 把每次写字动作记在本子上，断电后重做一遍

---

## 开始之前：你需要什么基础？

- 会用终端（命令行）—— 会 `cd`、`ls`、`mkdir` 就行
- 会用文本编辑器（VS Code 或任何编辑器）
- Python 3.x（用于运行演示脚本）
- 安装了 Redis：
  - **推荐方式 — Docker**：`docker run -d --name redis-demo -p 6379:6379 redis:7-alpine`
  - **Windows**：下载 Redis for Windows 或使用 WSL2 + Docker
  - **Mac**：`brew install redis && brew services start redis`
  - **Linux**：`sudo apt install redis-server`

> ❓ **完全零基础？** 从 [s00](s00_mental_model/) 开始 — 纯概念，不敲命令，帮你建立心智模型。
> 如果你已经知道「Redis 是干嘛的」，可以直接从 s01 开始。

---

## 学习路线图

```
s00  共享黑板心智模型       ← 纯概念，建立地图
 │
s01  第一次读写             ← 从这里开始敲命令（String + 基础操作）
s02  消失的墨水             ← 过期时间、TTL
s03  计数器与原子操作       ← INCR/DECR、并发安全
 │
s04  List — 队列与栈       ← 消息队列雏形
s05  Hash — 对象存储       ← 用户信息、配置项
s06  Set — 去重与集合      ← 标签、共同好友
s07  Sorted Set — 排行榜   ← 积分榜、延迟队列
 │
s08  缓存模式实战           ← Cache-Aside、穿透/击穿/雪崩
s09  分布式锁               ← SETNX → Redlock、看门狗
s10  限流与滑动窗口         ← 固定窗口、滑动窗口、令牌桶
 │
s11  持久化（上）— RDB     ← 给黑板拍快照
s12  持久化（下）— AOF     ← 记录每次写字，断电重放
 │
s13  主从复制               ← 多块黑板，读写分离
s14  Sentinel 哨兵          ← 主黑板坏了，副黑板自动顶上
s15  Cluster 集群           ← 一块黑板写不下？分片！
 │
s16  Pipeline 与事务        ← 批量操作、MULTI/EXEC/WATCH
s17  Pub/Sub 与 Stream      ← 发布订阅、可靠消息队列
 │
s18  深入原理               ← RESP 协议、内存编码、单线程事件循环
```

---

## 模块总览

### 🧭 第 0 章：心智模型

| # | 模块 | 要解决的问题 | 不写代码 |
|---|------|-------------|---------|
| s00 | [共享黑板心智模型](s00_mental_model/) | "Redis 到底是什么？为什么它这么快？和 MySQL 有什么区别？" | ✅ |

### ✏️ 第 1 章：打开黑板 — 基础操作

| # | 模块 | 要解决的问题 | 核心命令 |
|---|------|-------------|----------|
| s01 | [第一次读写](s01_first_read_write/) | "怎么把数据放进 Redis？怎么取出来？" | SET、GET、DEL、EXISTS、KEYS、TYPE |
| s02 | [消失的墨水](s02_expiration/) | "怎么让数据自动过期？Redis 怎么处理过期键？" | EXPIRE、TTL、PERSIST、EXPIREAT、过期策略 |
| s03 | [计数器与原子操作](s03_counter_atomic/) | "多个请求同时 +1，Redis 怎么保证不出错？" | INCR、DECR、INCRBY、INCRBYFLOAT、SETNX |

### 📋 第 2 章：黑板上的四种数据结构

| # | 模块 | 要解决的问题 | 核心命令 |
|---|------|-------------|----------|
| s04 | [List — 队列与栈](s04_list/) | "怎么做消息队列？怎么保留最新 N 条记录？" | LPUSH、RPUSH、LPOP、RPOP、LRANGE、LTRIM、BLPOP、BRPOP |
| s05 | [Hash — 对象存储](s05_hash/) | "怎么存用户信息？怎么只更新一个字段？" | HSET、HGET、HGETALL、HDEL、HINCRBY、HMGET、HMSET |
| s06 | [Set — 去重与集合运算](s06_set/) | "怎么给文章打标签？怎么找共同好友？" | SADD、SMEMBERS、SISMEMBER、SINTER、SUNION、SDIFF、SCARD |
| s07 | [Sorted Set — 排行榜](s07_sorted_set/) | "怎么做积分排行榜？怎么按时间排序？" | ZADD、ZRANGE、ZREVRANGE、ZRANK、ZSCORE、ZINCRBY、ZREMRANGEBYRANK |

### 🔥 第 3 章：实战三板斧

| # | 模块 | 要解决的问题 | 核心模式 |
|---|------|-------------|----------|
| s08 | [缓存模式实战](s08_cache_patterns/) | "缓存怎么和数据库配合？穿透/击穿/雪崩怎么解？" | Cache-Aside、布隆过滤器、互斥锁、随机过期 |
| s09 | [分布式锁](s09_distributed_lock/) | "多台服务器怎么保证同一时刻只有一个人在操作？" | SETNX → Redlock、看门狗、可重入锁 |
| s10 | [限流与滑动窗口](s10_rate_limiter/) | "API 怎么限制每人每分钟最多 100 次请求？" | 固定窗口、滑动窗口（ZSET）、令牌桶 |

### 💾 第 4 章：持久化 — 别让黑板断电就没了

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s11 | [RDB 快照](s11_rdb/) | "怎么给 Redis 数据拍照存盘？" | SAVE/BGSAVE、fork、写时复制、快照策略 |
| s12 | [AOF 日志](s12_aof/) | "怎么记录每次写操作，断电后重放？" | appendfsync、AOF 重写、RDB+AOF 混合持久化 |

### 🏗️ 第 5 章：高可用 — 一块黑板不够用

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s13 | [主从复制](s13_replication/) | "读写分离怎么做？从节点怎么追上主节点？" | replicaof、全量同步、增量同步、replication buffer |
| s14 | [Sentinel 哨兵](s14_sentinel/) | "主节点挂了怎么办？怎么自动切到备节点？" | 主观下线、客观下线、Leader 选举、故障转移 |
| s15 | [Cluster 集群](s15_cluster/) | "数据量大到一台机器装不下怎么办？" | 哈希槽（16384）、分片、MOVED/ASK、故障转移 |

### 🚀 第 6 章：进阶特性

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s16 | [Pipeline 与事务](s16_pipeline_tx/) | "100 次请求能不能压缩成 1 次网络往返？" | Pipeline、MULTI/EXEC、WATCH 乐观锁、Lua 脚本 |
| s17 | [Pub/Sub 与 Stream](s17_pubsub_stream/) | "怎么做实时推送？怎么做可靠消息队列？" | PUBLISH/SUBSCRIBE、Stream、消费组、ACK |

### 🔬 第 7 章：深入原理

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s18 | [深入原理](s18_internals/) | "Redis 单线程为什么这么快？RESP 协议长什么样？内存里数据怎么编码的？" | RESP、事件循环、ziplist/listpack/skiplist、渐进式 rehash |

---

## 如何使用本课程

### 学习节奏

每个模块按这个顺序：

1. **读 README 的「为什么」部分** — 理解这个模块要解决什么问题
2. **读 README 的「黑板模型」部分** — 用一张图理解核心概念
3. **运行 code.py** — 看实际效果，每一步都可视化黑板状态
4. **自己在 redis-cli 里复现** — 跟着 code.py 的输出，在自己的终端里敲同样的命令
5. **做「自己动手」练习** — 每个模块末尾有练习，一定要做
6. **再读一遍 README** — 此时有些概念你会理解得更深

### 不要跳章

每个模块的概念都依赖前一个模块。跳着学 = 浪费时间。

### 每个 code.py 做了什么？

每个 `code.py` 是一个**自动化演示脚本**：

1. 连接本地 Redis（或 Docker Redis）
2. 逐步执行 Redis 命令
3. **每一步都打印「黑板」的可视化状态**
4. 用彩色输出区分命令、解释、结果

```bash
# 运行某个章节的演示
python s25_redis/s01_first_read_write/code.py
```

### 遇到不懂的先记下来

有些概念（比如「持久化」、「哨兵」、「哈希槽」）第一次听到不懂很正常。先记下来，继续往后学，回头再看往往豁然开朗。

---

## 快速开始

```bash
# 1. 确认 Redis 可用
redis-cli ping    # 应该返回 PONG

# 如果没有 Redis，用 Docker 启动一个：
docker run -d --name redis-demo -p 6379:6379 redis:7-alpine

# 2. 安装 Python 客户端
pip install redis

# 3. 从概念章开始（纯阅读，不敲命令）
# 打开 s25_redis/s00_mental_model/README.md

# 4. 运行第一个演示
python s25_redis/s01_first_read_write/code.py
```

---

## 和 s23_git 的对照

| s23_git | s25_redis |
|---------|-----------|
| 时间树模型 | 共享黑板模型 |
| 工作区 → 暂存区 → 仓库 | 内存黑板 → RDB/AOF 持久化 |
| commit = 树上种节点 | SET = 黑板上写字 |
| branch = 可移动标签 | 数据结构 = 不同组织方式 |
| merge = 时间线汇合 | SINTER/SUNION = 集合汇合 |
| remote = 分享时间线 | 主从复制 = 多块黑板同步 |
| rebase = 嫁接历史 | AOF 重写 = 精简日志 |
| .git 内部对象模型 | RESP 协议 + 内存编码 |

---

## 和 learn-claude-code 项目的关系

本课程是 learn-claude-code 仓库中的 s25，和主项目遵循同样的学习理念：

| learn-claude-code | s25_redis |
|-------------------|-----------|
| Agent Loop = 一切的基础 | 共享黑板 = 一切的基础 |
| 渐进式添加工具 | 渐进式添加数据结构 |
| 每章一个可运行的 Agent | 每章一个可运行的演示 |
| Harness 层的概念 | 黑板层的概念 |
| 从简单到复杂，不跳步 | 从简单到复杂，不跳步 |
