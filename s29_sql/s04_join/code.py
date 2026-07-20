#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s29-04: 多表联查 — JOIN"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, get_db, run_sql, print_step, print_sql,
                   print_table, print_note, print_key_point, print_section)


def demo_all():
    db = get_db()
    db.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)")
    db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, product_id INTEGER, qty INTEGER)")
    db.executemany("INSERT INTO products VALUES (?,?,?)",
                   [(1, "apple", 3.5), (2, "banana", 2.0), (3, "orange", 4.0)])
    db.executemany("INSERT INTO orders VALUES (?,?,?)",
                   [(1, 1, 10), (2, 1, 5), (3, 99, 1)])  # product_id=99 不存在!

    print(f"  产品表:")
    print_table(run_sql(db, "SELECT * FROM products"))
    print(f"  订单表:")
    print_table(run_sql(db, "SELECT * FROM orders"))

    print_step(1, "INNER JOIN — 只保留匹配的")
    sql = """SELECT o.id AS order_id, p.name, o.qty
FROM orders o
INNER JOIN products p ON o.product_id = p.id"""
    print_sql(sql)
    print_table(run_sql(db, sql))
    print_note("order #3 (product_id=99) 被丢弃了 — 产品不存在")

    print_step(2, "LEFT JOIN — 保留左表全部")
    sql = """SELECT o.id AS order_id,
       COALESCE(p.name, 'UNKNOWN') AS name,
       o.qty
FROM orders o
LEFT JOIN products p ON o.product_id = p.id"""
    print_sql(sql)
    print_table(run_sql(db, sql))
    print_note("order #3 保留了 — 产品名填 NULL")

    print_step(3, "JOIN 类型对比")
    print(f"  INNER JOIN:  A ∩ B   (交集)")
    print(f"  LEFT JOIN:    A 全部  (B 没匹配的填 NULL)")
    print(f"  CROSS JOIN:   A × B   (笛卡尔积, 慎用)")

    db.close()


if __name__ == "__main__":
    print_section("s29-04: 多表联查 — JOIN")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("INNER JOIN = 两边匹配才留")
    print_key_point("LEFT JOIN = 左表全留, 右边没的为 NULL")
