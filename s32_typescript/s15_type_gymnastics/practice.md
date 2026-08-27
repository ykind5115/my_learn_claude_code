# s32-15: 类型体操 — 动手需求

[← 返回总索引](../PRACTICE.md) | [本章教程](./README.md)

> 一句话本章核心思想：**TS 的类型系统是图灵完备的——有条件、递归、循环、模式匹配，所以「用类型解题」成为可能。**

学完本章，用下面这些需求把知识变成肌肉记忆。**只给需求和提示，不给完整代码**——卡住了回到主项目提问。

## 使用说明
- 前置技能：s01~s15（重点是 s12 高级类型：keyof、条件类型、infer、映射类型）
- 自测方式：`cd s32_typescript && npm run typecheck` —— **typecheck 通过 = 测试通过**。本章练习全部发生在编译期，跑 node 没有意义（类型都被擦除了）
- 解答文件建议放本章目录内，命名 `practice_<名字>.ts`（如 `practice_toolkit.ts`）
- 约定：练习文件只用**可擦除语法**（全是类型定义，天然满足）；`npm run typecheck` 会扫全仓所有 .ts，练习文件写好就自动纳入验证

## 需求 1：手写工具类型库（带测试）（⭐ 入门 | 核心技能：递归条件类型 + infer + 映射类型 + Equal 断言）
- [ ] 完成

### 背景
README 说的"类型层单元测试"——用 `Equal` + `@ts-expect-error` 给工具类型写测试。读完这一章，这些类型你已经见过，现在把它们从零写出来，然后像写单元测试一样验证每一个。

### 要做什么（验收标准）
写一个 `practice_toolkit.ts`，实现 4 个工具类型：
- `DeepReadonly<T>`：递归把对象每一层都变 readonly
- `DeepPartial<T>`：递归把对象每一层的属性都变可选
- `MyReturnType<T>`：提取函数类型的返回类型（用 infer）
- `MyAwaited<T>`：从 `Promise<X>` 提取 X，支持嵌套 Promise（`MyAwaited<Promise<Promise<number>>>` 应为 `number`）

每个类型配 **3~5 个 `Equal` 断言**（正确用例）+ **至少 1 个 `@ts-expect-error` 反例**（错误用例——断言失败的那行必须报错）。

### 技术要点
- 递归模板：`X extends 条件 ? 递归 : 出口`——每个工具类型先想清楚"递归什么"和"出口在哪"（README「核心概念 1」）
- `infer` 只出现在条件类型的分支里：`T extends (...args: never[]) => infer R ? R : never`
- `MyAwaited` 的出口：`T extends Promise<infer X> ? MyAwaited<X> : T`（递归剥壳，Flatten 的兄弟）
- 映射类型 `[K in keyof T]` 上加 `readonly` / `?` 修饰符就是 Deep 系列的骨架
- `Equal` 断言写法**照 README 抄**（「核心概念 4」那段），`const ok: Equal<...> = true` 就是一条测试
- `@ts-expect-error` = "下一行必须报错"——反例写错位置（不报错）时 tsc 会反过来骂你"多余的 @ts-expect-error"

### 超纲提示
🔧 注意递归深度限制（几百层就到顶）——测试用例别拿 100 层嵌套的对象去压；另外生产级 `DeepReadonly` 要特判数组/函数（`T[K] extends object` 会把数组也递归进去），可以试着给数组加个分支。

### 自测方法
```bash
cd s32_typescript && npm run typecheck
# 全绿 = 全过。验收点：故意把一个 Equal 断言改成错误答案，typecheck 必须报错（验证测试真的在工作）
```

## 需求 2：类型安全路由（⭐⭐ 组合 | 核心技能：模板字面量类型 + infer 解析）
- [ ] 完成

### 背景
README 说路由、SQL 字符串的类型安全都靠模板字面量类型——"从字符串里解析出类型"是它的招牌本领。写完这个，你就明白 trpc、zod 这类库是怎么把路由玩出花的。

