# s32: TypeScript 实战 — 给 JavaScript 装上类型安全网

> *"TypeScript 不是一门新语言。TypeScript 是给 JavaScript 数据贴标签，让机器在运行之前帮你抓错。"*
>
> 本课程面向**有 JavaScript 基础、想系统掌握 TypeScript + Node.js** 的学习者。
> 每一章只比上一章多一个概念，每一步都讲清楚「为什么」。
> 最终目标是：**能够独立用 TypeScript + Node.js 写应用**。

---

## 这个模块为什么与众不同：零配置直跑

传统的 TS 教程第一课教你装一堆东西、配 tsconfig、跑构建。本课程反其道而行之：

```bash
node s32_typescript/s01_ts_basics/code.ts   # 直接跑，无需编译！
```

**因为 Node 22.18+ 原生支持类型擦除（type stripping）**——Node 在运行前自动撕掉类型标签，剩下的就是纯 JavaScript。这正好让"类型只在编译期存在"这个核心心智模型**活生生地呈现在你眼前**。

> ❓ **完全零基础？** 从 [s00](s00_mental_model/) 开始 — 纯概念，不写代码，先建立「类型=标签 / 编译器=质检员 / 擦除」的心智模型。

---

## 开始之前：环境要求

- **Node.js ≥ 22.18**（type stripping 默认开启的最低版本）—— `node --version` 检查
- 会基础的 JavaScript（let/const、函数、对象）即可
- 安装依赖（**仅 s07/s13/s14 需要**）：

```bash
cd s32_typescript
npm install        # 或 pnpm install（s07 会对比两者）
```

- 教程代码零构建运行：`node s32_typescript/sXX/code.ts`
- 唯一例外：**s13 装饰器章**需要编译，运行 `npm run demo:s13`

---

## 学习路线图

```
s00  心智模型               ← 纯概念：类型=标签 / 编译器=质检员
 │
s01  TS 基础语法     ⭐⭐⭐⭐⭐  标注、推断、any vs unknown
s02  interface/type  ⭐⭐⭐⭐⭐  给对象形状贴标签、声明合并
s03  union/narrowing ⭐⭐⭐⭐⭐  一个变量多种类型，如何安全收窄
 │
s04  async/Promise   ⭐⭐⭐⭐⭐  异步世界的三态与事件循环
s05  ES Module       ⭐⭐⭐⭐⭐  import/export、模块缓存、循环依赖
s06  Node.js         ⭐⭐⭐⭐⭐  事件循环、process、最小 http server
 │
s07  npm / pnpm      ⭐⭐⭐⭐   package.json、semver、实装一个依赖
s08  泛型            ⭐⭐⭐⭐   类型也能当参数
s09  class           ⭐⭐⭐⭐   修饰符、#私有字段、抽象类
s10  Error/异常处理  ⭐⭐⭐⭐   自定义错误、异步错误、Result 模式
 │
s11  文件系统/subprocess ⭐⭐⭐⭐  fs/promises、流、child_process
 │
s12  高级类型        ⭐⭐⭐   keyof、条件类型、infer、映射类型
s13  Decorator       ⭐⭐⭐   装饰器（唯一需要编译的章节）
s14  Compiler API    ⭐⭐     用 TypeScript 解析 TypeScript（AST）
s15  类型体操        ⭐       把类型系统当编程语言玩
 │
s16  综合实战：HTTP API 服务器  ← 串起全部知识，检验学习目标
```

---

## 模块总览

| # | 模块 | 要解决的问题 | 跟 Agent 的关系 |
|---|------|-------------|----------------|
| s00 | [心智模型](s00_mental_model/) | "TypeScript 到底是什么？" | 读 Claude Code 源码的地图 |
| s01 | [基础语法](s01_ts_basics/) | "类型怎么写上去？" | 源码里的 unknown→narrowing 链 |
| s02 | [interface/type](s02_interface_type/) | "对象的形状怎么描述？" | MCP 协议类型契约 |
| s03 | [union/narrowing](s03_union_narrowing/) | "一个变量多种类型怎么办？" | Agent 解析工具参数的校验 |
| s04 | [async/Promise](s04_async/) | "异步代码怎么写才不乱？" | Agent 循环并行调用工具 |
| s05 | [ES Module](s05_es_module/) | "代码怎么拆成模块？" | Claude Code 的包结构与导入边界 |
| s06 | [Node.js](s06_node/) | "代码跑在什么底座上？" | Agent 的运行时底座 |
| s07 | [npm/pnpm](s07_pkg_manager/) | "依赖怎么管理？" | Claude Code 依赖树与锁文件 |
| s08 | [泛型](s08_generics/) | "类型怎么复用？" | SDK 工具函数抽泛型的思路 |
| s09 | [class](s09_class/) | "面向对象怎么写？" | SDK 类设计；# 私有才是真封装 |
| s10 | [Error/异常处理](s10_error_handling/) | "出错了怎么办？" | Agent 错误恢复机制的 TS 实现 |
| s11 | [文件系统/subprocess](s11_fs_process/) | "怎么读写文件、调用外部程序？" | Agent 的 Read/Write/Bash 文件层 |
| s12 | [高级类型](s12_advanced_types/) | "类型系统还能更强？" | SDK 高阶类型推导 |
| s13 | [Decorator](s13_decorator/) | "怎么给代码声明式加功能？" | NestJS/MCP server 框架写法 |
| s14 | [Compiler API](s14_compiler_api/) | "工具怎么分析代码？" | 编辑器工具的语言分析层 |
| s15 | [类型体操](s15_type_gymnastics/) | "类型系统的极限在哪？" | 读 .d.ts 库源码不再怕 |
| s16 | [HTTP API 服务器](s16_capstone/) | "怎么独立写一个应用？" | 亲手做一个 mini Agent 工具 |

---

## 快速开始

```bash
# 1. 检查环境（Node 22.18+）
node --version

# 2. 安装依赖（仅 s07/s13/s14 需要，可选）
cd s32_typescript && npm install && cd ..

# 3. 跑第一章
node s32_typescript/s01_ts_basics/code.ts

# 4. 类型检查（质检员上班，需要步骤 2）
cd s32_typescript && npm run typecheck
```

## 模块约定（写代码时必读）

1. **相对导入必须带 `.ts` 扩展名**：`import { Color } from "../utils.ts"` —— Node ESM + type stripping 的硬要求，缺了就 `ERR_MODULE_NOT_FOUND`
2. **禁止 tsconfig `paths` 别名** —— type stripping 不解析别名，纯相对路径是唯一正解
3. **node 直跑的代码只能用可擦除语法** —— 避开 `enum`、`namespace`、参数属性、装饰器（README 会讲这些语法，code.ts 用替代写法）；tsconfig 的 `erasableSyntaxOnly` 已把这变成编译期契约
4. **路径一律 `import.meta.dirname`** —— 绝不依赖 `process.cwd()`（从仓库根跑时会写错位置）
5. **同一项目不要 npm/pnpm 来回 install** —— node_modules 布局不同会互相污染

## 故障排查

| 症状 | 原因 | 解决 |
|---|---|---|
| `SyntaxError: Unexpected token ':'` 或 strip types 报错 | Node < 22.18 | `node --version` 检查，升级到 22.18+ |
| `ERR_MODULE_NOT_FOUND` | 导入路径缺 `.ts` 扩展名 | 补上扩展名（见模块约定 1） |
| 跑 s07 报 `Cannot find package 'chalk'` | 没装依赖 | `cd s32_typescript && npm install` |
| 跑 s13 报装饰器语法错误 | s13 不能 node 直跑 | 用 `npm run demo:s13` |
