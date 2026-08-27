# s32-09: class — 动手需求

[← 返回总索引](../PRACTICE.md) | [本章教程](./README.md)

> 一句话核心思想：**class 是「数据 + 操作数据的方法」的打包；TS 在 JS class 之上加了类型检查，但只有 `#` 私有是运行时真隔离。**

学完本章，用下面这些需求把知识变成肌肉记忆。**只给需求和提示，不给完整代码**——卡住了回到主项目提问。

## 使用说明
- 前置技能：s01~s09（interface/type、泛型、async/Promise 都要能随手用）
- 自测方式：node 直跑（`node s32_typescript/s09_class/practice_*.ts`）+ `cd s32_typescript && npm run typecheck`
- 解答文件建议放本章目录内，命名 `practice_<名字>.ts`
- 项目约定：相对导入必须带 `.ts` 扩展名（如 `import { Color } from "../utils.ts"`）；只用可擦除语法（避开 enum/namespace/参数属性/装饰器）；涉及文件路径一律 `import.meta.dirname`

## 需求 1：钱包类（⭐ 入门 | 核心技能：#私有字段 + getter/setter 门禁）
- [ ] 完成

### 背景
README 的 BankAccount 换个场景重做——钱包人人有数：余额变动留流水，外面只能通过门禁操作，谁也别想直接改余额。把「封装保护数据」练成本能。

### 要做什么（验收标准）
- `class Wallet`，字段全私有：
  - `#balance: number`（运行时真私有）
  - `#ledger: LedgerEntry[]`，`type LedgerEntry = { type: "deposit" | "withdraw"; amount: number; time: string }`（时间用 `new Date().toISOString()`）
  - 至少一个 `private` 字段（如 `private owner: string`）——没有它就没有「# vs private」的对照组
- `deposit(amount)`：非正数 → 抛错或返回 Result（选一种，注释里说明为什么）
- `withdraw(amount)`：校验正数 + 余额充足；不足 → 抛错或返回 Result
- `get balance`：只读暴露余额（不写 setter）
- `get statements()`：返回流水**副本**（`[...this.#ledger]`）——外部改返回的数组不得影响内部
- 对照演示：`(wallet as any)` 能拿到 `private owner`，但拿不到 `#balance`，打印两个结果

### 技术要点
- `#` 私有 = 运行时真私有（存在私有槽里，`as any` 也进不去）；`private` 只挡编译期，擦除后等于没有（README 核心概念 1：数据安全用 `#`，协作提示用 `private`）
- getter 只读暴露：只有 `get` 没有 `set`，外面「看起来像读属性」，实际走方法
- 门禁方法：所有写入都经过方法内校验（正数、余额充足），数据永远从门禁进出
- 可擦除语法：本模块禁用参数属性（`constructor(private x: number)` 不可擦除，node 直跑报错），用「显式声明字段 + 构造函数赋值」（README 核心概念 2）

### 超纲提示
- 🔧 `Object.keys(wallet)` 看不到 `#` 字段（README 表格有对照）——跑一下验证
- 🔧 `#` 字段连 `JSON.stringify` 都序列化不出来；想给外部可序列化视图，就在 getter 里自己拼对象

### 自测方法
- 建议解答文件：`s32_typescript/s09_class/practice_wallet.ts`
- `node s32_typescript/s09_class/practice_wallet.ts`：看到存取过程、余额变化、流水列表
- 越权尝试：`(wallet as any).owner` 能打印；`(wallet as any)["#balance"]` 是 `undefined`；`wallet.balance = 999` 编译报错（只读）
- `cd s32_typescript && npm run typecheck`：0 错误

## 需求 2：图形类层次（⭐⭐ 组合 | 核心技能：abstract + extends + 多态）
- [ ] 完成

### 背景
README 实验 2 的完整版：抽象类立规矩（必须有 area 和 perimeter），子类各实现各的，多态统一调度。只做 area 太轻，带上 perimeter + 共享 describe 才把 abstract/extends/多态一次练全。

### 要做什么（验收标准）
- `abstract class Shape`：
  - `abstract area(): number`
  - `abstract perimeter(): number`
  - `describe(): string` 共享实现——内部调用 `this.area()` / `this.perimeter()`（这里就是多态现场：父类代码调用子类实现）
- `class Circle extends Shape`（半径）、`class Rectangle extends Shape`（宽高）、`class Triangle extends Shape`（底高，面积 底×高÷2）
- `const shapes: Shape[] = [new Circle(2), new Rectangle(4, 5), new Triangle(6, 3)]`，循环统一调 `area()` / `perimeter()` / `describe()`，打印对齐表格（名称 | 面积 | 周长）
- 新增 `class Pentagon extends Shape` **故意漏实现** `area()` → `npm run typecheck` 报错；补上实现后再跑通过（把报错记下来）

