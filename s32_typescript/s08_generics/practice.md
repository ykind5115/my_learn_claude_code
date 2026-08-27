# s32-08: 泛型 — 动手需求

[← 返回总索引](../PRACTICE.md) | [本章教程](./README.md)

> 一句话本章核心思想：**泛型 = 类型参数化：同一个函数适配多种类型，而且不丢失类型信息。**

学完本章，用下面这些需求把知识变成肌肉记忆。**只给需求和提示，不给完整代码**——卡住了回到主项目提问。

## 使用说明
- 前置技能：s01~s08（s06 的 http/fetch、s07 的 chalk 会用到；需求 3 用 s10 的 Result 模式作前瞻）
- 自测方式：`node s32_typescript/s08_generics/<文件名>.ts` 直跑；`cd s32_typescript && npm run typecheck` 零报错
- 解答文件建议放本章目录内，命名 `practice_<名字>.ts`
- 只用可擦除语法（避开 enum / namespace / 参数属性 / 装饰器——tsconfig 的 `erasableSyntaxOnly` 会替你把关）

## 需求 1：泛型工具集（⭐ 入门 | 核心技能：泛型参数、extends 约束、内置工具）
- [ ] 完成

### 背景
README 实验 2/3 的完整版：把最常用的泛型函数一次写齐。这些函数你会天天用（很多库源码里就是它们），写完你就知道"泛型 = 类型参数化"不是抽象概念，而是具体到每个尖括号的直觉。

### 要做什么（验收标准）
1. `practice_tools.ts` 里实现：
   - `pair<T, U>(a: T, b: U): [T, U]` —— 二元组
   - `findById<T extends { id: string }>(items: T[], id: string): T | undefined`
   - `groupBy<T, K extends string>(items: T[], keyFn: (item: T) => K): Record<K, T[]>`
   - `shuffle<T>(arr: T[]): T[]`（可选，返回新数组，别改原数组）
2. 每个函数配 **2~3 个不同类型**的调用，验证类型不丢：
   - 比如 `findById(users, "u-1")` 返回 `User | undefined`、`findById(products, "p-1")` 返回 `Product | undefined`
   - `groupBy` 按不同类型字段分组（按性别分人、按状态分任务）
3. 打印每个调用的结果
4. typecheck 零报错

### 技术要点
- **泛型推断**：`pair("a", 1)` 不用写 `<string, number>`，TS 自己猜——大多数调用都不需要显式类型参数（README 原理图）
- **extends 约束 = "至少长这样"**：`T extends { id: string }` 让函数体里能安全访问 `item.id`，同时返回值保持精确类型（传 `User[]` 返回 `User`，README 核心概念 1）
- **Record<K, V>**：内置泛型工具，键值字典——`groupBy` 的返回类型就是它（README 核心概念 3 的表）
- **返回值保持精确类型**：这是泛型 vs `any` 的分水岭——`any` 会让类型信息蒸发（README 开篇的例子）
- 泛型是零运行时开销的：编译期擦除后就是普通 JS（s00 心智模型）

### 超纲提示
🔧 `Partial<T>` / `Pick<T, K>` / `Omit<T, K>` 各找一个使用场景加进工具集（README 核心概念 3 的表格给了提示）：部分更新用 Partial、视图/摘要用 Pick、反 Pick 用 Omit——拿 `interface Todo` 之类验证。

### 自测方法
```bash
node s32_typescript/s08_generics/practice_tools.ts
cd s32_typescript && npm run typecheck
# 红线实验：故意给 findById 传一个没有 id 字段的类型数组（如 { name: string }[]）
#           → typecheck 应报"不满足约束"；跑 node 却照常执行 → 约束只在编译期存在
```

## 需求 2：泛型缓存 Cache&lt;T&gt;（⭐⭐ 组合 | 核心技能：泛型类 + Map + 容量管理）
- [ ] 完成

### 背景
缓存是服务里最常用的组件之一（配置、会话、API 结果都要缓存）。泛型让它能装任何类型，而"TTL 过期 + 容量淘汰"是缓存的两个真实约束。写完这个类，你就同时练了泛型类和工程里最常见的状态管理。

### 要做什么（验收标准）
1. `class Cache<T>`，公开方法：`set(key: string, value: T, ttlMs?: number)` / `get(key): T | undefined` / `has(key): boolean` / `delete(key): boolean` / `clear()` / `size`（只读属性）
2. **TTL 自动失效**：`set` 时记录过期时间，`get` / `has` 时检查是否过期，过期就删除并当作不存在
3. **容量上限**：构造时传入 `maxSize`（如 `new Cache<string>(3)`），超过上限淘汰**最旧的**（FIFO 即可，记住插入顺序）
4. 用 `Cache<string>` 和 `Cache<number[]>` 两个实例分别 set / get，证明类型隔离：往 `Cache<string>` 里塞 `number[]` 必须在编译期报错
5. 跑一个演示：set → get → 过期（短 ttl 如 50ms + 等待）→ 淘汰（塞满再塞）→ clear
6. typecheck 零报错

