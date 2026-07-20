#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s29-02: CRUD 完整操作"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, get_db, run_sql, print_step, print_sql,
                   print_table, print_note, print_key_point, print_section)


def demo_all():
    db = get_db()
    db.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)")
    db.executemany("INSERT INTO products VALUES (?,?,?)",
                   [(1, "apple", 3.5), (2, "banana", 2.0), (3, "orange", 4.0)])

    print_step(1, "C = Create (INSERT)")
    sql = "INSERT INTO products VALUES (4, 'grape', 5.0)"
    print_sql(sql)
    db.execute(sql)
    print_table(run_sql(db, "SELECT * FROM products"))

    print_step(2, "R = Read (SELECT)")
    sql = "SELECT * FROM products WHERE price > 3.0"
    print_sql(sql)
    print_table(run_sql(db, sql))
    print_note("只查价格 > 3 的产品")

    print_step(3, "U = Update (UPDATE)")
    sql = "UPDATE products SET price = 4.5 WHERE name = 'apple'"
    print_sql(sql)
    db.execute(sql)
    print_table(run_sql(db, "SELECT * FROM products"))
    print_note("apple 价格从 3.5 涨到 4.5")

    print_step(4, "D = Delete (DELETE)")
    sql = "DELETE FROM products WHERE name = 'banana'"
    print_sql(sql)
    db.execute(sql)
    print_table(run_sql(db, "SELECT * FROM products"))
    print_note("banana 下架了")

    print_step(5, "WHERE 的重要性")
    print(f"  UPDATE products SET price = 0    -> 所有产品价格变 0!")
    print(f"  DELETE FROM products              -> 清空整个表!")
    print(f"  不带 WHERE -> 全表操作 -> 危险!")

    db.close()


if __name__ == "__main__":
    print_section("s29-02: CRUD 完整操作")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("INSERT/UPDATE/DELETE/SELECT = 增删改查")
    print_key_point("UPDATE/DELETE 必须带 WHERE!")
