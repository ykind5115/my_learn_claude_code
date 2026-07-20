# s29-04: 多表联查 — JOIN

[← 返回概览](../README.md) | [上一章：过滤与排序](../s03_filter_sort/) | [下一章：聚合查询](../s05_aggregate/)

> *"两张表的数据怎么关联查询？JOIN——把两个货架按关系拼成一张大表。"*

---

## 问题 — 订单表里的 product_id 对应产品表的哪件货？

订单表只存了 `product_id`，你需要同时看到产品名称和价格。这就是 JOIN 的用武之地。

---

## 原理：INNER JOIN vs LEFT JOIN

```
products                      orders
id │ name    │ price          id │ product_id │ qty
───┼─────────┼──────          ───┼────────────┼─────
 1 │ apple   │ 3.5             1 │ 1          │ 10
 2 │ banana  │ 2.0             2 │ 1          │ 5
 3 │ orange  │ 4.0             3 │ 99         │ 1  (无效product_id!)
```

```sql
-- INNER JOIN: 只保留两边都匹配的行
SELECT o.id, p.name, o.qty
FROM orders o
INNER JOIN products p ON o.product_id = p.id;
-- 结果: order#1=apple, order#2=apple  (order#3 被丢弃, product_id=99 不存在)

-- LEFT JOIN: 保留左表全部行, 右表没匹配的填 NULL
SELECT o.id, p.name, o.qty
FROM orders o
LEFT JOIN products p ON o.product_id = p.id;
-- 结果: order#1=apple, order#2=apple, order#3=NULL
```

---

## 试一下

```bash
python s29_sql/s04_join/code.py
```

---

## 小结

```sql
INNER JOIN  -- 两边都有才保留
LEFT JOIN   -- 左表全部保留, 右表没匹配填 NULL
ON          -- 指定关联条件 (通常是 FK = PK)
```
