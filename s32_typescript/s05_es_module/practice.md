# s32-05: ES Module — 动手需求

[← 返回总索引](../PRACTICE.md) | [本章教程](./README.md)

> 一句话本章核心思想：**模块 = 代码的集装箱：有自己的命名空间、自己的缓存、明确的进出口。**

学完本章，用下面这些需求把知识变成肌肉记忆。**只给需求和提示，不给完整代码**——卡住了回到主项目提问。

## 使用说明
- 前置技能：s01~s05（s01 的 BMI 计算器、s04 的 async 会用到）
- 自测方式：`node s32_typescript/s05_es_module/<文件名>.ts` 直跑；`cd s32_typescript && npm run typecheck` 零报错
- 解答文件建议放本章目录内，命名 `practice_<名字>.ts`；多文件需求按需求里给出的文件名（如 `bmi-lib.ts` / `main.ts`）

## 需求 1：模块化重构 — 把 s01 的 BMI 计算器拆开（⭐ 入门 | 核心技能：export/import、模块缓存）
- [ ] 完成

### 背景
单文件能跑 ≠ 会写工程。s01 的 BMI 计算器是"一个人写完整个程序"；本章的课题是"把计算和界面拆开，各管各的"。用已经会的东西练拆模块，是最低成本的第一次工程化。

### 要做什么（验收标准）
1. `bmi-lib.ts`：纯函数 + 类型，不含任何 console.log / process 调用——
   - `parseInput(args: string[]): { weight: number; height: number }`：把命令行参数（体重 kg、身高 cm）解析成数值对象，解析失败直接 throw（s10 会系统讲错误处理，先用 throw 顶住）
   - `calcBmi(weight: number, height: number): number`：BMI = weight / (height/100)²
   - `classifyBmi(bmi: number): string`：按 <18.5 偏瘦 / <24 正常 / ≥24 偏胖 三档返回
2. `bmi-lib.ts` 顶层加一行 `console.log("[bmi-lib] 模块已加载")`——这是给"模块缓存"留的证据
3. `main.ts`：用**两个命名空间**导入同一个 bmi-lib（如 `import * as lib1` 和 `import * as lib2`），各自走一遍 `parseInput` → `calcBmi` → `classifyBmi`，打印结果；argv 为空时打印用法提示
4. 跑 `main.ts`：`[bmi-lib] 模块已加载` **只打印一次**（import 两次 ≠ 执行两次）
5. `cd s32_typescript && npm run typecheck` 零报错

### 技术要点
- **命名导出 vs 默认导出**：工具集（多个函数）用命名导出；一个模块一个主角才用默认导出（README 核心概念 1）
- **相对导入必须带 `.ts` 扩展名**：`import { calcBmi } from "./bmi-lib.ts"`，缺了就是 `ERR_MODULE_NOT_FOUND`——本项目铁律
- **模块缓存 = 模块级单例**：模块按 URL 缓存，顶层副作用只发生一次——用两个命名空间导入来证明它（README 核心概念 2）
- **计算与 I/O 分离（职责边界）**：bmi-lib 只算不打印（纯函数），main 只负责取参数、打印——README"模块边界 = 职责边界"的迷你版
- 纯类型导入用 `import type`（本项目开了 `verbatimModuleSyntax`，类型和值导入要分开写）

### 超纲提示
🔧 试 `import * as bmi from "./bmi-lib.ts"` 一次导入全部导出，用 `bmi.calcBmi(...)` 调用——命名空间导入是 s05 的 code.ts 演示模块缓存时用的姿势，正式学它。

### 自测方法
```bash
node s32_typescript/s05_es_module/main.ts 170 65      # 应打印 BMI 数值 + 分类
node s32_typescript/s05_es_module/main.ts             # 无参数 → 用法提示
# 观察输出：即使 import 了两次，"[bmi-lib] 模块已加载"也只出现一次
cd s32_typescript && npm run typecheck                # 零报错
# 实验：给 bmi-lib.ts 加一个模块级计数器（每次 calcBmi 调用 +1），
#       在 main 的两个命名空间里分别读，看是不是同一个实例
```

## 需求 2：插件注册表 — 迷你插件系统（⭐⭐ 组合 | 核心技能：模块级单例 + 副作用导入）
- [ ] 完成

### 背景
Agent/框架生态里的插件机制，核心就两样东西：**一个注册表（模块级单例）+ 插件"导入即注册"（副作用导入）**。模块缓存让"谁先 import、谁后 import"都不重要——这正是插件能乱序加载的原因。把这两样写出来，你就理解了插件系统的地基。

### 要做什么（验收标准）
1. `registry.ts`：模块级 `Map<string, Plugin>` 存插件 + 两个导出——
   - `registerPlugin(name: string, plugin: Plugin): void`
   - `runAll(): void`（遍历 Map，调用每个插件的 `run()`）
   - 用接口类型约定插件形状：`interface Plugin { name: string; run(): void }`
