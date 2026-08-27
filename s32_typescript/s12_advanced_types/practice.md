# s32-12: 高级类型 — 动手需求

[← 返回总索引](../PRACTICE.md) | [本章教程](./README.md)

> 一句话核心思想：**高级类型 = 类型层的编程语言：keyof 取钥匙、条件类型写 if、映射类型写循环、infer 做模式匹配。**

学完本章，用下面这些需求把知识变成肌肉记忆。**只给需求和提示，不给完整代码**——卡住了回到主项目提问。

## 使用说明
- 前置技能：s01~s12（interface/type、泛型、收窄都要能随手用）
- 自测方式：node 直跑 + `cd s32_typescript && npm run typecheck`——**类型层面的结论一律靠 typecheck 验证，node 直跑只是演示**
- 解答文件建议放本章目录内，命名 `practice_<名字>.ts`
- 项目约定：相对导入必须带 `.ts` 扩展名；只用可擦除语法（类型/接口全部在编译期擦除，node 直跑零负担）；涉及文件路径一律 `import.meta.dirname`

## 需求 1：类型安全取值 getProp（⭐ 入门 | 核心技能：keyof + 泛型约束 + 索引访问）
- [ ] 完成

### 背景
README 的主案例——让「返回值类型跟着 key 走」变成直觉。这是 Lodash.get 的类型版，也是高级类型里最常用、最该条件反射的写法。

### 要做什么（验收标准）
- `function getProp<T, K extends keyof T>(obj: T, key: K): T[K]`（README 核心概念 1 三件套）
- `function getPropWithDefault<T, K extends keyof T>(obj: T, key: K, def: T[K]): T[K]`——key 存在返回值，不存在返回 def
- 演示：`interface User { name: string; age: number }`，验证：
  - `getProp(user, "name")` 推断为 `string`（`.toUpperCase()` 可用）
  - `getProp(user, "age")` 推断为 `number`（`.toFixed()` 可用）
  - `getProp(user, "typo")` 编译报错——用 `// @ts-expect-error` 注释掉，并保证该行确实在报错（typecheck 不报「未使用的 @ts-expect-error」）
  - `getPropWithDefault(user, "email", "无")` 也能推断出 `string`

### 技术要点
- `keyof T`：取形状的钥匙集合（`"name" | "age"`）
- `K extends keyof T`：K 必须是合法钥匙——typo 直接编译报错（README 核心概念 1 三合一）
- `T[K]` 索引访问：返回类型跟着 key 走
- 默认值版：`def: T[K]` 让默认值类型也和 key 绑定
- 运行时判断：`key in obj` 或 `obj[key] === undefined` 收窄不存在的情况

### 超纲提示
- 🔧 多级取值 `getPropDeep(obj, "a.b.c")`：需要 `infer` + 递归拆字符串字面量——超纲很大，当挑战题玩，卡住就回来

### 自测方法
- 建议解答文件：`s32_typescript/s12_advanced_types/practice_get_prop.ts`
- `cd s32_typescript && npm run typecheck`：0 错误（`@ts-expect-error` 那行是「期望报错」的声明，不算错误）
- `node s32_typescript/s12_advanced_types/practice_get_prop.ts`：打印各取值的演示结果
- 临时把 `@ts-expect-error` 删掉 → typecheck 报错，证明约束在工作，再恢复

## 需求 2：手写内置工具 + satisfies（⭐⭐ 组合 | 核心技能：映射类型 + satisfies）
- [ ] 完成

### 背景
README 实验 1 的完整版——手写一遍工具类型，映射类型的三板斧（遍历钥匙、逐钥匙定类型、加减修饰符）就长在脑子里了；satisfies 是现代 TS 校验配置的推荐写法。

### 要做什么（验收标准）
- 手写四个映射类型，**逐行注释每行作用**：
  - `MyPartial<T>`（`[K in keyof T]?: T[K]`）
  - `MyReadonly<T>`（`[K in keyof T]: readonly T[K]`）
  - `MyPick<T, K extends keyof T>`（`[P in K]: T[P]`）
  - `MyOmit<T, K extends keyof T>`（提示：`Pick` + 内置 `Exclude<keyof T, K>`，Exclude 是分布式条件类型）
- 每个工具类型至少一个使用演示（partialUser / readonlyUser / picked / omitted）
- 用 `as const satisfies` 校验配置对象：
  - `const config = { host: "localhost", port: 8080, retry: 3 } as const satisfies Record<string, string | number>`
  - 验证 `config.port` 类型仍是字面量 `8080`：`const p: 8080 = config.port;` 能通过
  - 对照：写 `const bad = { port: 8080 } satisfies Record<string, string>` → typecheck 报错

