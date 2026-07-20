# s29-01: 建表与插入

[← 返回概览](../README.md) | [下一章：CRUD 完整操作](../s02_crud/)

> *"三句话入门 SQL：CREATE TABLE 建货架，INSERT INTO 放货，SELECT 看货。"*

---

## 问题 — 想把一组数据存起来，以后能查

```python
products = [
    (1, "apple", 3.5),
    (2, "banana", 2.0),
]
# 怎么查价格 > 3 的产品？怎么加新？怎么改？
```

用列表能存，但查起来要遍历。SQL 让你用**声明式**语言操作——你说"查价格>3的产品"，数据库负责找到它们。

---

## 三句话入门

```sql
-- 1. 建货架: 定义每列的名字和类型
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL
);

-- 2. 放货: 插入一行数据
INSERT INTO products (id, name, price) VALUES (1, 'apple', 3.5);

-- 3. 看货: 查询
SELECT * FROM products;
```

---

## 试一下

```bash
python s29_sql/s01_create_table/code.py
```

---

## 小结

```sql
CREATE TABLE name (col TYPE, ...);    建表
INSERT INTO name VALUES (...);        插入
SELECT col FROM name;                 查询
```
