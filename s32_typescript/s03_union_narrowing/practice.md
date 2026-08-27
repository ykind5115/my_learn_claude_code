# s32-03: union / narrowing — 动手需求

[← 返回总索引](../PRACTICE.md) | [本章教程](./README.md)

> 一句话本章核心思想：**union 表达「或」，narrowing 把「或」变回「具体」——TS 类型安全 90% 的日常就发生在这两步之间。**

学完本章，用下面这些需求把知识变成肌肉记忆。**只给需求和提示，不给完整代码**——卡住了回到主项目提问。

## 使用说明
- 前置技能：s01~s03（基础语法 + interface/type + union/narrowing）
- 自测方式：`node s32_typescript/s03_union_narrowing/practice_xxx.ts` 从仓库根直跑看输出；`cd s32_typescript && npm run typecheck` 零报错
- 解答文件建议放本章目录内，命名 `practice_<名字>.ts`

## 需求 1：命令分发器（简易计算器 CLI）（⭐ 入门 | 核心技能：判别联合 + switch 收窄 + never 穷尽）
- [ ] 完成

### 背景
「字符串输入 → 判别联合 → 分发处理」是 CLI / 协议解析的骨架。Agent 解析工具参数、HTTP 路由分发，底层都是这个模式。

### 要做什么（验收标准）
1. `node s32_typescript/s03_union_narrowing/practice_cli.ts add 3 5` 输出 `8`；支持 `add` / `sub` / `mul` / `div`。
2. `parseCommand(line: string)` 返回判别联合：`{ kind: "add" | "sub" | "mul" | "div"; a: number; b: number }` 或 `{ kind: "error"; message: string }`。
3. `handle` 用 `switch` 收窄 + `default` 里 `assertNever(r)` 穷尽检查。
4. **加第 5 种命令（如 `pow`）**，看 typecheck 如何逼你在 switch 里补分支。
5. 非法输入（`add x y`、`mod 1 2`、参数个数不对）→ `{ kind: "error" }`，友好提示，不崩溃。

### 技术要点
- 判别联合：每个成员带**字面量类型公共字段** `kind`——它就是"判别子"
- `switch (cmd.kind)` 时每个 case 自动收窄到对应成员（控制流分析跟着 switch 走）
- `never` + `assertNever(x: never): never`：default 分支里类型是 never 才算穷尽；加了新成员漏了分支 → 编译报错
- **解析与执行分离**：parse 负责"字符串 → 判别联合"，handle 负责分发——坏输入在 parse 层就变成 error 成员，handle 不用猜
- 判别字段记得写字面量类型：单独写 `{ kind: "add" }` 时 `kind` 会退化成 `string`（字符串拼接陷阱，`as const` 可救）
- 只用可擦除语法（别用 enum 表达 kind）

### 超纲提示
🔧 真正的 CLI 库 commander / yargs（s07 装依赖后可体验）——它们帮你做参数解析，但「判别联合 + 分发」的核心思想不变。

### 自测方法
```bash
node s32_typescript/s03_union_narrowing/practice_cli.ts add 3 5      # 8
node s32_typescript/s03_union_narrowing/practice_cli.ts div 10 4     # 2.5
node s32_typescript/s03_union_narrowing/practice_cli.ts mod 1 2      # 错误提示
node s32_typescript/s03_union_narrowing/practice_cli.ts add x 5      # 错误提示
cd s32_typescript && npm run typecheck
# 穷尽实验：注释掉 switch 里某个分支，或去掉 assertNever，typecheck 看报错
```

## 需求 2：表单校验器（⭐⭐ 组合 | 核心技能：unknown → 类型守卫 → 精确类型）
- [ ] 完成

### 背景
承接 s01 需求 3，这次用正规军武器——类型守卫 + 判别联合——做**可复用**的校验器。守卫是 TS 处理一切外部数据的标准姿势。

