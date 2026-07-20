#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s29-06: 索引"""

import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, get_db, run_sql, print_step, print_sql,
                   print_table, print_note, print_key_point, print_section)


def demo_all():
    db = get_db()
    db.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)")

    # 插入 50000 行
    N = 50000
    print(f"  插入 {N} 行测试数据...")
    db.execute("BEGIN")
    for i in range(N):
        db.execute("INSERT INTO products VALUES (?, ?, ?)",
                   (i, f"product_{i}", round(i * 1.5, 2)))
    db.execute("COMMIT")
    print_note("完成")

    print_step(1, "无索引 — 全表扫描")
    sql = "SELECT * FROM products WHERE name = 'product_49999'"
    start = time.time()
    run_sql(db, sql)
    no_index_time = (time.time() - start) * 1000
    print_sql(sql)
    print(f"  耗时: {Color.WARNING}{no_index_time:.1f}ms{Color.RESET}")

    plan = run_sql(db, "EXPLAIN QUERY PLAN " + sql)
    for row in plan:
        print(f"  {Color.DIM}计划: {row[3]}{Color.RESET}")

    print_step(2, "创建索引")
    sql_idx = "CREATE INDEX idx_name ON products(name)"
    print_sql(sql_idx)
    db.execute(sql_idx)

    print_step(3, "有索引 — 直接定位")
    start = time.time()
    run_sql(db, sql)
    index_time = (time.time() - start) * 1000
    print(f"  耗时: {Color.SUCCESS}{index_time:.1f}ms{Color.RESET}")

    plan = run_sql(db, "EXPLAIN QUERY PLAN " + sql)
    for row in plan:
        print(f"  {Color.DIM}计划: {row[3]}{Color.RESET}")

    if no_index_time > index_time:
        print_key_point(f"索引加速: {no_index_time / max(index_time, 0.01):.0f}x")
    else:
        print_note("数据量不够大, 差异不明显 (用 50 万行试试)")

    print_step(4, "索引的代价")
    print(f"  优点: SELECT 飞快")
    print(f"  缺点: INSERT/UPDATE/DELETE 变慢 (要同时更新索引)")
    print(f"  规则: 只为 WHERE/JOIN/ORDER BY 的列建索引")

    db.close()


if __name__ == "__main__":
    print_section("s29-06: 索引")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("索引 = 空间换时间")
    print_key_point("EXPLAIN 查看是否用到索引")
