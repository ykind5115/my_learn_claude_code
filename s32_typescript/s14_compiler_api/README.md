# s32-14: TypeScript Compiler API — 用 TypeScript 解析 TypeScript

[← 返回概览](../README.md) | [上一章：Decorator](../s13_decorator/) | [下一章：类型体操](../s15_type_gymnastics/)

> 一句话核心思想：**tsc 是一个库，不是黑盒——用 `createSourceFile` 把源码变成 AST，遍历它，你就拥有了写代码分析工具的能力。**

---

## 问题 — 工具怎么「看懂」代码？

编辑器怎么知道你点的方法定义在哪？ESLint 怎么发现未使用的变量？Prettier 怎么排版？OpenAPI 生成器怎么从接口生成类型？

答案都是同一件事：**把源码字符串解析成 AST（抽象语法树），然后在树上做文章。**

TypeScript 官方把这个能力开放成了库——**Compiler API**。它就是你天天用的 `tsc` 背后的引擎。

---

## 原理 — 一句话 + 示意图

**源码 → createSourceFile → AST（树形结构）→ 遍历节点做分析 / 转换 → 打印回代码。**

```
"function greet(u: User): string {...}"
        │ createSourceFile
        ▼
SourceFile
 └─ FunctionDeclaration "greet"
     ├─ Parameter "u: User"
     ├─ ReturnType "string"
     └─ Block
         └─ ReturnStatement ...
        │ 遍历（forEachChild / 类型守卫过滤）
        ▼
提取签名 / 找问题 / 改写代码 / 生成文档
```

---

## 核心概念 — 分点讲解

### 1. 解析：createSourceFile

```typescript
const sourceFile = ts.createSourceFile(
  "demo.ts",                  // 虚拟文件名（报错定位用）
  sampleCode,                 // 源码字符串
  ts.ScriptTarget.Latest,     // 语法版本
  true,                       // 是否记录父节点
);
```

### 2. 遍历：forEachChild 递归 + 类型守卫

```typescript
const collect = (node: ts.Node): void => {
  if (ts.isFunctionDeclaration(node)) { ... }   // 类型守卫（s03！）
  ts.forEachChild(node, collect);               // 递归
};
```

`ts.SyntaxKind` 是节点种类的对照表——注意它是**库的编译产物 enum**，在 node 里随便用（s01 说的"库里的 enum"）。

### 3. 转换：transpileModule

```typescript
const js = ts.transpileModule(sampleCode, { compilerOptions: { target: ts.ScriptTarget.ES2022 } });
js.outputText;   // interface 消失，类型标注全被擦除
```

**s00 的「类型擦除」在这里看到了机器实现**——Node 直跑 .ts 的 type stripping 做的就是同一件事。

### 4. 生态地图：谁在用

| 工具 | 干什么 |
|---|---|
| ESLint TS 规则 | 遍历 AST 找问题模式 |
| Prettier | 解析 → 重排 → 打印 |
| VSCode TS 服务 | 实时 AST + 类型信息（跳转/重构/补全） |
| OpenAPI → 类型生成器 | 读 schema 写 AST 再打印 |

---

## 跟 Agent 的关系 — 连接到 Claude Code

- Claude Code 及其编辑器生态的**语言分析层**（代码跳转、符号搜索、诊断）全部建立在 Compiler API / LSP 之上
- Agent 的代码理解工具（读文件、找符号、分析依赖）常常先过一遍 AST
- 学完本章：你从「TS 的使用者」变成「TS 工具的制造者」

---

## 试一下

```bash
node s32_typescript/s14_compiler_api/code.ts

# 实验 1：把第 3 步改成统计「interface 数量」和「导出数量」
# 实验 2：写一个遍历器，找出所有「以 export 开头的声明」并打印名字
# 实验 3：用 transpileModule 编译你自己的一个 code.ts，对比输入输出
```

---

## 小结 — 记住这个就够了

1. **createSourceFile**：源码字符串 → AST
2. **遍历三步曲**：forEachChild 递归 + 类型守卫过滤 + 提取信息
3. **transpileModule**：亲眼看到类型擦除的机器实现
4. **AST 是工具生态的通用语言**——ESLint、Prettier、编辑器都活在它上面
