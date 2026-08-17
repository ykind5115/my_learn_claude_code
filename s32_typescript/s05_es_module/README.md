# s32-05: ES Module — 把代码拆成可复用的模块

[← 返回概览](../README.md) | [上一章：async / Promise](../s04_async/) | [下一章：Node.js](../s06_node/)

> 一句话核心思想：**模块 = 代码的集装箱：有自己的命名空间、自己的缓存、明确的进出口。**

---

## 问题 — 为什么需要模块？

没有模块的 JS 世界（上古年代）：

```html
<script src="a.js"></script>
<script src="b.js"></script>
<!-- a.js 和 b.js 的变量全部挤在全局，谁覆盖谁看运气 -->
```

三个致命问题：**全局污染**（变量互相覆盖）、**依赖顺序靠 script 标签排列**（改顺序就炸）、**无法复用**（复制粘贴）。

ES Module（ESM）是标准答案。Node 同时存在两套系统——老牌的 CommonJS（CJS，`require`）和现代的 ESM（`import`），本章两套都讲，因为真实世界里它们共存。

---

## 原理 — 一句话 + 示意图

**每个模块是一个独立作用域，通过 export 亮出出口，通过 import 接入依赖。**

```
            lib-a.ts                  lib-b.ts
        ┌─────────────┐          ┌─────────────┐
        │ 内部变量    │          │ 内部变量    │
        │ 外部不可见  │          │ 外部不可见  │
        │             │  import  │             │
        │ export greet│ ←────── │ export getB │
        │ export aVal │   ──────→│ import aVal │
        └─────────────┘  import  └─────────────┘
             ▲   互相依赖 = 循环依赖
             └───────────────┘

   code.ts 从两个模块 import，各取所需
```

---

## 核心概念 — 分点讲解

### 1. 命名导出 vs 默认导出

```typescript
// lib-a.ts —— 命名导出（多个）
export const aValue = "A";
export function greet(name: string) { return `你好，${name}！`; }

// lib-b.ts —— 默认导出（一个）
export default function defaultGreet(name: string) { ... }

// 导入方
import { greet, aValue } from "./lib-a.ts";   // 点名，必须用原名
import defaultGreet from "./lib-b.ts";        // 默认导出，随便起名
import * as libA from "./lib-a.ts";           // 全部打包进命名空间
```

**工程惯例**：一个模块只导一个主角时用默认导出（如组件、类）；工具集用命名导出（如 utils.ts）。**本模块规则：相对导入必须带 `.ts` 扩展名**（Node ESM 硬要求）。

### 2. 模块缓存：整个进程只执行一次

```typescript
import * as libA1 from "./lib-a.ts";
import * as libA2 from "./lib-a.ts";
libA1.visit();  // count → 1
libA2.visit();  // count → 2 —— 同一个实例！
```

模块按 URL 缓存。**模块级状态 = 天然的单例**，副作用只发生一次。

### 3. 循环依赖：不会立刻爆炸，但有个死穴

lib-a 和 lib-b 互相 import，为什么没炸？因为 ESM 的两个机制：

- **函数延迟调用**：初始化时只建立引用，函数体里的读取等到被调用时才发生
- **活绑定（live binding）**：`export let bValue` 被导入方拿到的是"实时引用"——导出方改了值，所有导入方立刻看到新值

死穴在哪？**模块初始化时直接读取对方的顶层值**：

```typescript
// lib-a.ts 顶层
import { bValue } from "./lib-b.ts";
export const bad = bValue.toUpperCase();  // 💥 TDZ：lib-b 还没初始化完，bValue 是 undefined
```

规避口诀：**初始化时只建引用，读取推迟到函数调用**。

### 4. ESM vs CJS：判定规则与互操作

| | ESM | CJS |
|---|---|---|
| 语法 | `import` / `export` | `require` / `module.exports` |
| 加载 | 异步、静态（可 tree-shaking） | 同步、动态 |
| 顶层 await | ✅ | ❌ |
| 判定 | package.json `type: module` / `.mjs` | 默认 / `.cjs` |

互操作：

```typescript
// ESM → CJS：createRequire
const require = createRequire(import.meta.url);
const legacy = require("./legacy.cjs");

// CJS → ESM：只能用动态 import()（返回 Promise）
const mod = await import("./lib-a.ts");
```

**本模块 package.json 声明了 `"type": "module"`，所有 .ts 按 ESM 解析**——这是各章 code.ts 能直跑的地基。

---

## 跟 Agent 的关系 — 连接到 Claude Code

Claude Code 是一个庞大的 TS 工程：成百上千个模块，每个都是清晰的 ESM 单元：

```
claude-code/
├── src/
│   ├── agent/       # Agent 循环逻辑
│   ├── tools/       # 每个工具一个模块（Read/Write/Bash...）
│   ├── mcp/         # MCP 协议实现
│   └── ...
```

- **模块边界 = 职责边界**：一个模块一个职责，改工具逻辑不用碰 Agent 循环
- **模块缓存**让共享状态（配置、客户端实例）天然单例
- **循环依赖的规避口诀**在大型 TS 工程里天天用——Claude Code 的模块图也遵循它

---

## 试一下

```bash
node s32_typescript/s05_es_module/code.ts

# 实验 1：在 lib-a.ts 顶层加一行 console.log("lib-a 被加载")，
#         重复 import 多少次都只打印一次 —— 模块缓存的铁证
# 实验 2：把 lib-a.ts 顶层改成 const bad = bValue.toUpperCase()，
#         跑 code.ts 看 TDZ 报错长什么样
# 实验 3：新建一个 .mjs 和一个 .cjs 文件，用 import.meta / module 观察两套系统的差异
```

---

## 小结 — 记住这个就够了

1. **export 亮出口，import 接依赖**——模块 = 独立作用域 + 显式边界
2. **模块按 URL 缓存**：import 一百次也只执行一次（模块级单例）
3. **循环依赖靠两条腿**：函数延迟调用 + 活绑定；死穴是初始化时读对方顶层值
4. **ESM/CJS 共存**：ESM 用 createRequire 调 CJS，CJS 用动态 import() 调 ESM
5. **相对导入带 .ts 扩展名**——本模块铁律
