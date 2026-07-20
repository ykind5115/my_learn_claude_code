# s29-03: 过滤与排序

[← 返回概览](../README.md) | [上一章：CRUD](../s02_crud/) | [下一章：多表联查](../s04_join/)

> *"100 万行数据，你只想要价格 > 100 的前 10 个。WHERE 筛选，ORDER BY 排序，LIMIT 截断。"*

---

## 问题 — 数据太多，只想要符合条件的几条

`SELECT * FROM products` 返回全部。你需要过滤、排序、分页。

---

## 核心语法

```sql
SELECT name, price
FROM products
WHERE price > 3.0          -- 只要价格 > 3 的
  AND name LIKE '%e%'       -- 名字含 'e' 的
ORDER BY price DESC         -- 按价格从高到低
LIMIT 10;                   -- 只要前 10 条
```

### WHERE 运算符

| 运算符 | 含义 | 示例 |
|--------|------|------|
| `=` `!=` `>` `<` `>=` `<=` | 比较 | `price > 100` |
| `AND` `OR` `NOT` | 逻辑 | `price > 100 AND stock > 0` |
| `LIKE` | 模糊匹配 | `name LIKE '%apple%'` |
| `IN` | 在列表中 | `category IN ('food', 'drink')` |
| `BETWEEN` | 范围 | `price BETWEEN 10 AND 100` |

### ORDER BY + LIMIT

```sql
ORDER BY price DESC   -- 从高到低
ORDER BY name ASC     -- 从 A 到 Z
LIMIT 10              -- 只要前 10 条
LIMIT 10 OFFSET 20    -- 跳过 20 条，取 10 条 (第 3 页)
```

---

## 试一下

```bash
python s29_sql/s03_filter_sort/code.py
```

---

## 小结

```
WHERE      筛选条件 (>, <, =, LIKE, IN, BETWEEN)
AND / OR    组合条件
ORDER BY   排序 (ASC/DESC)
LIMIT      截断结果
OFFSET     跳过前面的行 (分页)
```
