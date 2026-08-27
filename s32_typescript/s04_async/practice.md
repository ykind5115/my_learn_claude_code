# s32-04: async / await / Promise — 动手需求

[← 返回总索引](../PRACTICE.md) | [本章教程](./README.md)

> 一句话本章核心思想：**Promise 是「未来的结果」的占位盒，async/await 让等待未来的代码读起来像现在。**

学完本章，用下面这些需求把知识变成肌肉记忆。**只给需求和提示，不给完整代码**——卡住了回到主项目提问。

## 使用说明
- 前置技能：s01~s04（基础语法 + interface + narrowing + async/Promise）
- 自测方式：`node s32_typescript/s04_async/practice_xxx.ts` 从仓库根直跑看输出（ESM 模块，顶层可以直接 `await`）；`cd s32_typescript && npm run typecheck` 零报错
- 解答文件建议放本章目录内，命名 `practice_<名字>.ts`

## 需求 1：模拟下载器（串行 vs 并行）（⭐ 入门 | 核心技能：async/await、Promise.all、计时）
- [ ] 完成

### 背景
用计时数据让「独立请求用 Promise.all」变成身体记忆——看完串行约 3.5 秒 vs 并行约 1.1 秒，你永远不会再写串行循环。

### 要做什么（验收标准）
1. `fakeFetch(name: string, ms: number): Promise<string>`——用 `setTimeout` 模拟网络延迟。
2. 5 个任务延迟错开：300 / 500 / 700 / 900 / 1100ms。
3. **串行版**：`for` 循环里逐个 `await`，打印总耗时和结果顺序。
4. **并行版**：`Promise.all(任务数组.map(...))`，打印总耗时和结果顺序。
5. 输出结论：并行总耗时 ≈ 最慢的那个（约 1100ms），串行总耗时 ≈ 各耗时之和（约 3500ms）。

### 技术要点
- `async` 函数永远返回 `Promise<T>`；`await` 暂停函数执行，等落定后带着结果继续——await 之后 = `.then` 回调（微任务）
- `Promise.all` 同时发起所有请求，总耗时 = 最慢的那个
- 计时用 `performance.now()`（或 `Date.now()`），`Math.round` 成整数 ms
- 顶层 `await`：ESM 模块顶层可以直接 await（本章 code.ts 就是这么结尾的）
- 项目约定三件套：相对导入带 `.ts` 扩展名（把 `fakeFetch` 拆到 `fake.ts` 再 import，就是 s05 的预习）；文件路径一律 `import.meta.dirname`；只用可擦除语法

### 超纲提示
🔧 真实 `fetch` 用法在 s16；并发上限（不一次性打爆 API）见本章需求 3。

### 自测方法
```bash
node s32_typescript/s04_async/practice_downloader.ts   # 跑两遍，确认两种耗时稳定
# 实验：把某个延迟改成 3000ms，观察并行总耗时跟随最慢任务、串行总耗时仍≈总和
cd s32_typescript && npm run typecheck
```

## 需求 2：请求超时器与批量结果（⭐⭐ 组合 | 核心技能：Promise.race、allSettled、错误三件套）
- [ ] 完成

### 背景
网络超时是 Agent 系统日常：请求可能永远不回来，必须自己掐表。`race + allSettled` 是标准答案。

### 要做什么（验收标准）
1. `withTimeout<T>(p: Promise<T>, ms: number): Promise<T>`——超时则 reject 一个错误（message 含 "timeout"，可自定义 `TimeoutError` 类名）；未超时则正常返回。
2. 演示三组：正常完成 / 超时被掐 / 恰好临界——每组都能看出谁赢。
3. 用 `Promise.allSettled` 跑 5 个任务（故意混入失败），逐个打印 `status / value / reason`——证明 `allSettled` 永不 reject（整批不需要 try/catch）。
4. typecheck 零报错。

### 技术要点
- `Promise.race`：先落定者胜——`withTimeout` 就是「原 Promise vs 定时炸弹」赛跑
- `allSettled` 返回 `PromiseSettledResult<T>[]`：`{ status: "fulfilled"; value } | { status: "rejected"; reason }` 判别联合——永不 reject，逐个看结果（回想 s03 的判别联合收窄）
- 「一个都不能少」用 allSettled；「遇错即停」用 Promise.all
- 自定义错误：s10 正式学（`class` 继承 `Error`），这里先 `throw new Error("...")` 即可
- `withTimeout<T>` 的 T 从传入的 Promise 推断——泛型先用起来（s08 讲原理）

### 超纲提示
🔧 `AbortController` 是 fetch 官方超时方案——查它和 `Promise.race` 的差别：race 只是"假装"超时（底层请求还在跑），AbortController 能真正取消请求。

### 自测方法
```bash
node s32_typescript/s04_async/practice_timeout.ts
# 正常组 → 拿到值；超时组 → 捕获 timeout 错误；混合组 → allSettled 逐条打印 status/value/reason
cd s32_typescript && npm run typecheck
```

## 需求 3：并发任务调度器（⭐⭐⭐ 挑战 | 核心技能：并发控制/工作池）
- [ ] 完成

### 背景
`Promise.all` 全开可能打爆 API 限流——真实工程都要并发上限，面试常考。这道题就是手写一个 mini 工作池。

### 要做什么（验收标准）
1. `mapWithConcurrency<T, R>(items: T[], limit: number, fn: (item: T) => Promise<R>): Promise<R[]>`——最多同时跑 `limit` 个，结果**按输入顺序**返回。
2. 8 个任务、`limit = 3`：打印时间线（任意时刻进行中的任务 ≤ 3 个，每个任务完成时打印「第 i 个完成，进行中: [...]」）。
3. 对比 `Promise.all` 版本（8 个同时开跑），打印两版总耗时。
4. `limit = 1` 时退化成串行、`limit = 8` 时退化成 Promise.all——验证边界。
5. typecheck 零报错。

### 技术要点
- **任务队列 + 空闲信号量**：`limit` 个"工位"，一个任务完成就补下一个
- **结果按序写入**：预分配数组槽位（`results[i] = ...` 按 index 落位），不要 `push`——push 会把乱序完成的结果排错
- 微任务 vs 宏任务对调度的影响：想清楚「`for` 循环里同步发起」和「await 之后发起」的区别——同步发起的 Promise 会立刻开始执行，工作池要保证同时进行的不超过 limit
- `Promise.all` 全开的代价：全部任务同时发起，超过 limit 的部分会排队等工位
- 只用可擦除语法

### 超纲提示
🔧 参考 `p-limit` 库的实现思路（npm 上搜，s07 后可装）——对比它的 API 设计和你的 `mapWithConcurrency` 差在哪。

### 自测方法
```bash
node s32_typescript/s04_async/practice_scheduler.ts
# limit=3：时间线显示任意时刻进行中 ≤ 3；limit=1：变串行；limit=8：≈ Promise.all
# 再跑一次确认结果顺序与输入顺序一致（乱序完成也要按序返回）
cd s32_typescript && npm run typecheck
```

## 做完之后
- 自查：你用了本章哪些概念？（Promise 三态 / async-await 语法糖 / 微任务先于宏任务 / 串行 vs 并行 / Promise.all / Promise.race / allSettled / 顶层 await）
- 想继续深挖：回看本章 README 的「跟 Agent 的关系」——`Promise.all(tools.map(t => t.execute(args)))` 是 Agent 并行调工具的形态，用你的 `mapWithConcurrency` 给同一场景加上并发上限
