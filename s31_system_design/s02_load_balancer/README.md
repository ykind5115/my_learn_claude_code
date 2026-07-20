# s31-02: 负载均衡

[← 返回概览](../README.md) | [上一章：单体 vs 微服务](../s01_monolith_vs_micro/) | [下一章：缓存策略](../s03_cache_strategies/)

> *"10 台服务器，1000 个请求，怎么分配？轮询、随机、加权——三种策略。"*

---

## 策略对比

| 策略 | 原理 | 适用 |
|------|------|------|
| 轮询 (Round Robin) | 1→2→3→1→2→3 循环 | 服务器性能一致 |
| 随机 (Random) | 随机选一台 | 大量请求时趋近均匀 |
| 加权 (Weighted) | 性能好的分更多请求 | 服务器配置不同 |

---

## 试一下

```bash
python s31_system_design/s02_load_balancer/code.py
```
