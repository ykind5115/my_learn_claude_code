# s29-06: 索引

[← 返回概览](../README.md) | [上一章：聚合查询](../s05_aggregate/) | [下一章：事务](../s07_transaction/)

> *"为什么查询突然从 0.01 秒变成了 10 秒？因为数据多了，没索引就要全表扫描。"*

---

## 问题 — 10 万行数据，查一次要扫全表

没有索引 → 数据库一行一行检查（全表扫描）。有了索引 → 像翻书的目录，直接跳到对应页。

---

## 原理

```sql
-- 创建索引: 像给这列建了个"快速查找目录"
CREATE INDEX idx_name ON products(name);

-- 之后这个查询就用索引了:
SELECT * FROM products WHERE name = 'apple';
-- 不用扫全表 → 直接定位 → 快几百倍
```

`EXPLAIN QUERY PLAN` 看查询计划：

```sql
EXPLAIN QUERY PLAN SELECT * FROM products WHERE name = 'apple';
-- SCAN products          <- 全表扫描 (没索引)
-- SEARCH products USING INDEX idx_name <- 用索引 (有索引)
```

### 索引的代价

- 占用磁盘空间
- INSERT/UPDATE/DELETE 变慢（要同时更新索引）
- **只为经常查的列建索引**，不要每列都建

---

## 试一下

```bash
python s29_sql/s06_index/code.py
```

---

## 小结

```sql
CREATE INDEX name ON table(col);      创建索引
EXPLAIN QUERY PLAN ...                查看是否用到索引
索引 = 快速查找目录, 空间换时间
只为 WHERE/JOIN/ORDER BY 的列建索引
```
