# s14: Sentinel 哨兵 — 自动故障转移

[s13](../s13_replication/) → `s14` → [s15](../s15_cluster/)
> *"监控员盯着所有黑板 — 哪块坏了马上报告，投票选新主板。"*
>
> **前提知识**: 理解主从复制（s13）。

---

## 1. 为什么需要 Sentinel？

s13 中我们学了主从复制——主黑板负责写，从黑板负责读。

但有一个致命问题：**主节点挂了怎么办？**

```
主节点挂了之后：
  1. 运维人员发现报警（可能在凌晨 3 点）
  2. 登录服务器检查
  3. 执行 REPLICAOF NO ONE 把从升为主
  4. 修改其他从节点的配置
  5. 修改客户端的连接配置

这个过程可能需要 5~30 分钟！
在这段时间里，写入服务完全不可用。
```

**Sentinel（哨兵） = 一个自动监控 + 自动故障转移的系统。**

```
主节点挂了 → Sentinel 检测到 → 自动选举新主 → 通知所有节点和客户端
                  ↓
            全程无人值守，通常 10~30 秒完成
```

---

## 2. 在黑板模型下理解 Sentinel

### 核心角色

```
┌──────────────────────────────────────────────────────────┐
│                     Sentinel 监控层                        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │ Sentinel1 │    │ Sentinel2 │    │ Sentinel3 │          │
│  └─────┬────┘    └─────┬────┘    └─────┬────┘           │
│        │               │               │                 │
│        └───────┬───────┘               │                 │
│                │ 互相通信，交换意见       │                 │
│                └──────────┬────────────┘                 │
└───────────────────────────│──────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │  主节点   │  │  从节点1  │  │  从节点2  │
        │ (Master)  │  │ (Replica)│  │ (Replica)│
        └──────────┘  └──────────┘  └──────────┘
```

### 一个比喻

```
教室里有 3 个监控员:

  监控员 A: 盯着主黑板
  监控员 B: 盯着主黑板
  监控员 C: 盯着主黑板

  突然，A 发现主黑板 5 秒没更新了
    → A 觉得「主黑板可能坏了」(主观下线)

  A 告诉 B 和 C：「你们看看主黑板还活着吗？」

  如果 B 和 C 也发现主黑板联系不上
    → 2/3 投票通过「主黑板确实坏了」(客观下线)
    → 开始故障转移

  选谁当新主？
    → 3 个监控员投票选一个从节点升为主
    → 通知另一个从节点去复制新主
    → 通知客户端：「主节点地址已变」
```

---

## 3. Sentinel 架构

### 最少 3 个 Sentinel

Sentinel 本身也是一个分布式系统——它需要**多个实例互相通信**来做出决策。

```
❌ 1 个 Sentinel：
    Sentine 自己挂了 → 没人监控
    或者网络抖动 → Sentinel 误判主节点挂了

❌ 2 个 Sentinel：
    其中一个觉得主挂了 → 只有 1 票，不到半数
    永远无法达成共识

✅ 3 个 Sentinel（推荐）：
    需要至少 2 票才能判定故障 → 防止误判
    挂 1 个还能继续工作
    挂 2 个 → 只能读不能切
```

### Sentinel 的端口

- **Redis 实例**：6379（主）、6380、6381（从）
- **Sentinel 实例**：26379、26380、26381

> Sentinel 和 Redis 是独立的进程，只是 Sentinel 中配置了要监控的 Redis 地址。

---

## 4. 故障检测 — SDOWN → ODOWN

### 主观下线 (SDOWN — Subjectively DOWN)

每个 Sentinel 独立检测：

```redis
# Sentinel 配置：多久没响应算主观下线
sentinel down-after-milliseconds mymaster 5000
```

- Sentinel 每隔 1 秒向 Redis 发 PING
- 如果超过 `down-after-milliseconds`（默认 5 秒）没收到 PONG
- 这个 Sentinel 就认为 **「我这边看，主节点可能挂了」**
- 这就是 **主观下线 (SDOWN)**

### 客观下线 (ODOWN — Objectively DOWN)

需要多个 Sentinel 达成共识：