### 要做什么（验收标准）
1. `isUser(x: unknown): x is User`（User `{ id: string; name: string; age?: number; email?: string }`）和 `isOrder(x: unknown): x is Order`（Order `{ id: string; items: { name: string; price: number }[] }`）。
2. `parseJson(raw: string)` 返回判别联合 `{ ok: true; value: unknown } | { ok: false; error: string }`。
3. 演示守卫后用不着手动收窄：`isUser(raw)` 为 true 的分支里直接访问 `raw.name`。
4. 嵌套校验：Order 的 `items` 要逐项检查（每项是对象、有 name、price 是数字且 ≥ 0）。
5. 合法 / 非法 JSON / 形状不符三组数据，typecheck 零报错。

### 技术要点
- `x is T` 签名：函数返回 true 时 TS 相信你并把 x 收窄——「验证逻辑」和「类型系统」打通
- 守卫内部用 `typeof` / `in` 判断：`typeof x !== "object" || x === null` 先挡脏数据（typeof null 陷阱）；`"name" in x` 查字段
- 判别联合表达成功/失败：`{ ok: true; value } | { ok: false; error }`——比 throw 直白，调用方不用 try/catch
- 嵌套校验：数组先 `Array.isArray`，再逐项守卫（守卫可以互相调用：`items.every(isItem)`）
- 项目约定三件套：相对导入带 `.ts` 扩展名（守卫拆文件时）；文件路径一律 `import.meta.dirname`；只用可擦除语法

### 超纲提示
🔧 zod / valibot 这类运行时校验库就是守卫思想的工程化（s07 后可体验）——对比你的手写守卫，看看库帮你省了什么。

### 自测方法
```bash
node s32_typescript/s03_union_narrowing/practice_validator.ts
# 合法 User / 合法 Order / 非法 JSON / 缺字段 / items 里混进坏项——每组的输出要能看出守卫在哪一步拦截
cd s32_typescript && npm run typecheck
```

## 需求 3：图形面积/周长计算器（⭐⭐⭐ 挑战 | 核心技能：in 收窄 + 判别联合 + 穷尽）
- [ ] 完成

### 背景
README「试一下」实验 2 的升级版：加周长、加形状、加穷尽检查。做完这道，判别联合的三板斧（判别字段 / in / never）就全熟了。

### 要做什么（验收标准）
1. 定义 `type Shape = { kind: "circle"; radius: number } | { kind: "square"; side: number } | { kind: "triangle"; base: number; height: number }`。
2. `area(s: Shape): number` 和 `perimeter(s: Shape): number`——用 `in` 或 `kind` 收窄（triangle 的周长可以简化为「base + height + 斜边近似」，规则写清楚即可）。
3. 新增 `{ kind: "rect"; w: number; h: number }` 时，两处函数必须补分支——不加 `assertNever` 就 typecheck 不过（穷尽演示）。
4. `main` 输出全部形状的面积/周长表格（模板字符串排版）。
5. 跑通 + typecheck 零报错。

### 技术要点
- `in` 收窄：`if ("radius" in s)` 用属性存在性区分形状
- **判别字段 vs in 的取舍**：成员有统一 `kind` 字段时用 `switch (s.kind)` 更稳（不依赖属性名巧合）；`in` 适合没有判别子的场景
- `never` 穷尽：`default: return assertNever(s)`——新增形状漏分支 → 编译报错，`area` / `perimeter` 两处都要补
- 形状的种类可以用**字面量联合类型**表达（可擦除语法，别用 enum）

### 超纲提示
🔧 `as const` + `typeof` 组合定义形状种类枚举的替代写法（s01 讲过）：`const ShapeKind = { Circle: "circle", ... } as const; type ShapeKind = (typeof ShapeKind)[keyof typeof ShapeKind]`——需要遍历形状类型时比手写字面量联合好用。

### 自测方法
```bash
node s32_typescript/s03_union_narrowing/practice_shapes.ts   # 输出三种形状的面积/周长表格
cd s32_typescript && npm run typecheck
# 穷尽实验：给 Shape 加 rect 成员，typecheck 看 area/perimeter 两处同时变红
```

## 做完之后
- 自查：你用了本章哪些概念？（union / typeof 收窄 / in 收窄 / 判别字段 / 判别联合 / 类型守卫 x is T / never 穷尽检查）
- 想继续深挖：回看本章 README 的「跟 Agent 的关系」——`ToolResult` 的成功/失败判别联合，试着给它的 `errorType` 加一种新错误，看穷尽检查怎么逼你补分支