2. `plugin-a.ts` / `plugin-b.ts`：各自 `import { registerPlugin } from "./registry.ts"`，**在模块顶层**调用 `registerPlugin(...)` 注册自己——这就是副作用导入：import 一个模块时，它顺手把注册的事干了
3. `plugin-main.ts`（避免和需求 1 的 main.ts 重名）：**只 import 模块本身，不 import 插件内容**——`import "./plugin-a.ts"` / `import "./plugin-b.ts"` 这种副作用导入 + `import { runAll } from "./registry.ts"`，然后 `runAll()`
4. 故意打乱 import 顺序（先 b 后 a），`runAll()` 的结果不变
5. typecheck 零报错

### 技术要点
- **模块级状态 = 天然单例**：registry 里的 Map 是模块级变量，整个进程只有一份（README 核心概念 2）
- **"导入即注册"的副作用导入**：`import "./plugin-a.ts"` 不取任何导出，只为了执行它的顶层代码——这就是插件系统的装载机制
- **用接口类型约定插件形状**：Plugin 接口就是插件协议，注册表只认接口、不认识具体实现
- 相对导入带 `.ts` 扩展名；插件模块顶层只做注册，别在顶层做重活（和 README 循环依赖"死穴"同款风险）

### 超纲提示
🔧 循环依赖规避口诀复习（README 核心概念 3）：插件只 import registry，**绝不反向 import main.ts**——插件需要 main 提供的东西时，把"东西"挪进 registry 或独立模块，让依赖方向永远是 插件 → 注册表 →（无）。

### 自测方法
```bash
node s32_typescript/s05_es_module/plugin-main.ts   # 应看到两个插件的输出
# 实验 1：把 import "./plugin-a.ts" 和 "./plugin-b.ts" 的顺序对调 → 结果不变（缓存 + 注册表无顺序依赖）
# 实验 2：在 plugin-main.ts 里再 import 一次 "./plugin-a.ts" → 输出不会重复注册（模块只执行一次）
cd s32_typescript && npm run typecheck
```

## 需求 3：两套模块系统的桥 — CJS/ESM 互操作（⭐⭐⭐ 挑战 | 核心技能：createRequire、动态 import()、CJS/ESM 互操作）
- [ ] 完成

### 背景
真实 Node 项目里，CJS 老库和 ESM 新代码永远共存。README 给了判定规则和两条互操作路径，但只有亲手"从 ESM 调 CJS、再从 CJS 侧调 ESM"跑一遍，规则才会长在手上。本项目的 package.json 声明了 `"type": "module"`，所有 .ts 都是 ESM——正好当互操作的试验台。

### 要做什么（验收标准）
1. `legacy-tool.cjs`：CommonJS 模块，`module.exports` 一个工具函数（如 `legacyGreet(name)`）+ 一个值（如 `version`）
2. `esm-tool.ts`：ESM 模块，正常 `export`，顶层放一行 console.log 证明它被（动态）加载过
3. `bridge-main.ts`：
   - 路径 A：`createRequire(import.meta.url)` 得到 require，用它加载 `./legacy-tool.cjs` 并调用（ESM → CJS）
   - 路径 B：`await import("./esm-tool.ts")` 动态加载并调用（这是 CJS 调 ESM 的唯一姿势；.ts 里没法真用 require，就用动态 import 演示"返回 Promise"这一侧）
   - 打印两条路径的输出，注释里对比：静态 import 在文件顶部解析、动态 import() 是运行时的 Promise——各适合什么场景
4. typecheck 零报错（`.cjs` 不在 tsc 的检查范围，放心写）

### 技术要点
- **createRequire(import.meta.url)**：在 ESM 里造一个以"当前模块"为基准的 require（README 互操作示例）
- **动态 import() 返回 Promise**：CJS 里同步 require 不到 ESM，只能 `await import()`；顶层 await 是 ESM 特权（README 判定规则表）
- **判定规则**：`.cjs` 后缀强制 CJS；package.json `"type": "module"` 让所有 .ts 按 ESM 解析（README 核心概念 4）
- 动态 import 的返回值要自己收窄类型（它给的类型可能不精确），可以 `as` 断言成你定义的形状

### 超纲提示
🔧 ESM 里没有 `__dirname`/`__filename`——那是 CJS 的全局。ESM 用 `import.meta.dirname` / `import.meta.url` 自定位（s06 的 code.ts 到处在用，s11 讲文件系统时会大量依赖它）。

### 自测方法
```bash
node s32_typescript/s05_es_module/bridge-main.ts
# 应看到：路径 A（CJS 工具）的输出 + 路径 B（ESM 模块）的输出 + esm-tool.ts 的顶层日志
cd s32_typescript && npm run typecheck
# 实验：把 legacy-tool.cjs 改成 legacy-tool.mjs（用 export 语法），
#       再用 createRequire 加载它——看报错，理解"判定规则"是怎么生效的
```

## 做完之后
- 自查：你用了本章哪些概念？——命名/默认导出、带 `.ts` 扩展名的相对导入、模块缓存（模块级单例）、副作用导入、createRequire、动态 import()、CJS/ESM 判定规则
- 想继续深挖：回看本章 README 的"跟 Agent 的关系"，选一个点展开——比如把需求 2 的插件注册表扩展成"技能加载器"：每个插件文件声明自己能处理什么，main 按需加载
