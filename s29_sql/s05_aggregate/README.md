# s29-05: 聚合查询 — GROUP BY

[← 返回概览](../README.md) | [上一章：JOIN](../s04_join/) | [下一章：索引](../s06_index/)

> *"这些产品一共卖了多少件？每个品类平均价格多少？GROUP BY 分组统计。"*

---

## 问题 — 你看的不是一行一行，而是整体趋势

"总共多少订单？""每个产品卖了多少？""哪个产品最畅销？"——这些不是查一行，而是统计。

---

## 聚合函数

| 函数 | 作用 | 示例 |
|------|------|------|
| `COUNT(*)` | 数行数 | `COUNT(*)` → 100 |
| `SUM(col)` | 求和 | `SUM(qty)` → 总销量 |
| `AVG(col)` | 平均值 | `AVG(price)` → 平均价格 |
| `MAX(col)` | 最大值 | `MAX(price)` → 最贵 |
| `MIN(col)` | 最小值 | `MIN(price)` → 最便宜 |

### GROUP BY — 分组统计

```sql
SELECT product_id, SUM(qty) AS total_sold
FROM orders
GROUP BY product_id;
-- product_id=1: 卖了 15 件
-- product_id=99: 卖了 1 件
```

### HAVING — 过滤分组结果

`WHERE` 在分组**前**筛选，`HAVING` 在分组**后**筛选：

```sql
SELECT product_id, SUM(qty) AS total
FROM orders
GROUP BY product_id
HAVING total > 10;    -- 只要总销量 > 10 的产品
```

---

## 试一下

```bash
python s29_sql/s05_aggregate/code.py
```

---

## 小结

```
聚合函数: COUNT/SUM/AVG/MAX/MIN
GROUP BY: 按某列分组统计
HAVING:   分组后筛选 (WHERE 是分组前)
```
