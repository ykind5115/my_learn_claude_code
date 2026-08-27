# s32-10: Error / 异常处理 — 动手需求

[← 返回总索引](../PRACTICE.md) | [本章教程](./README.md)

> 一句话核心思想：**错误处理 = 决定「谁能接住、怎么接住、接住后干什么」——同步靠 try/catch，异步靠 await+catch 或 .catch，业务错误还可以根本不抛。**

学完本章，用下面这些需求把知识变成肌肉记忆。**只给需求和提示，不给完整代码**——卡住了回到主项目提问。

## 使用说明
- 前置技能：s01~s10（union/收窄、泛型、async/Promise 都要能随手用）
- 自测方式：node 直跑（`node s32_typescript/s10_error_handling/practice_*.ts`）+ `cd s32_typescript && npm run typecheck`
- 解答文件建议放本章目录内，命名 `practice_<名字>.ts`
- 项目约定：相对导入必须带 `.ts` 扩展名（如 `import { Color } from "../utils.ts"`）；只用可擦除语法（避开 enum/namespace/参数属性）；涉及文件路径一律 `import.meta.dirname`

## 需求 1：错误家族（⭐ 入门 | 核心技能：自定义错误类 + instanceof 分层）
- [ ] 完成

### 背景
README 实验 2 的完整版——把「自定义错误 + 上下文 + 分层处理」做成体系。真实项目里错误是分层的：业务校验、资源不存在、网络问题，处理方式完全不同，靠一个 Error 字符串走天下是新手病。

### 要做什么（验收标准）
- `class AppError extends Error`——基类：`super(message)` 后把 `this.name = "AppError"` 修正
- `class ValidationError extends AppError`——带 `field: string`、`value: unknown` 上下文（如 `new ValidationError("age", -1, "年龄不能为负")`）
- `class NotFoundError extends AppError`
- `class NetworkError extends AppError`——带 `retryable: boolean`（如 429/超时 → true，500 → false）
- `handleError(e: unknown): string`——用 `instanceof` 依次判断，分别返回：
  - `ValidationError` → `"校验失败: <field> 收到非法值 <value>"`
  - `NotFoundError` → `"没找到"`
  - `NetworkError` → `"网络问题(可重试/不可重试)"`
  - 其他 → `"未知错误: <message>"`
- 演示：分别 throw 四类错误，都放进 `try/catch`；catch 里 `e` 是 `unknown`，先收窄才能访问 `.message`

### 技术要点
- 自定义错误三件套：`extends Error` + `super(message)` + 修正 `this.name`（README 核心概念 2：不修正的话 name 显示还是 "Error"）
- `instanceof` 链：子类错误也 instanceof 父类，所以判断顺序从最具体到最笼统（先 ValidationError，最后 AppError）
- `e: unknown` 收窄：catch 的 e 是 unknown，不做 `instanceof` 就不能安全访问 `.message`（s03 收窄复习）
- 可擦除语法：字段显式声明，禁用参数属性（构造参数赋值用普通写法）

### 超纲提示
- 🔧 `Error.cause`（ES2022）：底层错误用 `new AppError(msg, { cause: rawError })` 链式包装，排查时能一路追到根因——`cause` 字段的类型要自己定义一下

### 自测方法
- 建议解答文件：`s32_typescript/s10_error_handling/practice_error_family.ts`
- `node s32_typescript/s10_error_handling/practice_error_family.ts`：四类错误分别输出对应文案
- `cd s32_typescript && npm run typecheck`：0 错误

## 需求 2：Result 化改造（⭐⭐ 组合 | 核心技能：Result 模式 vs throw 对比）
- [ ] 完成

### 背景
README 说「可预期的业务失败用 Result」——拿已写过的东西改造，对比两种风格，体会「编译期强制处理失败」到底是什么意思。这是 s08 泛型接口 Result 落地的一章。

### 要做什么（验收标准）
- 选 s02 需求 2 的配置加载器（或 s03 需求 2 的校验器）改造：
  - `type Result<T, E> = { ok: true; value: T } | { ok: false; error: E }`（README 核心概念 4 的判别联合）
  - `loadConfig(partial: Partial<AppConfig>): Result<AppConfig, ConfigError>`——`ConfigError` 是判别联合：`{ kind: "missing"; field: string } | { kind: "invalid"; field: string; value: unknown }`
- 写两个调用方对比：
  - throw 版：`try/catch` 接
  - Result 版：`if (!r.ok)` 显式处理失败分支
- 文件顶部注释里总结：什么场景 throw 更合适、什么场景 Result 更合适（至少各写 2 条理由）

