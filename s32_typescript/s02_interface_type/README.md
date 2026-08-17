# s32-02: interface / type — 给对象形状贴标签

[← 返回概览](../README.md) | [上一章：基础语法](../s01_ts_basics/) | [下一章：union / narrowing](../s03_union_narrowing/)

> 一句话核心思想：**interface 是「形状契约」，type 是「标签的别名」——两者 90% 场景通用，差异只在扩展方式。**

---

## 问题 — 为什么需要描述对象形状？

s01 里的类型都是"单值标签"（string、number）。但真实代码的主角是**对象**：

```typescript
function createOrder(user: { name: string; age: number; email?: string }, items: { price: number }[]): ... {
  // 函数签名长得可怕，而且每处调用都要重复一遍这个形状
}
```

当"用户的形状"在 10 个文件里出现时，你就需要**给这个形状起个名字**——这就是 interface / type 的由来。

---

## 原理 — 一句话 + 示意图

**interface = 画一张"对象形状图纸"，tsc 拿图纸比对每个对象。**

```
interface User {          ┌──────────────────┐
  name: string;           │  User 形状图纸    │
  age: number;            │  name   → string │
  email?: string;         │  age    → number │
}                         │  email? → string │
                          └──────────────────┘
const u: User = { ... } ──→ 按图纸逐字段比对
                            缺 name？ ❌  多一个字段？ ❌（字面量才查）
                            类型不对？ ❌  全对？  ✅ 放行
```

---

## 核心概念 — 分点讲解

### 1. 可选属性 / readonly / 索引签名 / 函数类型

```typescript
interface Config {
  retry?: number;                    // 可选：可有可无
  readonly apiKey: string;           // 只读：创建后不可改（编译期封条）
  [key: string]: string | number;    // 索引签名：任意 key 都行
  onSuccess: (data: string) => void; // 函数类型：描述函数形状
}
```

- **可选属性**对应 JS 的"这个字段可能不存在"现实，避免到处写 `undefined` 检查
- **readonly** 是编译期约定——运行时该改还是能改（类型擦除后没人拦），但它把意图写成了契约
- **函数类型**让"回调"也纳入类型系统

### 2. type vs interface 差异对照表

| 能力 | interface | type |
|---|---|---|
| 描述对象形状 | ✅ | ✅ |
| extends 继承 | ✅ | ✅（交叉 `&`） |
| 联合 `\|` / 交叉 `&` | ❌ | ✅ |
| 映射类型 / 条件类型 | ❌ | ✅（s12 展开） |
| 声明合并（同名自动合并） | ✅ | ❌ |
| 描述基本类型别名 | ❌ | ✅（`type Id = string \| number`） |

**现代实践（社区共识）**：
- 描述**对象形状**：默认 `interface`（可扩展、可声明合并，第三方类型打补丁方便）
- 需要**联合、映射、推导**：用 `type`
- 团队统一风格比争论哪个好更重要

### 3. 声明合并：interface 的独门绝技

```typescript
interface Player { name: string }
interface Player { score: number }   // 同名再声明 → 字段合并
const p: Player = { name: "A", score: 99 };  // 两个字段都要
```

最实用的场景：**给第三方库打类型补丁**——不改库代码，在自己的文件里同名声明一次，把库的类型扩展掉。这是真实工程里天天发生的事。

### 4. 结构化类型（鸭子类型）

```typescript
interface HasName { name: string }
const person = { name: "路人", age: 40, city: "北京" };
readName(person);  // ✅ 不用 extends，形状对得上就行
```

TS 的类型兼容看**形状**不看**身份**（和 Java/Go 的接口不同）。这带来一个思维转变：**接口是"需求清单"，不是"身份证"**——调用方需要什么，就声明什么形状。

---

## 跟 Agent 的关系 — 连接到 Claude Code

Claude Code 的 MCP（Model Context Protocol，s19 讲过）类型定义就是典型的接口设计：

```typescript
interface McpTool {
  name: string;
  description?: string;
  inputSchema: Record<string, unknown>;   // 工具的 JSON Schema
}
```

- Agent 调用工具前，靠这些接口校验参数形状——接口就是**协议**
- 第三方插件要扩展 Claude Code 的类型时，用的正是声明合并
- `Record<string, unknown>` 是内置泛型工具（s08 展开），本质是索引签名的语法糖

---

## 试一下

```bash
node s32_typescript/s02_interface_type/code.ts

# 实验 1：把第 2 步里 u3.id = "hacked" 的注释去掉，npm run typecheck 看报错
# 实验 2：自己写一个 interface，试试可选属性 + readonly + 函数类型三种能力
```

---

## 小结 — 记住这个就够了

1. **interface 画对象形状，type 起别名**——90% 场景通用
2. 联合/交叉/映射用 type；**声明合并是 interface 独有**（打补丁神器）
3. 可选属性 `?`、readonly、索引签名是形状的三件套
4. **TS 是结构化类型**：形状对得上就兼容，不需要登记身份
