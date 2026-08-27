# s32-01: TypeScript 基础语法 — 动手需求

[← 返回总索引](../PRACTICE.md) | [本章教程](./README.md)

> 一句话本章核心思想：**类型标注不改变代码的运行，只改变机器检查代码的能力。**

学完本章，用下面这些需求把知识变成肌肉记忆。**只给需求和提示，不给完整代码**——卡住了回到主项目提问。

## 使用说明
- 前置技能：s01（本章）——TypeScript 基础语法，会基础 JavaScript 即可
- 自测方式：`node s32_typescript/s01_ts_basics/practice_xxx.ts` 从仓库根直跑看输出；`cd s32_typescript && npm run typecheck` 零报错
- 解答文件建议放本章目录内，命名 `practice_<名字>.ts`

## 需求 1：命令行 BMI 计算器（⭐ 入门 | 核心技能：函数标注/推断、模板字符串）
- [ ] 完成

### 背景
第一个程序别碰框架——一个「输入 → 计算 → 输出」的命令行小程序，就能把标注、推断、函数契约全部用一遍。跑通它的瞬间，你会真切看到「类型标签在编译期起作用、运行时被撕掉」。

### 要做什么（验收标准）
1. 写 `s32_typescript/s01_ts_basics/practice_bmi.ts`：`node s32_typescript/s01_ts_basics/practice_bmi.ts 170 60` 输出类似 `BMI: 20.8（正常）`，BMI 保留 1 位小数。
2. 体型判断：BMI < 18.5 → 偏瘦；< 24 → 正常；否则 → 偏胖。
3. 参数缺失或非数字：给友好提示（如「用法：practice_bmi.ts <身高cm> <体重kg>」），不崩溃。
4. `cd s32_typescript && npm run typecheck` 零报错。

### 技术要点
- 函数参数、返回类型**显式标注**：`function bmi(heightCm: number, weightKg: number): number`——参数标注是输入契约，返回标注是输出契约
- 命令行来的是字符串，用 `Number()` 转换；`Number("abc")` 得到 `NaN`，记得用 `isNaN` 拦住
- 模板字符串 `` `BMI: ${...}` `` 拼输出，保留 1 位小数用 `toFixed(1)`
- 体型分类用**字面量联合类型**（`type BodyType = "偏瘦" | "正常" | "偏胖"`）或 `as const` 对象——这是可擦除语法，**别用 enum**（node 直跑会报错，项目约定）
- 能推断的不写：`const weight = Number(process.argv[3])` 交给推断即可

### 超纲提示
🔧 `process.argv` 是 s06 的内容，提前用没关系——先 `console.log(process.argv)` 看数组结构：第 0 个是 node，第 1 个是脚本路径，第 2 个起才是你的参数。

### 自测方法
```bash
node s32_typescript/s01_ts_basics/practice_bmi.ts 170 60    # → BMI: 20.8（正常）
node s32_typescript/s01_ts_basics/practice_bmi.ts 160 45    # → 偏瘦
node s32_typescript/s01_ts_basics/practice_bmi.ts 175 80    # → 偏胖
node s32_typescript/s01_ts_basics/practice_bmi.ts 170       # 缺参数 → 友好提示
node s32_typescript/s01_ts_basics/practice_bmi.ts abc 60    # 非数字 → 友好提示
cd s32_typescript && npm run typecheck                      # 零报错
```

## 需求 2：记账小本本（内存版）（⭐⭐ 组合 | 核心技能：对象数组、数组方法、类型标注）
- [ ] 完成

### 背景
对象形状 + 数组操作是数据类应用的骨架——定义形状、存数据、算统计，一条链跑完，你对「类型描述数据」就有了手感。

### 要做什么（验收标准）
1. 定义 `Transaction` 类型：`{ date: string; amount: number; category: "food" | "transport" | "other" }`。
2. 写 4 个函数：`add`（加一笔）、`list`（列全部）、`total`（总额）、`sumByCategory`（分类小计）。
3. 硬编码或 argv 输入 4~5 笔账（覆盖三种分类），输出总额和三个分类的小计。
4. typecheck 零报错。

