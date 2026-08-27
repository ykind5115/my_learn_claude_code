# s32-00: 心智模型 — 动手需求（热身）

[← 返回总索引](../PRACTICE.md) | [本章教程](./README.md)

> 一句话本章核心思想：**TypeScript = 给 JavaScript 数据贴标签。贴标签是编译期的事，运行时标签全部被撕掉。**

这一章不写代码的章，但心智模型必须"动手"才能建立——热身题就是用你的话把它写出来。

**只给需求和提示，不给完整代码**——卡住了回到主项目提问。

## 使用说明
- 前置技能：无（会基础 JavaScript 即可）
- 自测方式：`cd s32_typescript && npm run typecheck` 零报错
- 解答文件建议放本章目录内，命名 `practice_warmup.ts`

## 热身 1：给 JS 代码贴标签（⭐ 入门 | 核心技能：编译期 vs 运行时心智模型）

### 背景
s00 的三句话地图——"类型=标签 / 编译器=质检员 / 擦除=撕标签"——只有亲手贴一遍标签、亲手回答"哪个检查是编译期的、哪个是运行时的"，地图才会长在脑子里。

### 要做什么（验收标准）
1. 下面这段**无类型 JS**，加上你认为合适的 TypeScript 类型标注：

```javascript
function totalPrice(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}

function formatUser(user) {
  return user.name + "（" + user.age + "岁）";
}

const cart = [
  { name: "键盘", price: 199, qty: 2 },
  { name: "鼠标", price: 89, qty: 1 },
];
```

2. 在代码里用注释回答 3 个问题：
   - 每个标注的标签，**编译期**会检查什么？
   - 如果 `totalPrice(cart)` 里有一个 `item.price` 是字符串 `"199"`，类型系统能拦住吗？为什么？（提示：运行时会发生什么）
   - 用一行 `// @ts-expect-error` 故意写一个类型错误，然后跑 typecheck，观察 tsc 的反应；再跑 node 直跑，观察运行时是否照常执行——把观察到的差异写在注释里。

3. typecheck 零报错（@ts-expect-error 那处除外，它是"预期内的错误"）。

### 技术要点
- 标注 vs 推断：`const name: string` 是标注，`const age = 18` 是推断
- `any` 是逃课生：`as any` 能骗过质检员，但骗不过运行时（`cart as any` 之后访问不存在的字段，编译期放行、运行时崩）
- `@ts-expect-error` = "下一行有类型错误（我故意的）"，typecheck 时跳过、node 直跑照常执行——**这一行浓缩了本章全部思想**

### 超纲提示
🔧 给 `totalPrice` 的参数标注成 `{ name: string; price: number; qty: number }[]`——数组 + 对象形状的标注写法，是下一章（s02 interface）的正式内容，先用起来。

### 自测方法
```bash
cd s32_typescript && npm run typecheck   # 应该零报错（@ts-expect-error 处除外）
node s32_typescript/s00_mental_model/practice_warmup.ts   # node 直跑，验证"标签被撕掉"
# 实验：把 @ts-expect-error 那一行的注释删掉，再 typecheck，看报错长什么样
```

## 做完之后
- 自查：你能不能用一句话向别人解释"为什么 node 能直接跑 .ts"？
- 想继续深挖：翻开 s32 模块根目录的 README，看"学习路线图"——下一站 s01，标签贴法正式开始
