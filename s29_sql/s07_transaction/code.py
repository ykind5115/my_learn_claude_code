#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s29-07: 事务 — ACID"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, get_db, run_sql, print_step, print_sql,
                   print_table, print_note, print_key_point, print_section)


def demo_all():
    db = get_db()
    db.execute("CREATE TABLE accounts (id INTEGER PRIMARY KEY, name TEXT, balance REAL)")
    db.executemany("INSERT INTO accounts VALUES (?,?,?)",
                   [(1, "Alice", 1000.0), (2, "Bob", 500.0)])
    print(f"  初始:")
    print_table(run_sql(db, "SELECT * FROM accounts"))

    print_step(1, "无事务 — 中途崩溃的后果")
    # 模拟崩溃: 扣 Alice 100, 但不给 Bob 加
    db.execute("UPDATE accounts SET balance = balance - 100 WHERE name = 'Alice'")
    print(f"  Alice -100 后 (假设崩溃):")
    print_table(run_sql(db, "SELECT * FROM accounts"))
    print(f"  Bob 的 100 没了! 钱凭空消失了!")
    # 手动回滚 (修复刚才的演示)
    db.execute("UPDATE accounts SET balance = 1000 WHERE name = 'Alice'")
    db.commit()  # 确保后续 BEGIN 不在隐式事务内

    print_step(2, "有事务 — COMMIT")
    db.execute("BEGIN")
    db.execute("UPDATE accounts SET balance = balance - 100 WHERE name = 'Alice'")
    db.execute("UPDATE accounts SET balance = balance + 100 WHERE name = 'Bob'")
    db.execute("COMMIT")
    print_table(run_sql(db, "SELECT * FROM accounts"))
    print_note("两件事一起完成")

    print_step(3, "有事务 — ROLLBACK")
    db.execute("BEGIN")
    db.execute("UPDATE accounts SET balance = balance - 999 WHERE name = 'Alice'")
    print(f"  Alice 扣了 999... 但发现问题!")
    db.execute("ROLLBACK")
    print_table(run_sql(db, "SELECT * FROM accounts"))
    print_note("回滚 → 回到 BEGIN 之前")

    print_step(4, "ACID")
    print(f"  Atomicity:   要么全做，要么全不做")
    print(f"  Consistency: 数据库始终合法 (Alice+Bob = 1500)")
    print(f"  Isolation:   并发事务互不干扰")
    print(f"  Durability:  提交了就持久化")

    db.close()


if __name__ == "__main__":
    print_section("s29-07: 事务")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("BEGIN → 操作 → COMMIT/ROLLBACK")
    print_key_point("事务 = 不可分割的操作包")