### 技术要点
- `abstract` 方法 = 契约：子类必须实现，漏了编译期报错（README 核心概念 3：abstract = 模板 + 规矩）
- `extends` 复用代码：`describe()` 写在父类，所有子类共享；子类只写差异（自己的字段 + area/perimeter 实现）
- 多态：数组元素统一标注 `Shape`，运行时每个元素调用自己的 `area()` / `perimeter()` 实现
- 提示：子类构造函数里要先调 `super()`（Circle 的写法参考 code.ts）

### 超纲提示
- 🔧 对比 s03 需求 3 的判别联合版形状系统（`type Shape = { kind: "circle"; r: number } | …` + `switch` 收窄）：联合版数据与函数分离、加新形状要改 switch 和 never 穷尽检查；类层次版数据与方法打包、加新形状只加新类。各自优缺点写 2~3 句到文件注释里

### 自测方法
- 建议解答文件：`s32_typescript/s09_class/practice_shapes.ts`
- `node s32_typescript/s09_class/practice_shapes.ts`：输出三行对齐表格
- `cd s32_typescript && npm run typecheck`：0 错误
- 临时删掉 `Pentagon` 的 `area()` → typecheck 报「非抽象类没有实现继承的抽象成员」→ 恢复再查

## 需求 3：任务队列类（⭐⭐⭐ 挑战 | 核心技能：类 + 泛型 + 事件回调）
- [ ] 完成

### 背景
把 s04 需求 3 的并发调度器对象化成类并加事件回调——这是库设计的雏形：内部状态收进 `#` 私有，对外只露 `add` / `run` / `on` 三个口子。TaskQueue 是 mini 版任务调度库，Agent 的工具执行器就是这种形态。

### 要做什么（验收标准）
- `class TaskQueue<T>`：
  - `constructor(concurrency: number)`
  - `add(fn: () => Promise<T>): void`——入队
  - `run(): Promise<void>`——按并发上限执行，全部任务完成才 resolve
  - `on(cbs: OnCallbacks<T>): void`——订阅事件
- 回调用接口描述：`interface OnCallbacks<T> { done?: (result: T) => void; error?: (e: unknown) => void; empty?: () => void }`（不用 EventEmitter，自己用数组/Map 实现简单订阅）
- 队列内部状态（等待中的任务、运行中的计数、回调注册表）一律 `#` 私有
- 演示：8 个任务、`new TaskQueue<number>(3)`，任务用 `setTimeout` 模拟耗时并打印开始/结束时间线（能看出任何时刻最多 3 个在跑）；订阅 `done` / `empty` 回调打印进度

### 技术要点
- 泛型类：`class TaskQueue<T>` 把任务结果类型参数化（s08 泛型 × 本章 class）
- `#` 私有内部状态：等待队列、并发计数、回调列表——外面摸不到，只能通过 add/run/on 交互
- 回调接口：`OnCallbacks` 字段全可选（s02 接口 + 可选属性），订阅时只传需要的
- 并发窗口：复用 s04 需求 3 的思路（启动 `concurrency` 个 worker，一个完成就拉下一个），这次把状态装进类里
- 可擦除语法：字段显式声明，禁用参数属性

### 超纲提示
- 🔧 换成 Node 原生 `EventEmitter`（`node:events`）重写一版：`queue.on("done", …)`——对比「自己实现订阅 vs 原生事件系统」，体会 `once` / `off` / 多监听器

### 自测方法
- 建议解答文件：`s32_typescript/s09_class/practice_task_queue.ts`
- `node s32_typescript/s09_class/practice_task_queue.ts`：输出时间线显示并发上限 3（任何时刻最多 3 个任务在跑）、done/empty 回调触发、8 个任务全部完成
- `cd s32_typescript && npm run typecheck`：0 错误

## 做完之后
- 自查：你用了本章哪些概念？
  - `#` 私有字段 vs `private`（运行时真隔离 vs 编译期约定）
  - getter / setter 门禁（只读暴露、写时校验）
  - abstract / extends / 多态（父类代码调用子类实现）
  - 泛型类（TaskQueue<T>）
  - 可擦除语法（显式字段声明，避开参数属性）
- 想继续深挖：回看本章 README 的「跟 Agent 的关系」——SDK 里 `class AgentLoop { #config }`、`class ToolExecutor implements Tool`；选一个点展开：比如给任务队列的 `on` 订阅升级成 `implements` 一个接口的形态，或给 Shape 家族再加 `implements HasArea` 的多接口承诺，体会 extends 与 implements 的分工
