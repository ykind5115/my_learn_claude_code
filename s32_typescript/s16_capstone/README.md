# s32-16: 综合实战 — 用 TypeScript + Node.js 独立写一个 HTTP API

[← 返回概览](../README.md) | [上一章：类型体操](../s15_type_gymnastics/)

> 一句话核心思想：**把前面 15 章组装成一个真实应用——类型设计、校验、持久化、错误分层、模块拆分，一个都不少。**

---

## 问题 — 学完了，能独立写应用吗？

这是检验章节。目标是回答一个问题：**给你一个需求（"做一个 todo 的 REST API"），你能从零搭起来吗？**

本章的每个文件都标注了它对应前面哪一章的知识点——顺着标注往回看，你会发现自己已经掌握了一切所需的零件。

---

## 架构 — 5 个文件的职责

```
s16_capstone/
├── code.ts        入口：演示模式（自动跑全部端点）/ --serve 模式（真实服务器）
├── server.ts      HTTP 服务器 + 手写路由 + 请求体解析 + 错误映射
├── todo-model.ts  Todo 类型 + 请求体校验（unknown → 精确类型）
├── todo-store.ts  JSON 文件持久化（data/todos.json）
└── errors.ts      HttpError + 400/404 快捷构造
```

```
请求进来
  │
  ▼
server.ts 路由分发（GET /todos、POST /todos、PATCH /todos/:id ...）
  │
  ├─→ todo-model.ts 校验请求体（s03 的 unknown → 类型守卫）
  ├─→ todo-store.ts 读写 JSON（s11 的 fs/promises）
  └─→ errors.ts     业务错误 → 4xx，未知错误 → 500（s10 的分层）
```

---

## API 一览

| 方法 | 路径 | 干什么 | 成功码 |
|---|---|---|---|
| GET | /health | 健康检查 | 200 |
| GET | /todos | 列出全部 | 200 |
| POST | /todos | 创建（`{"title":"..."}`） | 201 |
| GET | /todos/:id | 查看单条 | 200 |
| PATCH | /todos/:id | 修改（`{"done":true}` / `{"title":"..."}`） | 200 |
| DELETE | /todos/:id | 删除 | 200 |

错误路径全兜住：title 为空 → 400，body 不是对象 → 400，非法 JSON → 400，id 不存在 → 404，未知路径 → 404，方法不支持 → 405，数据文件损坏 → 500。

---

## 核心概念 — 每个文件的知识点对照

| 文件 | 用到的章节知识 |
|---|---|
| errors.ts | s10：自定义错误类（name 修正 + statusCode 上下文） |
| todo-model.ts | s02（interface）+ s03（unknown 校验收窄）+ s10（业务失败抛 HttpError） |
| todo-store.ts | s11（fs/promises + import.meta.dirname）+ s10（ENOENT 友好处理） |
| server.ts | s06（createServer 内核）+ s04（for await 读流式 body）+ s10（错误分层） |
| code.ts | s04（顶层 await、fetch）+ s06（端口 0）+ s02/s03（as unknown 标注） |

找一遍这些标注，你会发现：**15 章没有一章是白学的。**

---

## 跟 Agent 的关系 — 亲手做一个 mini Agent 工具

这个服务器就是一个「工具」的雏形：

- Agent 的工具 = HTTP 接口 + 文件系统 + 校验 + 错误映射（和你的代码一模一样）
- 真实系统里它可能接到 MCP server（s19）上，被 Claude Code 调用
- 你已经会写「Agent 能用的工具」了——剩下的只是协议封装

---

## 试一下

```bash
# 演示模式：自动跑一遍全部端点 + 错误路径 + 重启持久化验证
node s32_typescript/s16_capstone/code.ts

# 真实服务器模式
node s32_typescript/s16_capstone/code.ts --serve 3000
# 另开终端：
curl http://localhost:3000/todos
curl -X POST http://localhost:3000/todos -H "Content-Type: application/json" -d '{"title":"手动创建"}'
curl -X PATCH http://localhost:3000/todos/1 -H "Content-Type: application/json" -d '{"done":true}'
```

## 拓展练习（检验「独立写应用」）

1. **加字段**：给 Todo 加 `priority: "low" | "mid" | "high"`，支持创建/修改/按优先级筛选
2. **加路由**：GET /todos?done=true 过滤已完成的
3. **加并发安全**：两个请求同时 POST，会不会丢数据？（提示：load → 改 → save 之间有窗口）
4. **改成 sqlite**：把 todo-store.ts 换成 sqlite 存储，其余文件不动——体会分层的好处

---

## 小结 — 记住这个就够了

1. **文件分工 = 模块边界**：入口/路由/模型/存储/错误各管各的（s05）
2. **外部数据永远先校验**：unknown → 类型守卫 → 精确类型（s03）
3. **错误分层**：业务错误 → 4xx，未知错误 → 500（s10）
4. **能跑起来、能自测、能持久化、能报友好错误**——这就是「独立用 TS + Node 写应用」的全部标准
