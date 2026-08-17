# s32-03: union / narrowing — 一个变量多种类型，如何安全收窄

[← 返回概览](../README.md) | [上一章：interface / type](../s02_interface_type/) | [下一章：async / Promise](../s04_async/)

> 一句话核心思想：**union 表达「或」，narrowing 把「或」变回「具体」——TS 类型安全 90% 的日常就发生在这两步之间。**

---

## 问题 — 为什么需要 union 和 narrowing？

真实世界的数据天然是"多种可能"：

```javascript
// 用户 id 可能是字符串（用户名）也可能是数字（数据库自增 id）
// 工具调用结果可能成功也可能失败
// 一个宠物可能是会飞的鸟也可能是会游的鱼
```

如果只用一个宽泛类型（any / object / unknown），会失去所有检查；如果硬拆成多个类型，又没法表达"就是这几者之一"。**union 解决表达问题，narrowing 解决使用问题。**

---

## 原理 — 一句话 + 示意图

**union = 几个类型的"或"；narrowing = 用运行时信息，把 union 在某段代码里"切"成具体的一个。**

```
        string | number | boolean      ← union：宽
              │
   typeof v === "string" ?             ← 运行时检查（收窄）
      ┌───────┴───────┐
      ▼               ▼
   string          number | boolean    ← 变窄了
（分支内可安全          │
  调用字符串方法）        │
                   后续再收窄
```

TS 的**控制流分析**（control flow analysis）会跟着 `if` / `switch` / `return` 走，自动更新每个分支里变量的类型——收窄不是魔法，是编译器在做"路径追踪"。

---

## 核心概念 — 分点讲解

### 1. union 的基本规则

```typescript
type Id = string | number;
const id: Id = "abc";

id.toUpperCase();  // ❌ 编译错误：number 没有这个方法
```

**union 上只能调用所有成员共有的能力**。想要独有能力，先收窄。

### 2. 四种收窄手段对比

| 手段 | 写法 | 适用场景 |
|---|---|---|
| `typeof` | `if (typeof v === "string")` | 基本类型（string/number/boolean…） |
| `in` | `if ("fly" in animal)` | 对象形状的区分 |
| 判别字段 | `switch (r.status)` | 每个成员带字面量标签的 union（**推荐**） |
| 类型守卫 | `if (isApiResponse(raw))` | 从 unknown 开始验证外部数据 |

### 3. 判别联合（discriminated union）—— 工业级标准写法

```typescript
type ApiResponse =
  | { status: "success"; data: string[] }
  | { status: "error"; code: number; message: string };
```

要点：**每个成员都有一个字面量类型的公共字段（`status`）**，这个字段就是"判别子"。判别联合的好处：

- 一眼看出有哪些情况（像 enum 一样自文档化）
- switch 判别子时，每个 case 里自动收窄到对应成员
- 配合 `never` 做**穷尽检查**：漏了哪个 case，编译期报错

```typescript
default:
  return assertNever(r);  // r 的类型是 never → 若加了新成员，这里编译报错
```

**穷尽检查 = 编译器帮你保证"所有情况都处理了"**。以后给 `ApiResponse` 加第三种 status，所有 switch 处立刻变红——这是维护大型系统的救命能力。

### 4. 类型守卫（type guard）：收窄的"自定义关卡"

```typescript
function isApiResponse(x: unknown): x is ApiResponse {
  // 运行时验证...
  return true;  // true 时 TS 相信你：x 现在就是 ApiResponse
}
```

`x is T` 签名是 TS 最强大的收窄能力之一。它把"验证逻辑"和"类型系统"打通：

**unknown → 守卫验证 → 精确类型**，这是处理一切外部数据（API 响应、JSON.parse、用户输入）的标准姿势。Claude Code 处理工具返回值时就是这个套路。

### 5. 常见陷阱

```typescript
// ❌ 陷阱 1：typeof null 也是 "object"
// ❌ 陷阱 2：用 any 绕过收窄，等于放弃所有检查
// ❌ 陷阱 3：字符串拼接的 union 少了 as const 会退化成 string
const s = { status: "success" };       // status: string（不是字面量！）
const s2 = { status: "success" } as const;  // status: "success" ✅
```

---

## 跟 Agent 的关系 — 连接到 Claude Code

Agent 循环（s01_agent_loop）里，每轮的核心动作是"调用工具、检查结果、决定下一步"。用 TS 写就是：

```typescript
type ToolResult =
  | { ok: true; content: string }
  | { ok: false; errorType: "timeout" | "permission" | "api"; message: string };

// 处理结果：switch 判别字段，穷尽检查保证每个错误类型都有对策
```

- 工具结果的成功/失败形态 = 判别联合
- 错误类型的枚举 = 判别字段
- 加上 never 穷尽检查 = **新增一种错误类型时，编译器逼你给每处处理逻辑补分支**——这正是 s11_error_recovery 讲的错误恢复机制的静态保障

---

## 试一下

```bash
node s32_typescript/s03_union_narrowing/code.ts

# 实验 1：给 ApiResponse 加第三种成员 { status: "pending" }，
#         看 typecheck 如何报"穷尽检查失败"
# 实验 2：自己写一个 shape 判别联合（circle/square），用 in 收窄计算面积
```

---

## 小结 — 记住这个就够了

1. **union = 「或」**，只能调用成员共有能力
2. **narrowing 四种手段**：typeof 分基本类型、in 分形状、判别字段 switch、类型守卫收 unknown
3. **判别联合 + never = 穷尽检查**：新情况漏处理，编译期报错
4. **unknown → 守卫 → 精确类型**是处理外部数据的标准姿势
