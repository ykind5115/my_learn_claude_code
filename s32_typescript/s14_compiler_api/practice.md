# s32-14: TypeScript Compiler API — 动手需求

[← 返回总索引](../PRACTICE.md) | [本章教程](./README.md)

> 一句话本章核心思想：**tsc 是一个库，不是黑盒——用 `createSourceFile` 把源码变成 AST，遍历它，你就拥有了写代码分析工具的能力。**

学完本章，用下面这些需求把知识变成肌肉记忆。**只给需求和提示，不给完整代码**——卡住了回到主项目提问。

## 使用说明
- 前置技能：s01~s14（类型守卫 s03、enum s01、文件读取 s11）
- 自测方式：`cd s32_typescript && npm install`（需要 typescript 包）之后 **node 直跑**；顺手 `npm run typecheck` 保持零报错
- 解答文件建议放本章目录内，命名 `practice_<名字>.ts`（如 `practice_analyze.ts`）
- 约定：相对导入带 `.ts` 扩展名；脚本内部的文件路径用 `import.meta.dirname` 拼（s11 的铁律）；命令行参数（要分析哪个文件）是用户从终端给的，按参数原样使用即可；类型导入用 `import type`（tsconfig 开了 `verbatimModuleSyntax`）

## 需求 1：代码统计器（⭐ 入门 | 核心技能：createSourceFile + forEachChild + 类型守卫）
- [ ] 完成

### 背景
README 实验 1 的完整版——你写的第一个"分析代码的工具"。从"读代码"到"让程序读代码"，这一步跨过去，后面所有工具（扫描器、文档生成器）都只是换个统计目标。

### 要做什么（验收标准）
`practice_analyze.ts` 接收一个 .ts 文件路径（命令行参数，缺省指向 `s01_ts_basics/code.ts`），输出统计表：
- 总行数（源码字符串按 `\n` 切）
- 函数声明数（`FunctionDeclaration`）和箭头函数数（`ArrowFunction`）
- interface 数
- class 数
- 导出数（`export function` / `export const` / `export default` 都算）
- 用对齐文本或表格打印

换一个文件跑（比如 `s06_node/code.ts`），数字跟着变——证明你的工具真的"看懂"了代码。

### 技术要点
- `ts.createSourceFile("demo.ts", code, ts.ScriptTarget.Latest, true)`——四个参数各是什么（README「核心概念 1」）
- `forEachChild` **不会自动深挖**——回调里要对每个子节点再调用同一遍历函数，递归得自己写（README「核心概念 2」的三步曲）
- 类型守卫收窄：`ts.isFunctionDeclaration(node)` 之后才能安全访问 `node.name`；箭头函数是 `ts.isArrowFunction`
- `ts.SyntaxKind[node.kind]` 打印节点种类对照表（它是库里的编译产物 enum，node 里随便用）
- 判断"是否导出"：看 `node.modifiers` 里有没有 `ts.SyntaxKind.ExportKeyword`——这是本需求最绕的地方，想清楚"导出"在 AST 里长什么样
- 读文件用 `node:fs/promises` 的 `readFile`（s11）

### 超纲提示
🔧 把递归遍历封装成通用 `walk(node, cb)` 工具，三个需求共用：`walk(sourceFile, (n) => { ... })`——这就是你第一个 Compiler API 脚手架。

### 自测方法
```bash
cd s32_typescript && node s14_compiler_api/practice_analyze.ts s01_ts_basics/code.ts
# 换一个文件再跑：node s14_compiler_api/practice_analyze.ts s06_node/code.ts
# 验收点：输出表格、数字合理（打开文件人工数几个数核对）
```

## 需求 2：TODO/FIXME 扫描器（⭐⭐ 组合 | 核心技能：AST 遍历 + 注释提取）
- [ ] 完成

### 背景
真实团队工具第一号：grep 只能匹配文本，AST 扫描器"懂"代码——注释在语法树里有自己的位置，还能拿到精确行号。写完这个，你就能在团队里说"我写了个 lint 工具"。

### 要做什么（验收标准）
`practice_scan_todo.ts` 遍历一个 .ts 文件，提取所有注释，匹配 `/TODO|FIXME|HACK/`，输出 `文件:行号:内容`：

```
s01_ts_basics/code.ts:12: TODO 这里要处理边界
```

- 先做单文件模式（命令行参数给路径）
- 至少覆盖两种注释：`//` 行注释（含 `///`）和 `/* */` 块注释 / JSDoc
- 匹配大小写不敏感