### 技术要点
- `type` 描述对象形状（s02 正式学，这里先用简单的内联 `type`）
- `category` 用**字面量联合类型** `"food" | "transport" | "other"`——写错分类编译期就报错
- `reduce` 算总额、`filter` 分组算分类小计
- 数组函数参数可以带**可选参数默认值**（如 `list(category?: Transaction["category"])`——索引访问类型 `Transaction["category"]` 可以先亮出来）
- 想拆模块（如把类型放 `types.ts`）：**相对导入必须带 `.ts` 扩展名**：`import { Transaction } from "./types.ts"`（项目约定，缺了就 `ERR_MODULE_NOT_FOUND`）

### 超纲提示
🔧 持久化到 JSON 文件：查 `fs/promises` 的 `writeFile` / `readFile`（s11 内容）。写文件路径一律用 `import.meta.dirname`（项目约定：从仓库根跑时 `process.cwd()` 会写错位置）。

### 自测方法
```bash
node s32_typescript/s01_ts_basics/practice_ledger.ts   # 输出总额 + food/transport/other 三个小计
# 实验：把某笔 amount 改成负数，观察你的「合法」定义——校验拦住它了吗？
cd s32_typescript && npm run typecheck
```

## 需求 3：外部输入守卫（⭐⭐⭐ 挑战 | 核心技能：any vs unknown、typeof 收窄）
- [ ] 完成

### 背景
「外部数据 unknown → 验证 → 使用」是 s01 最值钱的实战习惯——Claude Code 处理 API 响应就是这套思路（见本章 README「跟 Agent 的关系」）。这道题把它亲手实现一遍。

### 要做什么（验收标准）
1. `parseProfile(raw: unknown)`：校验字段存在、类型正确、范围合法，成功返回精确类型对象（如 `{ name: string; age: number; email?: string }`），失败返回错误描述字符串——**不 throw**。
2. `parseScores(raw: unknown)`：校验 `scores` 是数字数组且每项在 0~100，成功返回 `number[]`，失败返回错误描述字符串。
3. 再写一个用 `any` 的对照版本（同样的数据流），演示它**哪里会运行时崩**（比如对 `null` 直接调 `.length`）。
4. 用四组数据自测：合法 / 缺字段 / 类型错 / 范围错，typecheck 零报错。

### 技术要点
- `unknown` 上**不能直接操作**——先收窄再用；`any` 编译期放行、运行时爆炸（逃课生 vs 转学生）
- `typeof` 收窄：`typeof raw === "object"` 只说明"可能是对象"，**`typeof null === "object"`**——对象判断必须 `x !== null && typeof x === "object"`
- 字段级校验：先看 `"name" in raw`，再 `typeof raw.name === "string"`（`in` 是 s03 正式内容，这里先直接上手）
- 返回类型写清楚：`parseProfile(raw: unknown): { name: string; age: number; email?: string } | string`——成功/失败两种形态
- 只用可擦除语法（避开 enum / namespace / 参数属性 / 装饰器），tsconfig 的 `erasableSyntaxOnly` 会盯着你

### 超纲提示
🔧 完整收窄武器库在 s03：`in` 收窄、判别联合（discriminated union）、类型守卫 `x is T`——做完 s03 回来把这版 parse 重写一遍，对比手感。

### 自测方法
```bash
node s32_typescript/s01_ts_basics/practice_guard.ts
# 合法 / 缺字段 / 类型错 / 范围错 四组数据各跑一遍，失败时看到的是错误描述而不是崩溃堆栈
cd s32_typescript && npm run typecheck
```

## 做完之后
- 自查：你用了本章哪些概念？（类型标注 vs 推断 / any vs unknown / typeof 收窄 / 函数契约标注 / 字面量联合或 as const / 数组与元组）
- 想继续深挖：回看本章 README 的「跟 Agent 的关系」——把 `unknown → 层层收窄 → 精确类型` 的链路在你的 `parseProfile` 里用注释标注出来，对照 Claude Code 处理 API 响应的写法
