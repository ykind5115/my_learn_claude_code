# s32-12: 高级类型 — keyof、条件类型、infer 的进阶玩法

[← 返回概览](../README.md) | [上一章：文件系统 / subprocess](../s11_fs_process/) | [下一章：Decorator](../s13_decorator/)

> 一句话核心思想：**高级类型 = 类型层的编程语言：keyof 取钥匙、条件类型写 if、映射类型写循环、infer 做模式匹配。**

---

## 问题 — 为什么需要"类型层的编程"？

写出一个函数很容易，写出一个**通用的、类型安全的**函数很难。比如：

```typescript
// 想写一个「安全取值」函数，怎么标注？
function getProp(obj, key) { return obj[key]; }

getProp(user, "name");   // 希望返回 string
getProp(user, "age");    // 希望返回 number
getProp(user, "typo");   // 希望编译报错
```

普通类型做不到"返回值类型跟着 key 变"。答案在类型层的三件工具里：keyof、泛型约束、索引访问。

---

## 原理 — 一句话 + 示意图

**把类型当成数据来操作：从形状里取钥匙（keyof）、按钥匙取类型（索引访问）、用条件分支（条件类型）、遍历钥匙（映射类型）、从结构里猜子类型（infer）。**

```
interface User { name: string; age: number; email: string }
                      │
              keyof User ──→ "name" | "age" | "email"（钥匙集合）
                      │
              User["name"] ──→ string（索引访问：按钥匙取类型）
                      │
    { [K in keyof User]?: User[K] } ──→ { name?: string; age?: number; email?: string }
                      │                （映射类型：遍历钥匙，改写每个字段）
              T extends (...args) => infer R ? R : never
                      │                （infer：模式匹配提取）
```

---

## 核心概念 — 分点讲解

### 1. keyof + 索引访问 + 泛型约束（三合一）

```typescript
function getProp<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
```

- `keyof T`：T 的钥匙集合
- `K extends keyof T`：K 必须是合法钥匙（typo 直接编译报错）
- `T[K]`：索引访问——返回类型跟着钥匙走

### 2. 条件类型与分布式

```typescript
type IsString<T> = T extends string ? true : false;   // 类型层的 if

// 分布式：T 是 union 时，逐个判断再拼回
type ToArray<T> = T extends unknown ? T[] : never;
// ToArray<string | number> = string[] | number[]（拆开各判一次！）
```

`Exclude<T, U>`、`Extract<T, U>` 等内置类型就是分布式条件类型的应用。

### 3. infer：模式匹配提取

```typescript
type ReturnTypeOf<T> = T extends (...args: never[]) => infer R ? R : never;
type ElementOf<T> = T extends readonly (infer E)[] ? E : never;
```

**infer = 「这个位置的类型，帮我猜出来并命名」**。看懂 infer，90% 的复杂 .d.ts 都读得通。

### 4. 映射类型：内置工具的实现

```typescript
type MyPartial<T> = { [K in keyof T]?: T[K] };      // = Partial
type MyPick<T, K extends keyof T> = { [P in K]: T[P] };  // = Pick
type MyRecord<K extends PropertyKey, V> = { [P in K]: V }; // = Record
```

三板斧：遍历钥匙 + 逐钥匙定类型 + 加减修饰符（`?` / `readonly`）。

### 5. satisfies：只检查，不改变推断

```typescript
const config = { host: "localhost", port: 8080 } as const satisfies Record<string, string | number>;
config.port;   // 类型仍是字面量 8080（标注会退化成 number）
```

**标注改变推断，satisfies 只做检查**——鱼和熊掌兼得。注意：保留字面量类型要写 `as const satisfies`（单用 satisfies 仍会把 `8080` 加宽成 `number`）。

---

## 跟 Agent 的关系 — 连接到 Claude Code

SDK 里的"魔法类型"全是本章的内容：

```typescript
// 工具定义从实现类推导出参数/返回类型
type ToolInput<T> = T extends Tool<infer I, infer O> ? I : never;

// API 客户端的响应类型自动从 schema 推导
// 配置对象的 satisfies 校验
```

读 Claude Code 的 .d.ts 时，这些构造会反复出现——本章就是那张"读图指南"。

---

## 试一下

```bash
node s32_typescript/s12_advanced_types/code.ts
cd s32_typescript && npm run typecheck   # 类型层面的结论靠它验证

# 实验 1：手写 MyReadonly 和 MyOmit（对照 Partial/Pick 的写法）
# 实验 2：写一个 ExtractPromiseValue<T>（用 infer 从 Promise<X> 提取 X）
# 实验 3：给 getProp 加一个「默认值」参数，key 不存在时返回默认值
```

---

## 小结 — 记住这个就够了

1. **keyof 取钥匙，T[K] 按钥匙取类型**——类型安全取值的三件套
2. **条件类型 = 类型层 if**；union 会被拆开逐个判断（分布式）
3. **infer = 模式匹配提取**——猜出结构的某个位置并命名
4. **映射类型 = 类型层循环**——Partial/Pick/Record 就是这么实现的
5. **satisfies 只检查不改变推断**——现代推荐写法
