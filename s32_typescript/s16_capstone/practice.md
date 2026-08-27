# s32-16: 综合实战 — 动手需求

[← 返回总索引](../PRACTICE.md) | [本章教程](./README.md)

> 一句话本章核心思想：**把前面 15 章组装成一个真实应用——类型设计、校验、持久化、错误分层、模块拆分，一个都不少。**

学完本章，用下面这些需求把知识变成肌肉记忆。**只给需求和提示，不给完整代码**——卡住了回到主项目提问。

## 使用说明
- 前置技能：s01~s16（检验章——全部 15 章的知识都在下面的需求里）
- 自测方式：`node s32_typescript/s16_capstone/code.ts`（演示模式，自动跑全部端点）/ `node s32_typescript/s16_capstone/code.ts --serve 3000` + curl（真实服务器）；改完记得 `cd s32_typescript && npm run typecheck` 保持零报错
- 解答文件建议放本章目录内，命名 `practice_<名字>.ts`（如 `practice_stress.ts`）
- 约定：相对导入带 `.ts` 扩展名；文件路径用 `import.meta.dirname` 拼；类型导入用 `import type`（tsconfig 开了 `verbatimModuleSyntax`）

### 动手前必读
本模块的 5 个文件就是你的"他人代码"：`code.ts`（入口：演示/--serve 两模式）、`server.ts`（HTTP + 手写路由 + body 解析 + 错误映射）、`todo-model.ts`（Todo 类型 + unknown 校验）、`todo-store.ts`（JSON 文件持久化）、`errors.ts`（HttpError + 400/404 快捷构造）。**需求 1、2 要在它们上面加功能，动手前先通读这 5 个文件**——README 的"文件知识点对照表"就是阅读地图。

⚠️ 需求 1、2 会改动 `todo-model.ts` / `server.ts` / `todo-store.ts`。动手前先 `git commit` 或复制一份原文件，改坏了能还原。演示模式会自动清空 `s16_capstone/data/`，--serve 模式的数据会保留。

## 需求 1：扩展 todo——priority 与筛选排序（⭐ 入门 | 核心技能：全章串联——加字段 + 筛选 + 排序）
- [ ] 完成

### 背景
README 拓展练习 1+2 的完整版。给现成系统加功能，是读懂他人架构最好的练习——你要先看懂 5 个文件的分层，再决定每一处改动落在哪个文件。

### 要做什么（验收标准）
1. `Todo` 加 `priority: "low" | "mid" | "high"`（`todo-model.ts` 的 interface + 校验同步升级）；创建时缺省 `mid`
2. 创建支持 priority：`POST /todos` body 可带 `{"title":"...", "priority":"high"}`
3. 修改支持 priority：`PATCH /todos/:id` 可改 `{"priority":"low"}`
4. 筛选：`GET /todos?done=true&priority=high`（两个参数可叠加、可单独用；`done=true` 只返回已完成的）
5. 排序：`GET /todos?sort=priority|createdAt&order=asc|desc`（`sort` 二选一，`order` 缺省 `asc`）
6. 非法 priority 值 → 400（复用 `errors.ts` 的 `badRequest`；`sort`/`order` 的非法值建议同样 400）

### 技术要点
- 先读全部 5 个文件，弄清分层：入口（code.ts）/ 路由（server.ts）/ 模型+校验（todo-model.ts）/ 存储（todo-store.ts）/ 错误（errors.ts）——改哪一处、不动哪一处，本身就是设计题
- `unknown → 精确类型`校验升级：`parseCreateBody` / `parsePatchBody` 里给 priority 加一道类型守卫（s03 的判别联合思路，`"low"|"mid"|"high"` 是字符串字面量联合）
- 缺省值放哪：`parseCreateBody` 返回时补 `mid`，还是 server 创建时补？想清楚哪一层该负责
- query 解析：`new URL(req.url ?? "/", "http://localhost").searchParams`——`url.searchParams.get("done")` 拿到的是字符串，`"true"` → boolean 要自己转
- 筛选 = `todos.filter(...)`，排序 = `todos.toSorted(...)`（不改变原数组，避免污染后续 save）——排序的字段名到属性值的映射自己写
- 校验失败抛 `badRequest(...)`（errors.ts），server.ts 的 catch 会自动映射成 400（s10 错误分层）

### 超纲提示
🔧 加 `GET /stats`：返回总数 / 已完成数 / 未完成数 / 按 priority 分组统计——一个小而完整的"聚合查询"练习。

### 自测方法
```bash
cd s32_typescript && npm run typecheck        # 零报错
node s32_typescript/s16_capstone/code.ts      # 演示模式全跑一遍（原有端点必须都还活着）
node s32_typescript/s16_capstone/code.ts --serve 3000
# 另开终端：
curl -X POST http://localhost:3000/todos -H "Content-Type: application/json" -d '{"title":"高优先级","priority":"high"}'
curl -X POST http://localhost:3000/todos -H "Content-Type: application/json" -d '{"title":"默认优先级"}'
curl "http://localhost:3000/todos?priority=high"
curl "http://localhost:3000/todos?done=false&sort=priority&order=desc"
curl -X POST http://localhost:3000/todos -H "Content-Type: application/json" -d '{"title":"x","priority":"urgent"}'   # 应 400
```

## 需求 2：并发安全与压测（⭐⭐ 组合 | 核心技能：并发窗口 + 压测）
- [ ] 完成

### 背景
README 拓展练习 3：两个请求同时 POST，会不会丢数据？答案藏在 `loadTodos → 改 → saveTodos` 的窗口里。先复现、再分析、再修复、最后对比数据——这是生产环境并发 bug 的标准处置流程。

