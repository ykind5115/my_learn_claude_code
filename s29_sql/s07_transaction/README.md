# s29-07: 事务 — ACID

[← 返回概览](../README.md) | [上一章：索引](../s06_index/) | [下一章：Agent Memory 实战](../s08_agent_memory/)

> *"转账：A 扣 100，B 加 100。如果扣完 A 系统崩了，B 没收到怎么办？事务保证要么全做，要么全不做。"*

---

## 问题 — 多步操作中途崩溃了

```sql
-- 转账: A -> B 转 100
UPDATE accounts SET balance = balance - 100 WHERE name = 'A';
-- 此时系统崩溃!
UPDATE accounts SET balance = balance + 100 WHERE name = 'B';  -- 没执行
-- 结果: A 的钱凭空消失了
```

---

## 原理：事务 = 原子操作包

```sql
BEGIN;                            -- 开始事务
UPDATE accounts SET balance = balance - 100 WHERE name = 'A';
UPDATE accounts SET balance = balance + 100 WHERE name = 'B';
COMMIT;                           -- 提交 (两件事一起生效)
-- 如果中途崩溃 → ROLLBACK → 回到 BEGIN 之前的状态
```

### ACID 四个特性

| 字母 | 含义 | 解释 |
|------|------|------|
| **A**tomicity | 原子性 | 要么全做，要么全不做 |
| **C**onsistency | 一致性 | 数据库从一个合法状态到另一个合法状态 |
| **I**solation | 隔离性 | 并发事务互不干扰 |
| **D**urability | 持久性 | 提交了的数据就永远不会丢 |

---

## 试一下

```bash
python s29_sql/s07_transaction/code.py
```

---

## 小结

```sql
BEGIN    开始事务
COMMIT   提交 (生效)
ROLLBACK 回滚 (撤销)
ACID     原子性/一致性/隔离性/持久性
```
