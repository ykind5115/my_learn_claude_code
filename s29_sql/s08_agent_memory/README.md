# s29-08: Agent Memory 实战

[← 返回概览](../README.md) | [上一章：事务](../s07_transaction/)

> *"把 s01-s07 学的全串起来——设计一个 Agent Memory 系统。用 SQLite 存对话记忆，支持 CRUD。"*

---

## 问题 — Agent 怎么记住之前对话的内容？

纯文件读写（JSON/txt）适合少量数据。但当你需要：
- 按时间查历史对话
- 搜索含特定关键词的记忆
- 关联记忆和对话会话

数据库比文件强 100 倍。

---

## 设计方案

### 表结构

```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,          -- 会话 ID (UUID)
    title TEXT,                   -- 会话标题
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,  -- 属于哪个会话
    role TEXT NOT NULL,             -- user / assistant
    content TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

CREATE INDEX idx_messages_conv ON messages(conversation_id);
```

---

## 试一下

```bash
python s29_sql/s08_agent_memory/code.py
```

---

## 小结

```
Agent Memory = SQLite + CRUD + 索引 + 事务
conversations 表: 会话元信息
messages 表: 每条消息
索引: 加速按会话查消息
这就是 s09 Memory 系统的原型
```
