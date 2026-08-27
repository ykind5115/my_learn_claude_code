# s32-01: TypeScript 基础语法 — 给数据贴上第一个标签

[← 返回概览](../README.md) | [下一章：interface / type](../s02_interface_type/)

> 一句话核心思想：**类型标注不改变代码的运行，只改变机器检查代码的能力。**

---

## 问题 — 为什么需要类型标注？

先看一段纯 JavaScript：

```javascript
function totalPrice(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}

totalPrice([{ price: 10 }, { price: 20 }]);  // 30 ✅
totalPrice("不是数组");                       // 💥 运行时崩溃
totalPrice([{ price: "10" }, { price: 20 }]); // "01020" ❓ 静默错误！
```

三种情况，JS 全部接受，其中两种是错的。**错得越晚，修起来越贵**——用户都点下单了才崩溃，和写代码时就看到红线，成本差一万倍。

TypeScript 的类型标注，就是让错误**提前到编译期**被发现。

---

## 原理 — 一句话 + 示意图

**类型标注 = 给数据贴标签，质检员（tsc）按标签检查"用法"是否匹配。**

```
你写的代码                       tsc 质检员                运行时
─────────────────────────────────────────────────────────────────────
const age: number = 18;   →   age 标签是 number    →   撕掉标签，跑 JS
age.toUpperCase();        →   ❌ number 没有         →   （永远到不了这）
                               toUpperCase 方法！
                               编译期拦下，报错
```

注意质检员的工作方式：**它检查的是"标签上写了什么"，而不是"值到底是什么"**。所以：

```typescript
// 你能骗过质检员（as any），但骗不过运行时
const age: any = 18;
age.toUpperCase();  // 编译期放行，运行时崩溃 💥
```

---

## 核心概念 — 分点讲解

### 1. 类型标注 vs 类型推断

```typescript
const name: string = "小明";  // 标注：自己写标签
const age = 18;               // 推断：TS 从值猜出 number
```

TS 的类型推断很强，大多数简单变量不用写。**实践准则：能推断的不写；函数参数、对象形状（跨模块共享的结构）显式写**——它们是"契约"，写出来是为了让调用方一眼看懂。

### 2. any / unknown / never 三兄弟

| 类型 | 含义 | 编译期 | 典型场景 |
|---|---|---|---|
| `any` | 完全关闭检查 | 什么都放行 | 旧代码迁移、赶时间（不推荐） |
| `unknown` | 不知道是什么，用前必须确认 | 必须收窄才能用 | API 响应、用户输入、JSON.parse |
| `never` | 永远不会出现 | 任何值都赋不进去 | 穷尽检查的兜底（s03 展开） |

**`any` 是逃课生，`unknown` 是转学生**——转学生进教室前要先"验明身份"（narrowing）。

### 3. 数组 / 元组 / as const

```typescript
const nums: number[] = [1, 2, 3];            // 数组：元素同类型
const pair: [string, number] = ["age", 18];  // 元组：长度+每位置类型都固定
const config = { retry: 3 } as const;        // 字面量类型 + 只读
```

- `as const` 之后 `retry` 的类型是字面量 `3`（不是 `number`），且属性只读
- 元组和 `as const` 是类型体操（s15）的基本材料

### 4. enum：为什么本模块的 code.ts 看不到它

```typescript
enum Color { Red, Green }          // ❌ 不可擦除语法
const Color = { Red: 0, Green: 1 } as const;  // ✅ 现代替代
type Color = (typeof Color)[keyof typeof Color];
```

`enum` 编译后会**真的生成 JS 代码**（不像其他类型标签那样被撕掉），所以 node 直跑 .ts 会报错。社区主流已经转向 `as const` 对象 + 联合类型——好处完全相同，还兼容 type stripping。**本模块所有 node 直跑的代码只用可擦除语法**，tsconfig 里的 `erasableSyntaxOnly: true` 把这变成了编译期强制。

### 5. @ts-expect-error：编译器检查能力的"对照实验"

```typescript
// @ts-expect-error 下一行有类型错误（我故意的）
const wrong: number = "这不是数字";
```

- `npm run typecheck` 时：tsc 知道这里有"预期内的错误"，跳过不报
- `node code.ts` 时：照常运行，`wrong` 的值就是那个字符串

**这一行代码浓缩了本章全部思想：类型错误只存在于编译期，运行时没有标签，也没有检查。**

---

## 跟 Agent 的关系 — 连接到 Claude Code

Claude Code 的源码里，处理 API 响应的典型代码：

```typescript
const data: unknown = await response.json();
if (typeof data === "object" && data !== null && "content" in data) {
  // 收窄后才能安全使用 data.content
}
```

- 外部数据进来一律 `unknown` → 层层收窄 → 变成精确类型。这就是本章第 4 步的实战形态
- 工具返回值（s02_tool_use 讲过的 ToolResult）也是同样套路：不知道工具会返回什么，先 `unknown`，验证后再用

---

## 试一下

```bash
# 1. 跑演示代码
node s32_typescript/s01_ts_basics/code.ts

# 2. 质检员上班：类型检查（能看到 @ts-expect-error 如何被处理）
cd s32_typescript && npm run typecheck && cd ..

# 3. 实验：把第 5 步的 @ts-expect-error 注释删掉，再跑 typecheck，看报错长什么样
```

---

## 小结 — 记住这个就够了

1. **标注 vs 推断**：能推断的不写，契约型的地方（参数/对象形状）显式写
2. **any 逃课，unknown 转学**：外部数据一律 unknown，收窄后再用
3. **类型错误只挡编译期**：node 直跑 .ts 就是证据——标签在运行前全被撕掉
4. **enum 用 as const 替代**：本模块代码全部可擦除，node 零配置直跑



## 注释：
1. ts只静态页面的标签检查；对于定义的变量的类型，要在js运行时才赋值的话，ts是检查不出来的。