```
Sentinel A: 「我觉得主节点挂了」 → SDOWN
  │
  ├── 用 SENTINEL is-master-down-by-addr 询问其他 Sentinel
  │
  ├── Sentinel B: 「我也联系不上」   → 同意
  ├── Sentinel C: 「我也联系不上」   → 同意
  │
  └── 3 个 Sentinel 中 3 个都同意 → 超过半数 (2/3)
                        ↓
                 客观下线 (ODOWN)
                        ↓
                 开始故障转移
```

### 为什么需要两阶段？

```
场景：Sentinel A 和主节点之间的网络恰好断了
      Sentinel B 和 Sentinel C 都能连上主节点

  Sentinel A: 主观下线 (它只看自己的视角)
  Sentinel B: 联系不上 A，但能连主节点 →「主还活着」
  Sentinel C: 联系不上 A，但能连主节点 →「主还活着」

  只有 1/3 投票 → 不能达成客观下线 → 不切换

  结果：避免了因单点网络故障导致的误切换 ✅
```

---

## 5. 故障转移流程

### 完整流程（约 10~30 秒）

```
时间线
  │
  ├── T0:  主节点挂了（停电、进程崩溃、网络分区）
  │
  ├── T+5s: Sentinel A 发现主节点没响应 → SDOWN
  │         Sentinel B 发现主节点没响应 → SDOWN
  │         Sentinel C 发现主节点没响应 → SDOWN
  │
  ├── T+6s: Sentinel A 发起投票
  │         询问 B 和 C：「主节点是否真的挂了？」
  │
  ├── T+7s: B 和 C 确认 → 3/3 达成 ODOWN
  │
  ├── T+8s: Sentinel 们开始选举 Leader
  │         （谁来做故障转移的指挥官？）
  │         使用 Raft 算法选出一个 Leader Sentinel
  │
  ├── T+9s: Leader Sentinel 选定新主节点
  │         从从节点中选一个：
  │           - 优先选 slave_priority 最高的
  │           - 再选 offset 最大的（数据最新的）
  │           - 再选 runid 最小的
  │
  ├── T+10s: Leader Sentinel 执行：
  │           REPLICAOF NO ONE     → 从节点升为主
  │           REPLICAOF new-master → 其他从节点指向新主
  │
  ├── T+11s: 原主节点恢复后，自动成为新主的从节点
  │
  └── T+12s: 故障转移完成 ✅
```

### 选新主的规则

```
从节点列表（按优先级排序）:

  从节点 A: priority=1, offset=10000, runid=aaa
  从节点 B: priority=2, offset=9800,  runid=bbb
  从节点 C: priority=1, offset=9900,  runid=ccc

  选举过程:
    1. 淘汰 priority=0 的（永远不参与选举）
    2. 按 priority 排序: A(1) C(1) B(2)
    3. A 和 C 的 priority 相同 → 比 offset
    4. A(10000) > C(9900) → A 数据更新
    5. 选定 A 为新主节点 ✅
```

### 通知客户端

故障转移后，客户端如何知道新主节点的地址？

**方案一：客户端直接问 Sentinel**

```python
from redis.sentinel import Sentinel

sentinel = Sentinel([('sentinel-host', 26379)])
# Sentinel 自动返回当前主节点的地址
master = sentinel.master_for('mymaster')
slave = sentinel.slave_for('mymaster')
```

**方案二：客户端订阅 Sentinel 的频道**

```redis
SUBSCRIBE +switch-master    ← 当主节点切换时收到通知
```

---

## 6. Sentinel 配置详解

### sentinel.conf

```redis
# 监控的 Redis 主节点
# sentinel monitor <name> <ip> <port> <quorum>
sentinel monitor mymaster 192.168.1.10 6379 2
#                              主节点地址       ↑ quorum

# 多久没响应算主观下线（毫秒）
sentinel down-after-milliseconds mymaster 5000

# 故障转移超时（毫秒）
sentinel failover-timeout mymaster 180000

# 同时可向几个从节点发 REPLICAOF（并行复制）
sentinel parallel-syncs mymaster 1

# 保护：密码认证
# sentinel auth-pass mymaster YourPassword
```

### 配置项详解

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `sentinel monitor` | — | 监控的主节点名称、地址、端口、投票数 |
| `quorum` | 2 | 判定 ODOWN 需要的最少投票数 |
| `down-after-milliseconds` | 30000 | 多少毫秒无响应算主观下线 |
| `failover-timeout` | 180000 | 故障转移超时 |
| `parallel-syncs` | 1 | 同时同步的从节点数（越大压力越大） |
| `auth-pass` | — | 如果 Redis 有密码，这里配置 |

