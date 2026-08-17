# s32-15: 类型体操 — 把类型系统当编程语言玩

[← 返回概览](../README.md) | [上一章：Compiler API](../s14_compiler_api/) | [下一章：综合实战 HTTP API](../s16_capstone/)

> 一句话核心思想：**TS 的类型系统是图灵完备的——有条件、递归、循环、模式匹配，所以「用类型解题」成为可能。**

---

## 问题 — 类型体操是什么？有什么用？

先看一段"魔法"：

```typescript
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};
```

这是**递归**。再看：

```typescript
type Add<A extends number, B extends number> = [...BuildTuple<A>, ...BuildTuple<B>]["length"];
```

这是**用元组长度做加法**。类型体操 = 用条件类型、递归、映射、infer 在类型层解编程题。

**实际价值排序**（诚实版）：

1. **读懂/写出高质量库的类型**——zod、trpc 这些库的核心就是类型体操，学完本章读 .d.ts 不再怕
2. **给团队写更强的类型约束**——把更多错误提前到编译期
3. 面试题（最不重要）

它是锦上添花，**不是基础刚需**——学不会不影响你写应用。

---

## 原理 — 一句话 + 示意图

**把「类型」当数据、「条件类型」当 if、「递归」当循环、「元组」当数组、「@ts-expect-error」当断言——在编译期跑一个程序。**

```
type BuildTuple<N, Acc = []> = Acc["length"] extends N ? Acc : BuildTuple<N, [...Acc, unknown]>
      │                │                   │
      │                │                   └─ 递归出口：长度到了就返回
      │                └─ 每次递归往元组塞一个元素
      └─ 参数：目标长度 + 累加器

BuildTuple<3> → [unknown, unknown, unknown]
其 length 类型 = 3
```

---

## 核心概念 — 分点讲解

### 1. 递归条件类型

```typescript
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};
```

模板：`X extends 条件 ? 递归 : 出口`。注意 TS 对递归深度有限制（几百层），`BuildTuple<1000>` 会爆。

### 2. 元组 = 数字的编码

类型系统里没有直接的"数字计算"，但元组有 `length`：

```typescript
type Add<A, B> = [...BuildTuple<A>, ...BuildTuple<B>]["length"];
// Add<3, 4> = 7
```

**数字 → 元组 → 拼接 → 长度**，这是类型体操最经典的编码技巧。

### 3. 模板字面量类型：字符串解析

```typescript
type EventName<T extends string> = `${T}Changed`;
EventName<"volume"> = "volumeChanged"   // 类型系统拼字符串

type Greeting = `Hello, ${string}`;      // 通配符匹配
```

配合 infer 还能**反向解析**：从 `"Hello, 小明"` 提取出 `小明`。路由、事件名、SQL 字符串的类型安全都靠它。

### 4. Equal 断言 + @ts-expect-error = 类型层测试

```typescript
type Equal<X, Y> =
  (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;

const ok: Equal<Add<1, 2>, 3> = true;        // ✅ 断言成立
// @ts-expect-error 断言失败——这行必须报错
const bad: Equal<Add<1, 2>, 4> = true;
```

**跑 typecheck = 跑类型层的单元测试**。本章每个结论都这样验证。

### 5. 体操的边界

- 递归深度有限（几百层）
- 每个体操都是编译器要跑的程序——多了编译变慢
- 可读性换收益要划算：库的核心类型值得雕琢，业务代码简单清晰最值钱

---

## 跟 Agent 的关系 — 连接到 Claude Code

Claude Code 及其生态（zod 校验、trpc 类型路由、SDK 泛型）的 .d.ts 里全是本章的构造。学完这一章：

- 读 SDK 的类型定义不再像读天书
- 理解 `Equal`/`Expect` 这类工具类型的断言思路
- 有能力给自己的 Agent 工具写更强的参数类型约束（工具 schema 的类型安全）

---

## 试一下

```bash
node s32_typescript/s15_type_gymnastics/code.ts
cd s32_typescript && npm run typecheck   # 体操的验证器在编译期

# 实验 1：手写 Sub<A, B>（减法，提示：元组切片）
# 实验 2：手写 DeepRequired<T>（把 DeepReadonly 的 readonly 换成 -?）
# 实验 3：把第 2 步的 @ts-expect-error 删掉，跑 typecheck 看报错
```

---

## 小结 — 记住这个就够了

1. **类型体操 = 类型层编程**：条件/递归/映射/infer 都是工具
2. **元组长度 = 数字**，拼元组 = 加法——最经典的编码技巧
3. **模板字面量类型**能拼也能反向解析字符串
4. **@ts-expect-error + typecheck = 类型层的测试框架**
5. **体操是奢侈品不是刚需**：读得懂 .d.ts 就是最大的收获