### 技术要点
- **泛型类**：`class Cache<T>` 让字段/方法的类型跟着 T 走（README 核心概念 2 的 Box 例子）
- **私有 Map**：用 `#items: Map<string, ...>` 存值，过期时间单独记（再存一个 Map，或把值和过期时间存成元组）——`#` 私有字段才是真封装（s09 展开）
- **TTL 检查（Date.now()）**：`get` 时先 `Date.now() >= expiredAt` 就 `delete` 并返回 undefined——惰性清理，最省事
- **淘汰策略**：FIFO = 记插入顺序，满员时删最先插入的；`Map` 的迭代顺序就是插入顺序（超纲点的 LRU 要用这个特性）
- 避开参数属性语法：字段用普通声明 + 构造函数里赋值（可擦除语法约定，tsconfig 会拦）

### 超纲提示
🔧 LRU（最近最少使用）：淘汰"最久没被访问"的条目——`get` 命中时把该键删掉再重新 `set`（移到迭代顺序末尾），`Map` 的迭代顺序特性正好支持。查 MDN 的 Map 文档确认迭代顺序。

### 自测方法
```bash
node s32_typescript/s08_generics/practice_cache.ts
# 应看到：正常命中 → TTL 过期后 miss → 塞满后最旧的被淘汰 → clear 后 size 为 0
cd s32_typescript && npm run typecheck
# 类型红线：cache.set("k", [1,2,3])（Cache<string> 实例）→ typecheck 必须报错
```

## 需求 3：类型安全 API 客户端（⭐⭐⭐ 挑战 | 核心技能：callApi&lt;T&gt; + Result 模式（s10 前瞻））
- [ ] 完成

### 背景
README 里 SDK 的 `callApi<T>` 就是这题：同一个函数服务十几种返回类型，调用方指定 T，编译器按 T 检查结果。配合 Result 模式（s10 的主角），成功和失败都变成类型可见的数据，而不是靠 try/catch 猜。这是你离"真实 SDK 源码"最近的一次。

### 要做什么（验收标准）
1. `practice_api_client.ts`：
   - `type Result<T, E> = { ok: true; value: T } | { ok: false; error: E }`（判别联合）
   - `class ApiError extends Error { statusCode: number; constructor(statusCode: number, message: string) }`（s10 详述，先用起来）
   - `async function callApi<T>(url: string, init?: RequestInit): Promise<Result<T, ApiError>>`：
     - `fetch` → 响应 `ok` / `status` 校验 → JSON 解析；任何一步失败都包成 `ApiError` 返回 `{ ok: false, error }`
     - 成功返回 `{ ok: true, value: <解析出的 T> }`
   - 解析出的数据要过一遍"unknown → 校验 → 精确类型"的链条（`resp.json()` 给的类型别直接当 T 用）
2. 定义 `interface User { id: number; login: string; ... }` 和 `interface Repo { id: number; name: string; ... }`，分别调用 `callApi<User>` / `callApi<Repo>`，验证调用方拿到的 `value` 类型分别是 User 和 Repo（**不是 any**）——写一行 `value.login.toUpperCase()` 之类的类型敏感操作，typecheck 通过即证明类型没丢
3. 自测数据来源：本地起一个 s06 的最小 HTTP 服务器返回假 JSON（`127.0.0.1` 随机端口），或直接打真实公开 API（超纲）
4. 跑通 + typecheck 零报错

### 技术要点
- **泛型 T 由调用方指定**：`callApi<User>(url)` 和 `callApi<Repo>(url)`——同一个函数，T 各填各的（README"跟 Agent 的关系"原例）
- **unknown → 校验 → 精确类型链条**：拿到的响应先当 unknown，做形状校验（比如确认有 `id` 和 `login` 字段）再收窄成 T——s01 提过的 unknown→narrowing 链在真实代码里的样子
- **判别联合表达成功/失败**：`{ ok: true; value } | { ok: false; error }`，用 `if (result.ok)` 收窄——s03 的 union/narrowing 直接落地（README Result 例子）
- **自定义错误类**：`ApiError extends Error` 携带 statusCode——s10 会系统讲错误家族，先照 README 的 Result 模式用起来
- 别忘了 `resp.json()` 也可能失败（非 JSON 响应）——那也是错误分支

### 超纲提示
🔧 对接真实公开 API：`https://api.github.com/users/octocat`（→ User）和 `https://api.github.com/repos/microsoft/typescript`（→ Repo）。注意 GitHub API 要求 `User-Agent` 请求头，`init` 里带上；没网 / 被限流就退回本地假服务器方案。

### 自测方法
```bash
node s32_typescript/s08_generics/practice_api_client.ts
# 应看到：User 调用的 value 是 User 形状、Repo 调用是 Repo 形状；失败分支（打一个 404 地址）返回 { ok: false, error: ApiError }
cd s32_typescript && npm run typecheck
# 类型红线：把 value 误用成别的形状（比如对 Repo 的 value 调 .login）→ typecheck 必须报错
# 实验：把地址改成 http://127.0.0.1:1/（必然连接失败）→ 观察错误怎么被包装成 ApiError
```

## 做完之后
- 自查：你用了本章哪些概念？——泛型参数与推断、extends 约束、泛型类、Record / Partial / Pick / Omit、内置泛型、类型不丢失 vs any、判别联合 + Result 前瞻
- 想继续深挖：回看本章 README 的"跟 Agent 的关系"，选一个点展开——比如把需求 2 的 Cache&lt;T&gt; 接到需求 3 的 callApi&lt;T&gt; 上（带 TTL 的 API 缓存客户端），或者研究一个真实 SDK 的 .d.ts 里 callApi&lt;T&gt; 是怎么写的（s15 会教你读库源码）
