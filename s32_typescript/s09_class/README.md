# s32-09: class — 面向对象的家当

[← 返回概览](../README.md) | [上一章：泛型](../s08_generics/) | [下一章：Error / 异常处理](../s10_error_handling/)

> 一句话核心思想：**class 是「数据 + 操作数据的方法」的打包；TS 在 JS class 之上加了类型检查，但只有 `#` 私有是运行时真隔离。**

---

## 问题 — 为什么需要 class？

对象 + 函数满天飞的代码，数据和操作是散的：

```typescript
// 没有 class：数据和操作分离，谁都可能把 balance 改坏
const account = { no: "6222", balance: 1000 };
account.balance = -99999;   // 没人拦，数据坏了
function deposit(a: any, n: number) { a.balance += n; }   // 谁都可以传错对象
```

class 把数据和操作打包在一起，用封装（私有 + 门禁方法）保护数据。

---

## 原理 — 一句话 + 示意图

**class = 实例的图纸：字段装数据，方法操作数据，修饰符划定访问边界。**

```
                    BankAccount（图纸）
        ┌────────────────────────────────────┐
        │  readonly accountNo    ← 只读      │
        │  private ownerName     ← 编译期私有 │
        │  #balance              ← 运行时私有 │
        │  protected createdAt   ← 子类可见   │
        │  deposit()  get balance  describe()│ ← 门禁方法
        └────────────────────────────────────┘
                         │ new
                         ▼
                   acc（实例，按图纸造出来）
```

---

## 核心概念 — 分点讲解

### 1. private vs `#`：一个挡编译期，一个挡运行时（本章最重要的知识点）

| | `private` | `#私有字段` |
|---|---|---|
| 检查时机 | 编译期（标签擦除后消失） | 编译期 + 运行时（私有槽） |
| `as any` 绕过 | ✅ 能拿到 | ❌ 拿不到 |
| `Object.keys` | 能看到 | 看不到 |
| 本质 | TS 类型系统特性 | JS 原生语法 |

```typescript
const anyAcc = acc as any;
anyAcc.ownerName;   // "王小明" —— private 形同虚设
anyAcc["#balance"]; // undefined —— # 运行时也在岗
```

**数据安全用 `#`，团队协作提示用 `private`**（两者可以并存）。

### 2. 参数属性：为什么本模块 code.ts 看不到它

```typescript
// ❌ 参数属性：constructor(private x: number) {}  —— 编译后真的生成赋值代码
//    属于「不可擦除语法」，node 直跑 .ts 会报错
class A {
  constructor(private x: number) {}
}

// ✅ 可擦除的等价写法
class A {
  private x: number;
  constructor(x: number) { this.x = x; }
}
```

参数属性本身很好用（少写三行），但为了零构建直跑，本模块统一用显式写法。**在真实工程里（有构建步骤），参数属性随便用。**

### 3. extends / abstract / implements 分工

| 关键字 | 干什么 | 类比 |
|---|---|---|
| `extends` | 继承实现（代码复用） | 继承家产 |
| `abstract` | 模板 + 规矩（子类必须实现抽象方法） | 公司章程 |
| `implements` | 承诺接口（只查形状，不继承代码） | 签合同 |

```typescript
abstract class Shape {
  abstract area(): number;    // 子类必须实现
  describe() { ... }          // 共享实现
}
class Circle extends Shape { area() { ... } }   // 多态：同一种类型，各自实现
```

### 4. getter / setter：属性语法 + 方法逻辑

```typescript
get fahrenheit(): number { return this.#celsius * 9 / 5 + 32; }
set fahrenheit(f: number) {
  if (f < -459.67) throw new Error("低于绝对零度");   // 写入前的门禁
  this.#celsius = (f - 32) * 5 / 9;
}
```

读时计算、写时校验——外面永远通过门禁，不直接摸数据。

---

## 跟 Agent 的关系 — 连接到 Claude Code

Claude Code 的 SDK 里，类无处不在：

```typescript
class AgentLoop {
  #config: LoopConfig;              // 运行时真私有：配置不能被外部乱动
  async run(query: Query): Promise<Result> { ... }
}

class ToolExecutor implements Tool {   // implements 承诺工具接口
  execute(args: unknown): Promise<ToolResult> { ... }
}
```

- `#` 私有保护内部状态（Agent 的会话状态、配置）——`as any` 绕不过去
- `implements Tool` 保证每个工具都提供统一的执行接口——Agent 才能统一调度
- 抽象类定义"一个工具必须会什么"，具体工具类各实现各的

---

## 试一下

```bash
node s32_typescript/s09_class/code.ts

# 实验 1：把 BankAccount 的 #balance 改成 private，重跑看「绕过」实验的结果变化
# 实验 2：给 Shape 家族加一个 Triangle（底×高÷2），放进 shapes 数组一起跑
# 实验 3：写一个用参数属性的类，跑 node 直跑看报什么错（体验不可擦除语法）
```

---

## 小结 — 记住这个就够了

1. **`#` 私有 = 真私有**（运行时隔离）；private/protected = 编译期约定（擦除后消失）
2. **参数属性不可擦除**——本模块用显式写法，真实工程里随便用
3. **extends 继承代码，implements 承诺形状，abstract 立规矩**——三件套分工明确
4. **getter/setter = 数据的门禁**：读时计算，写时校验