### 技术要点
- `Result<T, E>` 判别联合：成功/失败两个成员共享 `ok` 判别子（s03 判别联合 + s08 泛型）
- 编译期强制处理：`if (!r.ok)` 分支里 `r.error` 有类型、`r.value` 被排除——漏处理失败分支编译器直接报错
- 业务失败不抛异常：校验不过/字段缺失是「可预期」的失败，走 Result；预期外的编程错误（逻辑 bug）才 throw 保留现场（README 核心概念 4 的选择标准）
- 进阶：`ConfigError` 是判别联合时，配合 `never` 穷尽检查（s03），漏处理新的错误种类也编译报错

### 超纲提示
- 🔧 参考 Rust 的 `Result` / 开源 `ts-result` 库的 API 设计：`map`、`mapErr`、`unwrap` 等组合子——想想它们怎么用泛型和收窄实现

### 自测方法
- 建议解答文件：`s32_typescript/s10_error_handling/practice_result_config.ts`
- `node s32_typescript/s10_error_handling/practice_result_config.ts`：成功配置 + 缺失字段 + 非法值三种输入，两种风格输出一致
- `cd s32_typescript && npm run typecheck`：0 错误；故意删掉 `if (!r.ok)` 分支，看编译器怎么报「未处理失败分支」的错，再恢复

## 需求 3：重试器（⭐⭐⭐ 挑战 | 核心技能：重试 + 退避 + 全局兜底）
- [ ] 完成

### 背景
README 说的「接住能恢复的，抛出让上层处理的，兜底剩下的」——重试器是恢复层的核心。网络抖动、临时 429，重试一次就活了；这是 Agent 调 API 的日常。

### 要做什么（验收标准）
- `retry<T>(fn: () => Promise<T>, opts: { retries: number; backoffMs: number; retryable?: (e: unknown) => boolean }): Promise<T>`：
  - fn 抛错且 `retryable(e)` 为 true → 等 `backoffMs * attempt`（第 1 次重试等 1×、第 2 次等 2×……）后重试
  - 错误非 retryable（或没传 retryable）→ 立即上抛
  - 重试耗尽 → 上抛最后一次错误
- 顶层挂 `process.on("unhandledRejection", …)`：打印带时间戳的日志兜底（README 核心概念 3：最后的兜底网）
- 演示三个场景：
  - 成功场景：一个「前 2 次失败、第 3 次成功」的任务（内部计数），打印每次尝试/等待/最终成功的时间线
  - 耗尽场景：`retries: 2` 但一直失败 → 上抛最后一次错误
  - 不可重试场景：抛非 NetworkError（或 `retryable` 返回 false）→ 立即上抛

### 技术要点
- 退避重试算法：循环 + `await sleep(backoffMs * attempt)`（s04 async 复习：async 函数里的 throw 变成 reject）
- 错误分类：`retryable` 判别函数决定「这个错误能不能恢复」——和需求 1 的 `NetworkError.retryable` 字段配合最自然
- 未捕获兜底：`unhandledRejection` 是最后一张网，只该记录/上报，不该吞掉业务逻辑（README 核心概念 3：没监听器时进程以非 0 码退出）
- 类型安全：`retry<T>` 泛型保证重试成功后拿回 `T`

### 超纲提示
- 🔧 指数退避 + 抖动（jitter）：`backoffMs * 2 ** attempt` 再乘随机系数 `0.5~1`，防止大量客户端同时重试打爆服务（thundering herd）
- 🔧 配合 s07 装的 chalk 给日志上色（成功/重试/失败三种颜色）

### 自测方法
- 建议解答文件：`s32_typescript/s10_error_handling/practice_retry.ts`
- `node s32_typescript/s10_error_handling/practice_retry.ts`：三种场景输出清晰（成功场景能看到 2 次退避等待；耗尽场景上抛最后一次错误；不可重试场景立即上抛）
- 故意忘 catch 一个 Promise（`void Promise.reject(new Error("漏网的"))`）→ 观察 unhandledRejection 兜底日志
- `cd s32_typescript && npm run typecheck`：0 错误

## 做完之后
- 自查：你用了本章哪些概念？
  - 自定义错误类（extends Error + name 修正 + 上下文字段）
  - instanceof 分层判断 / e: unknown 收窄
  - Result 判别联合 vs throw 的选择标准
  - 异步错误三条路（await+catch / .catch / unhandledRejection 兜底）
  - 退避重试算法（s04 async 复用）
- 想继续深挖：回看本章 README 的「跟 Agent 的关系」——「接住能恢复的，抛出让上层处理的，兜底剩下的」就是 s11_error_recovery 的静态结构；选一个点展开：比如给 retry 加退避上限（cap），或把 handleError 升级成「错误 → 用户可读消息 + 是否可恢复」的完整映射
