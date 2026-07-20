# s29-02: CRUD 完整操作

[← 返回概览](../README.md) | [上一章：建表与插入](../s01_create_table/) | [下一章：过滤与排序](../s03_filter_sort/)

> *"增删改查——数据库的四大基本操作。UPDATE 改、DELETE 删、INSERT 增、SELECT 查。"*

---

## 问题 — 数据不是一成不变的

价格变了要改，商品下架要删，新品要加。SQL 有四种操作覆盖所有场景。

---

## CRUD 四件套

| 操作 | SQL | 仓库比喻 |
|------|-----|---------|
| **C**reate | `INSERT INTO` | 放一件新货上架 |
| **R**ead | `SELECT` | 看货架上有啥 |
| **U**pdate | `UPDATE ... SET` | 改货物标签 |
| **D**elete | `DELETE FROM` | 把货从货架拿走 |

```sql
-- Create
INSERT INTO products VALUES (4, 'grape', 5.0);

-- Read
SELECT * FROM products WHERE price > 3.0;

-- Update
UPDATE products SET price = 4.5 WHERE name = 'apple';

-- Delete
DELETE FROM products WHERE name = 'banana';
```

**WHERE 很重要**：`UPDATE` 和 `DELETE` 如果不带 WHERE → 全表遭殃！

---

## 试一下

```bash
python s29_sql/s02_crud/code.py
```

---

## 小结

```
INSERT  = 增 (Create)
SELECT  = 查 (Read)
UPDATE  = 改 (Update)
DELETE  = 删 (Delete)
WHERE   = 限定范围 (不带 WHERE 改全表!)
```