### 要做什么（验收标准）
1. 写压测脚本 `practice_stress.ts`：用 `Promise.all` 同时发 20 个 `POST /todos`（title 各不相同），**先跑 3 轮**，统计服务器最终条数 vs 预期条数——观察丢不丢、丢多少
2. 分析竞态窗口：为什么并发 POST 会互相覆盖？在 `server.ts` 的 POST 处理里找到 `loadTodos → push → saveTodos` 三步，画出两个请求交错的时间线
3. 修复：在 `todo-store.ts` 加一个**读-改-写串行化执行器**——所有"load → 改 → save"操作排队执行（一个简单 promise 链队列即可），让 server.ts 的读写都走这个执行器
4. 修完再压测 3 轮，对比修复前后的最终条数

### 技术要点
- 竞态窗口：两个请求几乎同时 `loadTodos()` 拿到同一个数组 → 各自 push → 各自 save——**后写的覆盖先写的**（s04 异步交错的心智模型）
- 串行队列：一个模块级的 `let chain: Promise<unknown> = Promise.resolve()`，新操作 = `chain = chain.then(执行操作)`——上一个完成才跑下一个（不需要锁，JS 单线程 + promise 链就是队列）
- 执行器签名自己定：`withLock(fn: () => Promise<T>): Promise<T>` 起步——注意队列要在**进程内共享**（模块级变量），每个请求进来都入同一个队
- 压测脚本：`fetch` + `Promise.all`（s04 的并发 API），20 个请求用一个数组生成
- 压测后数条数：`GET /todos` 返回数组长度 vs 期望 20×轮数；数据要隔离就换端口 + 删 `s16_capstone/data/`
- 修复后 server.ts 的 POST / PATCH / DELETE 都要走串行执行器，别只修 POST——想想为什么

### 超纲提示
🔧 原子写：`saveTodos` 先写临时文件再 `rename`（`writeFile(dataFile + ".tmp")` → `rename`），防止写一半进程崩溃留下半截 JSON——s11 文件系统知识的实战用法。

### 自测方法
```bash
# 终端 1：起服务器
node s32_typescript/s16_capstone/code.ts --serve 3100
# 终端 2：修复前压测 3 轮（观察丢数据）
node s32_typescript/s16_capstone/practice_stress.ts --port 3100 --rounds 3
# 修复 todo-store.ts 后，删数据再压测 3 轮（对比条数）
# 验收点：修复前 3 轮条数 < 预期；修复后 3 轮全部 = 预期（60 条）
```

## 需求 3：第二个完整 API（⭐⭐⭐ 挑战 | 核心技能：独立完成，全程无提示）
- [ ] 完成

### 背景
s16 的使命是回答一个问题：**给你一个需求，你能从零搭起来吗？** 现在换一个需求检验你——不许看参考答案，不许问提示，卡住了回对应章节复习。README 的"文件知识点对照表"就是你的地图。

### 要做什么（验收标准）
**三选一**（自选其一）：

- **A. 书签管理 API**：书签的增删改查 + 标签（一个书签多个标签）+ 按标签搜索 + 按创建时间/标题排序
- **B. todo 存储换成 sqlite**：`better-sqlite3`（新库，查文档装依赖），把 `todo-store.ts` 的 JSON 换成 sqlite，**其余文件不动**——体会分层的好处（README 拓展练习 4）
- **C. 团队看板**：`board / column / card` 三层结构，看板的增删、列内卡片排序

**统一标准**（A/B/C 都要满足）：
- RESTful 路由齐全（集合 + 单条 + 创建 + 修改 + 删除 + 必要的查询参数）
- 外部数据全部校验（unknown → 精确类型，非法值 400）
- 错误分层：业务错误 4xx、未知错误 500（复用 `HttpError` 模式）
- JSON 文件持久化（B 用 sqlite 除外）；路径用 `import.meta.dirname`
- 演示模式自动跑全部端点 + 错误路径（参照 `code.ts` 的演示写法）
- `npm run typecheck` 零报错

### 技术要点
不提示——这是检验。卡住了，回到对应章节复习：类型设计看 s02/s03、异步看 s04、http 看 s06、错误分层看 s10、文件看 s11、模块拆分看 s05。README 的"文件知识点对照表"就是索引。

### 超纲提示
🔧 加单元测试（Node 内置 `node:test`，无需引库）或 Swagger 文档（`/docs` 返回 JSON 描述你的 API）——做完这些，你就真的是"能独立交付应用"的人了。

### 自测方法
```bash
cd s32_typescript && npm run typecheck              # 零报错
node s32_typescript/s16_capstone/practice_api.ts     # 你的演示模式：自动跑全部端点 + 错误路径
node s32_typescript/s16_capstone/practice_api.ts --serve 3200
# 另开终端用 curl 把每个端点手动过一遍，包括错误路径
```

## 做完之后
- 自查：你用了本章哪些概念？——文件分工与模块边界（s05）/ 外部数据校验 unknown → 精确类型（s03）/ 错误分层 4xx vs 500（s10）/ JSON 持久化与 import.meta.dirname（s11）/ createServer 与 body 流读取（s06+s04）/ 并发窗口与串行化（s04）——15 章没有一章是白学的
- 想继续深挖：回看本章 README 的「跟 Agent 的关系」，选一个点展开——这个服务器就是一个 mini Agent 工具的雏形，想想怎么把它接到 MCP server 上被 Claude Code 调用
