# s32-04: async / await / Promise — 异步世界的三件套

[← 返回概览](../README.md) | [上一章：union / narrowing](../s03_union_narrowing/) | [下一章：ES Module](../s05_es_module/)

> 一句话核心思想：**Promise 是「未来的结果」的占位盒，async/await 让等待未来的代码读起来像现在。**

---

## 问题 — 为什么需要异步？

JS 是**单线程**的：一个线程跑所有代码。如果发网络请求时傻等（同步阻塞），整个程序就冻住了——浏览器页面卡死、服务器无法响应其他请求。

所以耗时操作（网络、文件、定时器）全部设计成**异步**：发出请求后先干别的，结果到了再通知你。异步本身的实现有三种写法，从丑到美：

```
回调地狱（老 JS）  →  Promise 链  →  async/await（现代写法）
```

---

## 原理 — 一句话 + 示意图

**Promise = 一个「未来的结果」的占位盒**，三种状态，只变一次：

```
        ┌────────────┐   resolve(值)   ┌──────────────┐
        │  pending   │ ──────────────→ │  fulfilled   │
        │  (进行中)  │                 │  (成功，有值) │
        └────────────┘                 └──────────────┘
               │
               │ reject(错误)
               ▼
        ┌──────────────┐
        │   rejected   │
        │ (失败，有错因) │
        └──────────────┘
```

`async` 函数永远返回 Promise；`await` 暂停函数执行、等 Promise 落定（settled）后带着结果继续。**await 之后的代码相当于包在 `.then` 回调里**——理解了这句，就理解了 async 函数的一切。

---

## 核心概念 — 分点讲解

### 1. 事件循环：微任务 vs 宏任务

在**主上下文**（比如 CommonJS 模块顶层）排队时，Node 的顺序是：

```
同步代码 → process.nextTick（Node 专属微任务）→ Promise 微任务 → 宏任务（setTimeout 等）
```

但有两个**官方文档写明的陷阱**：

1. 在 Promise 回调（async 续体）里调用 `nextTick`，回调会排在**微任务队列之后**
2. **ESM/TS 的模块顶层本身就是 promise 上下文**（模块加载器是异步的），所以 .ts 文件顶层排队的 nextTick 也排在 Promise 微任务之后——只有 CJS 顶层才是主上下文

code.ts 的演示 A（async 续体）/ B（.cjs 子进程）会把两种顺序都跑给你看。

两条永远不变的铁律：

1. **同步代码最先执行**
2. **微任务整体先于宏任务**（每个宏任务结束后，先清空微任务队列，再取下一个宏任务）

- 宏任务：setTimeout、setInterval、I/O 回调
- 微任务：Promise.then、process.nextTick
- `await` 后面的代码 = 微任务，所以"看起来同步"的代码其实是排队执行的
- 工程结论：**别依赖 nextTick 和 Promise 之间的相对顺序**

### 2. 串行 vs 并行

```typescript
// 串行：总耗时 = 各耗时之和
for (const id of ids) {
  names.push(await fetchUserName(id));   // 每个都要等前一个完成
}

// 并行：总耗时 ≈ 最慢的那个
const names = await Promise.all(ids.map(fetchUserName));
```

**互相独立的请求永远用 Promise.all**。这是性能的日常来源。

### 3. 错误处理三件套

```typescript
try { await risky(); } catch (e) { ... }        // await 的错误
promise.catch(e => ...)                          // 链式风格
await Promise.allSettled([...])                  // 永不 reject，逐个看结果
```

### 4. 顶层 await

本模块的 code.ts 结尾是 `await demo_all();`——**ESM 独有能力**：模块顶层可以直接 await，整个模块会等到它完成才算加载完。CJS 没有这个能力（下一章展开）。

---

## 跟 Agent 的关系 — 连接到 Claude Code

Agent 循环（s01_agent_loop）的核心动作就是异步调用：

```typescript
// Agent 每轮：调用 LLM API → 等响应 → 决定下一步
const response = await client.messages.create({ ... });   // 异步等待模型

// 一轮里需要并行调用多个工具时：
const results = await Promise.all(tools.map(t => t.execute(args)));
```

- `await client.messages.create(...)`——这就是 Claude Code 和模型对话的方式
- 工具并行调用 = Promise.all 的实战形态
- 模型流式输出（打字机效果）= async generator（`for await ... of`），s14 会看到类似结构

---

## 试一下

```bash
node s32_typescript/s04_async/code.ts

# 实验 1：把第 4 步的并行改成 20 个请求，看串行/并行差距
# 实验 2：把第 3 步的 setTimeout 延迟改成 100ms，观察输出顺序是否变化
# 实验 3：写一个 async 函数，里面 await 两次独立的 fakeFetch，改成 Promise.all 再跑
```

---

## 小结 — 记住这个就够了

1. **Promise 三态只变一次**：pending → fulfilled（有值）/ rejected（有错因）
2. **async/await 是 Promise 的语法糖**：await 之后 = .then 回调
3. **微任务先于宏任务**：await 后的代码是微任务
4. **独立请求用 Promise.all 并行**；「一个都不能少」用 allSettled
