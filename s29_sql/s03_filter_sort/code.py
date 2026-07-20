#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s29-03: 过滤与排序"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, get_db, run_sql, print_step, print_sql,
                   print_table, print_note, print_key_point, print_section)


def demo_all():
    db = get_db()
    db.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)")
    items = [(1, "apple", 3.5, 100), (2, "banana", 2.0, 0), (3, "orange", 4.0, 50),
             (4, "grape", 5.0, 200), (5, "mango", 8.0, 30), (6, "peach", 3.0, 0)]
    db.executemany("INSERT INTO products VALUES (?,?,?,?)", items)
    print(f"  初始数据: {len(items)} 件商品")
    print_table(run_sql(db, "SELECT * FROM products"))

    print_step(1, "WHERE — 条件筛选")
    sql = "SELECT * FROM products WHERE price > 3.0"
    print_sql(sql)
    print_table(run_sql(db, sql))
    print_note("价格 > 3 的商品")

    print_step(2, "AND — 多条件")
    sql = "SELECT * FROM products WHERE price > 3.0 AND stock > 0"
    print_sql(sql)
    print_table(run_sql(db, sql))
    print_note("价格 > 3 且有库存")

    print_step(3, "LIKE — 模糊匹配")
    sql = "SELECT * FROM products WHERE name LIKE '%a%'"
    print_sql(sql)
    print_table(run_sql(db, sql))
    print_note("%a% = 名字含 'a' 的")

    print_step(4, "ORDER BY — 排序")
    sql = "SELECT name, price FROM products ORDER BY price DESC"
    print_sql(sql)
    print_table(run_sql(db, sql))
    print_note("DESC=降序(高到低), ASC=升序")

    print_step(5, "LIMIT + OFFSET — 分页")
    sql = "SELECT * FROM products ORDER BY price DESC LIMIT 2 OFFSET 0"
    print_sql(sql)
    print(f"  第 1 页:")
    print_table(run_sql(db, sql))
    sql2 = "SELECT * FROM products ORDER BY price DESC LIMIT 2 OFFSET 2"
    print_sql(sql2)
    print(f"  第 2 页:")
    print_table(run_sql(db, sql2))

    db.close()


if __name__ == "__main__":
    print_section("s29-03: 过滤与排序")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("WHERE=筛选 ORDER BY=排序 LIMIT=截断 OFFSET=跳过")