### 技术要点
- 映射类型 `[K in keyof T]`：类型层循环——遍历钥匙集合，逐钥匙写新类型（README 核心概念 4 三板斧）
- 修饰符：`?` 加可选、`readonly` 加只读；`Omit` 是「缩小钥匙集合」（Pick + Exclude 组合）
- `satisfies` 只检查不改变推断：通过 `Record<string, string | number>` 检查但 `port` 保留字面量 `8080`（README 核心概念 5）
- `as const satisfies`：单用 satisfies 会把 `8080` 加宽成 `number`，配 `as const` 才保留字面量
- 类型全部在编译期擦除，node 直跑零负担

### 超纲提示
- 🔧 实现 `MyRequired<T>`（`-?` 去掉可选修饰符）和 `MyMutable<T>`（`-readonly`）——映射类型修饰符的加减是同一套语法

### 自测方法
- 建议解答文件：`s32_typescript/s12_advanced_types/practice_my_utils.ts`
- `cd s32_typescript && npm run typecheck`：0 错误
- 可选加分：写一个 `Equal<A, B>` 断言类型（提示：`A extends B ? (B extends A ? true : false) : false` 双向往返），断言 `MyPartial<User>` 等于 `Partial<User>` 等
- `node s32_typescript/s12_advanced_types/practice_my_utils.ts`：跑 satisfies 演示输出

## 需求 3：类型安全事件表（⭐⭐⭐ 挑战 | 核心技能：infer + 索引访问 + 泛型）
- [ ] 完成

### 背景
README 说 infer 看懂 90% 的复杂 .d.ts——事件表是它最实用的场景：Node 的 EventEmitter 是 `any` 天堂，类型安全事件表能让 on/emit 全程有类型。这也是 s09 任务队列「事件回调」的类型版升级。

### 要做什么（验收标准）
- `interface EventMap { login: { user: string }; logout: void; error: { msg: string; code: number } }`
- `class TypedEmitter<EM extends Record<string, unknown>>`：
  - `on<K extends keyof EM>(event: K, cb: (payload: EM[K]) => void): void`
  - `emit<K extends keyof EM>(event: K, payload: EM[K]): void`
- 验证（全部靠 typecheck）：
  - `on("login", (p) => p.user)`——p 自动是 `{ user: string }`
  - `emit("login", { user: "a" })` 通过
  - `emit("login", { bad: 1 })` 编译报错（用 `@ts-expect-error` 留证）
  - `logout` 的 void payload 边界：`on("logout", () => {})` 回调可无参数、`emit("logout")` payload 可省略——跑 typecheck 验证（void 参数的特例）
- 运行时：内部用 `Map` 存回调（`Map<K, Array<(payload: EM[K]) => void>>`），emit 时逐个调用——简单实现，不用 EventEmitter

### 技术要点
- 泛型约束 `EM extends Record<string, unknown>`：事件表必须是「事件名 → payload 类型」的映射（s08 泛型约束 + 索引签名）
- `K extends keyof EM` + `EM[K]`：事件名与 payload 类型绑定，on/emit 两端一致
- void payload 边界：`EM[K]` 是 `void` 时，回调可以少写参数、emit 可以省略 payload——TS 对 void 参数的特例处理
- 回调注册表：`Map` 存数组，同事件多次 `on` 是叠加不是覆盖

### 超纲提示
- 🔧 对比 Node 原生 `EventEmitter` 的 `on(event: string, listener: (...args: any[]) => void)`——`any` 风格 vs 你的泛型版本，写两句感想

### 自测方法
- 建议解答文件：`s32_typescript/s12_advanced_types/practice_typed_emitter.ts`
- `cd s32_typescript && npm run typecheck`：0 错误（`@ts-expect-error` 行验证 emit 传错 payload 确实报错）
- `node s32_typescript/s12_advanced_types/practice_typed_emitter.ts`：login / logout / error 三个事件跑通，控制台有输出
- 故意把 `emit("login", { bad: 1 })` 的 `@ts-expect-error` 删掉 → typecheck 报错，再恢复

## 做完之后
- 自查：你用了本章哪些概念？
  - keyof / 泛型约束 / 索引访问 T[K]
  - 映射类型（含 `?` / `readonly` 修饰符）
  - satisfies / as const（只检查不改变推断）
  - 条件类型 / Exclude（MyOmit 里用到）
  - infer（超纲提示里可选）
- 想继续深挖：回看本章 README 的「跟 Agent 的关系」——SDK 的 `ToolInput<T> = T extends Tool<infer I, infer O> ? I : never`；选一个点展开：比如给 TypedEmitter 加 `once` 方法，或实现 `ExtractPromiseValue<T>`（README 实验 2）后，给 s09 需求 3 的任务队列换上一套类型安全的事件表
