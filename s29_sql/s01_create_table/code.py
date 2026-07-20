#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s29-01: 建表与插入"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, get_db, run_sql, print_step, print_sql,
                   print_table, print_note, print_key_point, print_section)


def demo_all():
    db = get_db()

    print_step(1, "CREATE TABLE — 建货架")
    sql = """CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL
)"""
    print_sql(sql)
    db.execute(sql)
    print_note("id=主键(唯一编号), name=文本(必填), price=浮点数")

    print_step(2, "INSERT — 放货")
    items = [(1, "apple", 3.5), (2, "banana", 2.0), (3, "orange", 4.0)]
    for item in items:
        sql = f"INSERT INTO products VALUES {item}"
        print_sql(sql)
        db.execute(f"INSERT INTO products VALUES (?,?,?)", item)

    print_step(3, "SELECT — 看货")
    sql = "SELECT * FROM products"
    print_sql(sql)
    rows = run_sql(db, sql)
    print_table(rows)

    print_step(4, "SELECT 指定列")
    sql = "SELECT name, price FROM products"
    print_sql(sql)
    print_table(run_sql(db, sql))

    print_step(5, "数据类型")
    print(f"  INTEGER  -> 整数")
    print(f"  REAL     -> 浮点数")
    print(f"  TEXT     -> 文本")
    print(f"  BLOB     -> 二进制数据")
    print(f"  NULL     -> 空值")

    db.close()


if __name__ == "__main__":
    print_section("s29-01: 建表与插入")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("CREATE TABLE = 建货架")
    print_key_point("INSERT INTO = 放货")
    print_key_point("SELECT = 看货")