### 要做什么（验收标准）
写 `practice_router.ts`，实现：
- `RouteParams<Path extends string>`：从路由字符串解析出参数对象类型
  - `RouteParams<"/user/:id">` → `{ id: string }`
  - `RouteParams<"/post/:pid/comment/:cid">` → `{ pid: string; cid: string }`
  - `RouteParams<"/todos">`（无参数）→ `{}`
- 反向拼接：``Route<Name extends string> = `/api/${Name}` ``，`Route<"users">` → `"/api/users"`
- 每个推导配 `Equal` 断言 + 反例 `@ts-expect-error`

### 技术要点
- 模板字面量类型能拼也能拆：`` `${string}:${infer Param}/${infer Rest}` ``——`infer` 一次抓一段
- 递归解析：`"/post/:pid/comment/:cid"` 拆掉 `:pid/` 之后，剩下的 `"comment/:cid"` 还要再拆——和需求 1 同一个递归模板
- 无参数时返回 `{}`：递归出口 + 兜底分支
- 对象拼装：`{ [P in Param]: string } & 递归结果` 或直接 `{ [P in Param | ...]: string }`——想清楚"多个参数怎么合并进一个对象"
- 注意：`:id` 和 `:pid` 这种多段参数，`infer Param` 抓到的是参数名本身（去掉冒号后），用它当 key

### 超纲提示
🔧 支持可选参数 `:id?`（解析成 `{ id?: string }`）——需要先判断段尾有没有 `?`，再决定 key 要不要加 `?` 修饰符。

### 自测方法
```bash
cd s32_typescript && npm run typecheck
# 全绿 = 全过。验收点：三个路径的 RouteParams 推导 + Route 拼接都有 Equal 断言覆盖
```

## 需求 3：类型层计算器（⭐⭐⭐ 挑战 | 核心技能：元组数字编码 + 递归）
- [ ] 完成

### 背景
README 说"元组长度 = 数字"，在类型层实现加减乘是类型体操最经典的挑战。做完这个，你的类型系统就真的"会算数"了。

### 要做什么（验收标准）
写 `practice_calculator.ts`，实现：
- `BuildTuple<N>`：造出长度为 N 的元组
- `Add<A, B>`：拼元组取 length
- `Sub<A, B>`：元组切片或递归递减（保证 A ≥ B）
- `Mul<A, B>`：递归加法（把 B 累加 A 次）
- `LessThan<A, B>`：大小比较
- 每项配 `Equal` 断言（如 `Equal<Add<3, 4>, 7>`、`Equal<Sub<10, 4>, 6>`、`Equal<Mul<3, 4>, 12>`、`Equal<LessThan<2, 3>, true>`）+ 反例 `@ts-expect-error`

### 技术要点
- 元组编码：数字 → 元组 → 运算 → 取 `["length"]`（README「核心概念 2」）
- `BuildTuple` 模板照 README 抄（「原理」示意图那段）：累加器参数 + 递归出口
- 减法两条路：**元组切片**（`BuildTuple<A> extends [...BuildTuple<B>, ...infer Rest] ? Rest["length"]`）或**递归递减**（长度差 1 就递归一次）
- 乘法：`Add` 的递归版——需要一个累加计数参数，数到 A 次就停
- `LessThan`：`BuildTuple<A> extends [...BuildTuple<B>, ...infer _]` 判断 A 能否"包含" B——能包含说明 A ≥ B
- 注意递归深度（几百层就到顶）：测试数字别超过 20，`BuildTuple<1000>` 会爆（README「核心概念 5」）

### 超纲提示
🔧 除法 / 取模：更难的递归（连续减直到不够减，数减了几次）——做出来你就是类型层图灵完备的完整证明。

### 自测方法
```bash
cd s32_typescript && npm run typecheck
# 全绿 = 全过。验收点：Add / Sub / Mul / LessThan 各配 Equal 断言；数字保持小值（≤ 20）
```

## 做完之后
- 自查：你用了本章哪些概念？——递归条件类型 / infer / 映射类型 / 模板字面量类型 / 元组长度编码 / Equal 断言 + @ts-expect-error
- 想继续深挖：回看本章 README 的「跟 Agent 的关系」，选一个点展开——比如打开 zod 或 trpc 的 .d.ts，找找里面有没有你刚写过的 DeepPartial / infer 模式
