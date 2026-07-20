#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s29-08: Agent Memory 实战"""

import os, sys, uuid
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, get_db, run_sql, print_step, print_sql,
                   print_table, print_note, print_key_point, print_section)


def demo_all():
    db = get_db()

    # 建表
    db.execute("""CREATE TABLE conversations (
        id TEXT PRIMARY KEY, title TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    )""")
    db.execute("""CREATE TABLE messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT NOT NULL, role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (conversation_id) REFERENCES conversations(id)
    )""")
    db.execute("CREATE INDEX idx_msg_conv ON messages(conversation_id)")

    print_step(1, "表结构")
    print(f"  conversations: id, title, created_at, updated_at")
    print(f"  messages: id, conv_id(FK), role, content, created_at")
    print_key_point("conversation 和 messages 是一对多关系")

    # 创建会话
    conv_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    db.execute("INSERT INTO conversations (id, title, created_at) VALUES (?,?,?)",
               (conv_id, "Learn Claude Code", now))
    print_step(2, f"新会话: {conv_id}")

    # 插入消息
    msgs = [
        (conv_id, "user", "什么是 Agent Loop?"),
        (conv_id, "assistant", "Agent Loop 是一个 while True 循环..."),
        (conv_id, "user", "怎么实现工具调用?"),
        (conv_id, "assistant", "工具调用的核心是 tool_use 块..."),
    ]
    db.executemany("INSERT INTO messages (conversation_id, role, content) VALUES (?,?,?)", msgs)

    print_step(3, "查询会话历史")
    sql = """SELECT role, substr(content, 1, 40) AS preview, created_at
FROM messages WHERE conversation_id = ?
ORDER BY created_at"""
    print_sql(sql)
    rows = run_sql(db, sql, (conv_id,))
    print_table(rows)

    print_step(4, "搜索含关键词的记忆")
    sql = "SELECT role, content FROM messages WHERE content LIKE '%工具%'"
    print_sql(sql)
    rows = run_sql(db, sql)
    for r in rows:
        print(f"  [{r['role']}] {r['content'][:60]}...")

    print_step(5, "统计")
    sql = """SELECT role, COUNT(*) AS count
FROM messages WHERE conversation_id = ?
GROUP BY role"""
    rows = run_sql(db, sql, (conv_id,))
    print_table(rows)

    db.close()

    print_key_point("这就是 s09 Memory 系统的原型!")
    print_key_point("SQLite = 零配置 + 文件数据库 + 完整 SQL 支持")


if __name__ == "__main__":
    print_section("s29-08: Agent Memory 实战")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("Agent Memory = SQLite + CRUD + Index + Transaction")
