# s29: SQL 基础 — 把数据装进仓库

[中文](README.md)

> *"SQL 不只是一堆 SELECT 语句。SQL 是一种思维方式——把数据看成有结构、有关联的仓库。"*

本课程面向 **SQL 零基础**的学习者。用 SQLite（Python 自带，零安装）教学。
每一章只加一个新概念，每一步都用「数据仓库」模型解释「为什么」。
最终目标：能设计 Agent 的 memory 表，写出高效的增删改查。

---

## 为什么大多数 SQL 教程让人学不会？

上来就甩一堆语法：CREATE TABLE、ALTER、GRANT、TRIGGER、VIEW……全是 DDL。然后让你背十几个函数。

你背下来了，但不知道为什么表要这样设计，为什么查询慢，为什么需要索引。

**本课程反其道而行之**：先用 s00 建立「数据仓库」心智模型。s01 只写 `CREATE TABLE + INSERT + SELECT` 三句话。每章只加一个新概念。最后 s08 把学的全串起来——设计一个 Agent Memory 系统。

---

## 开始之前

- Python 基础
- 什么都不用装——sqlite3 是 Python 标准库

> 从 [s00](s00_mental_model/) 开始 — 纯概念。

---

## 学习路线图

```
s00  心智模型：数据仓库           <- 表=货架, 行=货物, 索引=目录
s01  建表与插入                   <- CREATE TABLE + INSERT + SELECT
s02  CRUD 完整操作                <- UPDATE + DELETE + INSERT OR REPLACE
s03  过滤与排序                   <- WHERE, ORDER BY, LIMIT
s04  多表联查                     <- INNER JOIN, LEFT JOIN
s05  聚合查询                     <- GROUP BY, COUNT/SUM/AVG, HAVING
s06  索引                         <- CREATE INDEX, EXPLAIN, 速度对比
s07  事务                         <- BEGIN/COMMIT/ROLLBACK, ACID
s08  Agent Memory 实战            <- 完整 memory 表 + CRUD
```

---

## 模块总览

### 第 0 章：心智模型

| # | 模块 | 要解决的问题 | 不写代码 |
|---|------|-------------|---------|
| s00 | [数据仓库](s00_mental_model/) | "数据库和 Excel 有什么区别？" | YES |

### 第 1 章：基础操作

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s01 | [建表与插入](s01_create_table/) | "怎么创建表、插入数据？" | CREATE TABLE, INSERT, SELECT |
| s02 | [CRUD](s02_crud/) | "增删改查怎么写？" | UPDATE, DELETE, WHERE |
| s03 | [过滤与排序](s03_filter_sort/) | "怎么查符合条件的？" | WHERE, LIKE, ORDER BY, LIMIT |

### 第 2 章：进阶查询

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s04 | [多表联查](s04_join/) | "两张表怎么关联？" | INNER JOIN, LEFT JOIN, FK |
| s05 | [聚合查询](s05_aggregate/) | "怎么分组统计？" | GROUP BY, HAVING, COUNT/SUM/AVG |

### 第 3 章：性能与实战

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s06 | [索引](s06_index/) | "为什么查询慢了？" | CREATE INDEX, EXPLAIN, B-Tree |
| s07 | [事务](s07_transaction/) | "转账到一半崩了？" | BEGIN/COMMIT/ROLLBACK, ACID |
| s08 | [Agent Memory](s08_agent_memory/) | "Agent 怎么用 SQLite？" | 完整表设计 + CRUD |

---

## 快速开始

```bash
python s29_sql/s01_create_table/code.py
```

---

## 跟 Agent 的关系

| SQL 概念 | Agent 场景 |
|---------|-----------|
| SQLite | s09 Memory 系统存储后端 |
| CRUD | 记忆的增删改查 |
| 索引 | 大量记忆快速检索 |
| 事务 | 记忆写入原子性保证 |
| JOIN | 关联记忆与对话 |
