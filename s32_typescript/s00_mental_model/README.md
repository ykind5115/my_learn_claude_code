# s32-00: 心智模型 — 类型是标签，编译器是质检员

[← 返回概览](../README.md) | [下一章：TypeScript 基础语法](../s01_ts_basics/)

> 一句话核心思想：**TypeScript = 给 JavaScript 数据贴标签。贴标签是编译期的事，运行时标签全部被撕掉。**

---

## 问题 — 为什么需要 TypeScript？

JavaScript 是动态类型语言：

```javascript
function add(a, b) {
  return a + b;
}

add(1, 2);        // 3 ✅
add("1", "2");    // "12" ❓ 字符串拼接，不是你想要的
add({}, null);    // "[object Object]null" 💥 运行时才爆炸
```

同一个函数，传什么它都"努力"执行。小项目无所谓，**几万行的项目里，一个拼错的属性名、一次传错的参数类型，要到用户点下按钮的那一刻才爆炸**。

TypeScript 的做法：**在代码运行之前，先给所有数据贴上类型标签，让机器帮我们检查一遍。**

---

## 原理 — 三句话建立地图

```
① 类型 = 标签        const name: string = "小明";
                      ↑ 这个标签说：name 永远是个字符串

② 编译器 = 质检员    tsc 在生产线上检查：
                      标签和实际数据对不上 → 当场拦下，报错
                      标签齐全 → 放行

③ 擦除 = 撕标签      检查通过后，标签被全部撕掉，
                      跑起来的还是纯 JavaScript。
```

**关键理解：类型只存在于编译期，运行时什么都没有。**

TypeScript 的官方术语叫 **type erasure（类型擦除）**：

```typescript
// 你写的（有标签）
function greet(name: string): string {
  return "你好，" + name;
}

// 运行时实际执行的（标签被撕掉）
function greet(name) {
  return "你好，" + name;
}
```

这解释了一个看似神奇的现象——**Node 22 能直接运行 .ts 文件**：

```
node code.ts   ← Node 内部把类型标签撕掉，剩下的就是普通 JS
```

本模块全部教学代码都可以 `node s32_typescript/sXX/code.ts` 直接跑，不需要编译步骤。**"撕标签"就是 node 直跑 .ts 的秘密。**

---

## 核心概念 — 地图上的三个地标

### 地标 1：编译期 vs 运行时

| | 编译期（写代码/检查时） | 运行时（代码跑起来） |
|---|---|---|
| 谁在工作 | tsc / 编辑器 | Node / 浏览器 |
| 类型在不在 | ✅ 在 | ❌ 被擦除 |
| 错误怎么出现 | 红波浪线、编译报错 | 抛异常、行为诡异 |

**类型系统是编译期的"静态检查"，不是运行时的"动态保险"。** 类型标注得再全，运行时该崩还是崩（比如访问不存在的文件、连接不上的服务器）——那些是运行时错误，类型系统管不着。

### 地标 2：类型检查 ≠ 类型转换

```typescript
const age: number = 18;
(age as any).split(".");  // 编译期：你说 any，好，放行
                          // 运行时：18.split 不存在 → 崩溃 💥
```

`as` 只是"告诉质检员别查这里"，**不会在运行时把 18 变成字符串**。

### 地标 3：本模块的学习地图

```
     编译期（标签的世界）                运行时（撕掉标签的世界）
┌─────────────────────────────┐  ┌─────────────────────────────┐
│ s01 基础语法      s02 interface │  │ s04 async       s05 ES Module │
│ s03 union/narrow  s08 泛型     │→ │ s06 Node.js      s07 npm/pnpm  │
│ s09 class         s10 错误处理  │  │ s11 文件系统/subprocess       │
│ s12 高级类型      s13 装饰器    │  │ s16 实战: HTTP API 服务器     │
│ s14 Compiler API  s15 类型体操  │  │                             │
└─────────────────────────────┘  └─────────────────────────────┘
        ↓ tsc 检查通过，撕掉标签 ↓
```

学习顺序建议：**先 s01~s03 打好标签基础 → 再 s04~s07 搞懂运行时 → 最后按需深入类型高级玩法**。

---

## 跟 Agent 的关系 — 为什么学 TypeScript 对你有用？

Claude Code 本身就是用 TypeScript 写的。当你读到它的源码：

```typescript
async function* generateAssistantMessage(
  query: Query,
  options: Options,
): AsyncGenerator<APIAssistantMessage, void> { ... }
```

如果没有类型地图，这些标注像天书。有了地图你就知道：

- `Query`、`Options` 是**接口标签**——描述这个参数长什么样（s02）
- `AsyncGenerator<...>` 是**泛型标签**——描述这个函数的返回流（s04/s08）
- Agent 每轮循环里"工具返回值的 unknown → narrowing 检查"（s03），正是 Claude Code 处理 API 响应时的日常操作

**读完本模块，你再看 Claude Code 源码就不慌了。** 这是学这门课最直接的红利。

---

## 小结 — 记住这个就够了

1. **类型 = 标签**，只存在于编译期，运行时被擦除
2. **tsc = 质检员**，把错误拦截在运行之前
3. **node 直跑 .ts = 撕掉标签的纯 JS**，这是本模块零配置的根基
4. TypeScript 不改变运行时行为——**类型是给人和工具看的，不是给机器看的**