### quorum 选多少？

```redis
# 3 个 Sentinel → quorum=2
sentinel monitor mymaster 192.168.1.10 6379 2

# 5 个 Sentinel → quorum=3
sentinel monitor mymaster 192.168.1.10 6379 3
```

> quorum 建议设为 `N/2 + 1`（半数以上）。3 个 Sentinel 设 2，5 个设 3。

---

## 7. 常见错误

### ❌ 错误 1：Sentinel 数量是偶数

```
2 个 Sentinel:
  网络分区 → 各 1 票 → 永远无法达成多数
  需要人工介入

4 个 Sentinel:
  挂 1 个 + 网络分区 → 各 2 票 → 平局
  也无法达成多数
```

> **规则**：Sentinel 数量用奇数。3 或 5 最常用。

### ❌ 错误 2：网络分区导致脑裂（Split-Brain）

```
网络分区前:
  主：192.168.1.10
  从：192.168.1.11, 192.168.1.12

网络分区后:
  分区 A: 主节点 192.168.1.10 + Sentinel1（和外界断了）
  分区 B: 从节点 192.168.1.11, 192.168.1.12 + Sentinel2, Sentinel3

  分区 B 中 2/3 判定主挂了 → 把 192.168.1.11 升为新主
  分区 A 中 主节点还在正常服务
    → 出现两个主节点「同时存在」= 脑裂
```

**影响**：分区 A 中客户端写入的数据，分区恢复后会丢失（因为新主会覆盖这些数据）。

**对策**：
- 配置 `min-replicas-to-write` 和 `min-replicas-max-lag`：

```redis
# 主节点至少要有 1 个从节点在线且延迟 < 10 秒
# 否则主节点拒绝写入（防止脑裂期间的数据丢失）
min-replicas-to-write 1
min-replicas-max-lag 10
```

### ❌ 错误 3：quorum 设得太大

```
5 个 Sentinel → quorum=5
意思：必须 5 个 Sentinel 全票通过才能判定主挂了

如果任何 1 个 Sentinel 挂了
→ 永远凑不齐 5 票
→ 主节点真挂了也无法触发故障转移
```

> quorum 建议设为 N/2+1（超过半数即可），不是全部。

### ❌ 错误 4：故障转移后客户端不更新地址

老旧的客户端实现可能硬编码了主节点 IP。故障转移后，主节点地址变了，客户端还在连原来的 IP。

> **使用 Sentinel-aware 客户端**（如 redis-py 的 Sentinel 模式），或者用 DNS + 短 TTL。

---

## 8. 你学到了什么

| 概念 | 一句话 |
|------|--------|
| Sentinel | 监控 Redis 主从健康，自动故障转移 |
| SDOWN | 一个 Sentinel 发现主节点无响应 |
| ODOWN | 多个 Sentinel 投票确认主节点挂了 |
| quorum | 判定 ODOWN 需要的最少票数 |
| Raft 选举 | Sentinel 之间选出一个 Leader 来执行故障转移 |
| 故障转移 | 选新主 → 切换从 → 通知客户端，全程自动 |
| 脑裂 | 网络分区导致两个主节点同时存在 |
| min-replicas | 限制主节点在没有足够从节点时拒绝写入 |

---

## 9. 自己动手

1. **搭建最小 Sentinel 集群**：启动 1 主 2 从 + 3 个 Sentinel（全部在本地，不同端口）
2. **测试自动切换**：手动停掉主节点，观察 Sentinel 自动选新主
3. **查看 Sentinel 日志**：观察 SDOWN → ODOWN → 选举 → 切换的完整过程
4. **模拟网络分区**：用 `iptables` 或防火墙规则切断主节点和部分 Sentinel 的连接，观察是否触发切换
5. **使用 redis-py 的 Sentinel 模式**：写一个 Python 脚本，通过 Sentinel 获取主节点地址并执行写入
6. **思考**：如果你的业务场景允许 1 分钟的数据写入不可用，是否还需要 Sentinel？

---

> **下一章：[s15: Cluster 集群](../s15_cluster/)** — 一块黑板写不下？切分成 16384 块拼图
