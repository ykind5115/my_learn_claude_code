#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s29-05: 聚合查询 — GROUP BY"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, get_db, run_sql, print_step, print_sql,
                   print_table, print_note, print_key_point, print_section)


def demo_all():
    db = get_db()
    db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, product_id INTEGER, qty INTEGER, price REAL)")
    items = [(1, 1, 10, 3.5), (2, 1, 5, 3.5), (3, 2, 20, 2.0),
             (4, 2, 15, 2.0), (5, 3, 3, 4.0)]
    db.executemany("INSERT INTO orders VALUES (?,?,?,?)", items)

    print(f"  订单表: {len(items)} 条")
    print_table(run_sql(db, "SELECT * FROM orders"))

    print_step(1, "COUNT — 计数")
    sql = "SELECT COUNT(*) AS total_orders FROM orders"
    print_sql(sql)
    print_table(run_sql(db, sql))

    print_step(2, "GROUP BY — 分组统计")
    sql = """SELECT product_id,
       SUM(qty) AS total_qty,
       COUNT(*) AS order_count
FROM orders
GROUP BY product_id"""
    print_sql(sql)
    print_table(run_sql(db, sql))

    print_step(3, "AVG / MAX / MIN")
    sql = """SELECT
    AVG(price) AS avg_price,
    MAX(price) AS max_price,
    MIN(price) AS min_price
FROM orders"""
    print_sql(sql)
    print_table(run_sql(db, sql))

    print_step(4, "HAVING — 分组后筛选")
    sql = """SELECT product_id, SUM(qty) AS total
FROM orders
GROUP BY product_id
HAVING total > 10"""
    print_sql(sql)
    print_table(run_sql(db, sql))
    print_note("WHERE 在分组前筛选, HAVING 在分组后筛选")

    db.close()


if __name__ == "__main__":
    print_section("s29-05: 聚合查询")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("COUNT/SUM/AVG/MAX/MIN = 聚合函数")
    print_key_point("GROUP BY = 分组, HAVING = 分组后筛选")
