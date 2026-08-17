# s32-08: 泛型 — 类型也能当参数

[← 返回概览](../README.md) | [上一章：npm / pnpm](../s07_pkg_manager/) | [下一章：class](../s09_class/)

> 一句话核心思想：**泛型 = 类型参数化：同一个函数适配多种类型，而且不丢失类型信息。**

---

## 问题 — 为什么不能直接用 any？

```typescript
function identity(value: any): any { return value; }

const s = identity("你好");
s.toUpperCase();        // ✅ 能跑
s.不存在的属性.foo();   // ❌ 也能编译通过！运行时才爆炸
```

`any` 把检查全关掉了——**进来是 any，出去也是 any，类型信息在中途蒸发**。泛型要的就是"进来 string，出去还是 string"：

```typescript
function identity<T>(value: T): T { return value; }

const s = identity("你好");   // T 推断为 string，s: string
s.toUpperCase();              // ✅ 检查有效
s.不存在的属性();              // ❌ 编译期报错
```

---

## 原理 — 一句话 + 示意图

**泛型 = 类型的占位符：调用时填入具体类型，编译器按"填好的版本"检查。**

```
function identity<T>(value: T): T { ... }

identity("你好")    →  T 填 string  →  identity(value: string): string
identity(42)       →  T 填 number  →  identity(value: number): number
```

类型推断很聪明：大多数时候不用显式写 `<string>`，TS 从参数自己猜。类型在编译期被擦除（s00），所以**泛型是零运行时开销的**——它纯粹是编译期的记账。

---

## 核心概念 — 分点讲解

### 1. 泛型约束 extends

```typescript
function findById<T extends HasId>(items: T[], id: string): T | undefined {
  return items.find((item) => item.id === id);   // 约束保证 item.id 存在
}
```

**extends = "至少长这样"**（不是继承）：T 必须满足 HasId 形状。约束让你在函数体内安全使用约束声明的成员，同时返回值保持精确类型（传 User[] 返回 User）。

### 2. 泛型接口 / 泛型类 / 默认类型参数

```typescript
interface Result<T, E = Error> { ... }   // E 有默认值：Result<number> = Result<number, Error>

class Box<T> {
  #content: T;
  get(): T { return this.#content; }     // 装 string 的盒子取出就是 string
}
```

### 3. 内置泛型工具（天天见）

| 工具 | 作用 | 例子 |
|---|---|---|
| `Array<T>` | 数组 | `number[]` 的完整写法 |
| `Promise<T>` | 异步结果 | `Promise<string>` |
| `Partial<T>` | 全字段变可选 | 部分更新 |
| `Pick<T, K>` | 挑字段 | 视图/摘要 |
| `Record<K, V>` | 键值字典 | 索引表 |
| `Omit<T, K>` | 删字段 | 反 Pick |

它们本质是"类型层的小函数"——s12 会手写实现，s15 会玩到极限。

---

## 跟 Agent 的关系 — 连接到 Claude Code

SDK 里的工具函数大量使用泛型：

```typescript
// 包装一个 API 调用，返回类型由调用方决定
async function callApi<T>(endpoint: string, body: unknown): Promise<T> { ... }

const tools = await callApi<ToolDefinition[]>(...);   // T = ToolDefinition[]
const message = await callApi<Message>(...);          // T = Message
```

- 同一个函数服务十几种返回类型——泛型的典型场景
- 约束保证 Agent 工具都实现了统一的 `execute(args)` 接口
- `Result<T>` 模式是 s10 错误处理的主角，也是很多 Agent 框架的返回约定

---

## 试一下

```bash
node s32_typescript/s08_generics/code.ts

# 实验 1：给 identity 写一个调用，故意传错显式类型参数 identity<boolean>("不是布尔")，
#         看 typecheck 报什么
# 实验 2：写一个泛型函数 pair<T, U>(a: T, b: U): [T, U]，试几种调用
# 实验 3：把 findById 的约束去掉（变成 items: any[]），看函数体里还能不能用 item.id
```

---

## 小结 — 记住这个就够了

1. **泛型 = 类型参数化**：适配多种类型 + 不丢类型信息（any 的克星）
2. **extends = 至少长这样**：约束让函数体安全，返回值精确
3. **零运行时开销**：泛型在编译期擦除，纯粹是编译期记账
4. **内置泛型是日常**：Partial / Pick / Record 天天用，s12 手写实现