### 技术要点
- 注释在 AST 里的两种存在方式：JSDoc 是独立节点（`ts.isJSDoc(node)`，`node.getText()` 可拿全文）；普通 `//` 和 `/* */` **不是节点**，要用 `ts.getLeadingCommentRanges(text, pos)` / `getTrailingCommentRanges` 的思路——返回 `{pos, end, kind}[]`，kind 区分 `SingleLineCommentTrivia` 和 `MultiLineCommentTrivia`
- 遍历时对每个节点查它的 leading 注释即可覆盖绝大多数场景；注释内容用 `text.slice(range.pos, range.end)`（`text = sourceFile.getFullText()`）
- 行号：`sourceFile.getLineAndCharacterOfPosition(range.pos).line + 1`（1 基行号）
- 匹配用 `/\b(TODO|FIXME|HACK)\b/i`——`\b` 词边界帮你过滤"NOTODO"这类干扰

### 超纲提示
🔧 配合 s11 的 `readdir` 递归扫整个目录：`node practice_scan_todo.ts --dir s32_typescript`（或扫 s01~s05），输出全部文件的所有 TODO——这就是一个能跑的团队工具了。

### 自测方法
```bash
cd s32_typescript && node s14_compiler_api/practice_scan_todo.ts s01_ts_basics/code.ts
# 验收：先在 s01 的 code.ts 里临时加一行 "// TODO: 压测一下"，扫描应输出 文件:行号:内容 且行号准确
# 验证完把临时那行删掉，别污染教学文件
```

## 需求 3：模块导出清单生成器（⭐⭐⭐ 挑战 | 核心技能：AST 分析 + 生成文档）
- [ ] 完成

### 背景
README 说学完本章"从使用者变成工具制造者"——自动生成 API 文档是这类工具的代表作。你写的不再是"读代码"，而是"替人写文档"。

### 要做什么（验收标准）
`practice_gen_docs.ts` 解析一个多导出的模块文件（如 `s02_interface_type/code.ts` 或根目录的 `utils.ts`），生成 markdown 文档：
- 收集所有导出，按种类分组：
  - 函数：函数名 + 参数列表（`参数名: 类型`）+ 返回类型
  - interface / type：名字 + 成员列表
  - 默认导出：单独标记
- 输出 markdown：章节标题 + 每组的表格（名字 / 签名）+ 签名代码块
- 支持输出到文件：`--out docs.md`（缺省打印到 stdout）——写文件路径用 `import.meta.dirname` 拼，别依赖 cwd

### 技术要点
- 节点取文本三兄弟：`node.getText()`（整段源码）、`node.name?.getText()`（名字）、`param.type?.getText()`（类型）——类型是 `TypeNode`，`getText()` 直接吐出源码文本，这就是"签名准确性"的来源
- `FunctionDeclaration`：`node.parameters`（每个是 `ParameterDeclaration`，有 `.name` 和 `.type?`）、`node.type`（返回类型）、`node.questionToken`（可选参数 `?`）
- `InterfaceDeclaration`：`node.members` 遍历，取每个成员的 `name` + `type` 文本
- 判断"是否导出"：`node.modifiers` 里找 `ExportKeyword`（和需求 1 同一招）；`export default` 单独识别
- 按种类分组 = 一个 `Record<种类, item[]>` 累加器
- 写文件用 `node:fs/promises` 的 `writeFile`（s11 前瞻；或者先 console.log 再在 shell 里 `> docs.md` 重定向）

### 超纲提示
🔧 递归收集**跨文件导出**：从入口文件出发，顺着 `import ... from "./xxx.ts"` 把相关文件的导出也收进来（import/export 链）——你离自动文档工具（typedoc 的迷你版）只差这一步。

### 自测方法
```bash
cd s32_typescript && node s14_compiler_api/practice_gen_docs.ts s02_interface_type/code.ts
# 或输出到文件：node s14_compiler_api/practice_gen_docs.ts utils.ts --out s14_compiler_api/api-docs.md
# 验收：肉眼核对生成的签名与源码一致；每个导出都出现、没有漏
```

## 做完之后
- 自查：你用了本章哪些概念？——createSourceFile / 递归遍历（forEachChild）/ 类型守卫 / SyntaxKind / 注释节点与 commentRanges / getText 提取签名
- 想继续深挖：回看本章 README 的「跟 Agent 的关系」，选一个点展开——比如把扫描器接到"提交前自动扫 TODO"的脚本上，做你自己的小 lint 工具
