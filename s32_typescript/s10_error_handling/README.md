# s32-10: Error / 异常处理 — 程序摔倒了怎么优雅地站起来

[← 返回概览](../README.md) | [上一章：class](../s09_class/) | [下一章：文件系统 / subprocess](../s11_fs_process/)

> 一句话核心思想：**错误处理 = 决定「谁能接住、怎么接住、接住后干什么」——同步靠 try/catch，异步靠 await+catch 或 .catch，业务错误还可以根本不抛。**

---

## 问题 — 为什么错误处理值得专门一章？

程序总会出错：文件不存在、网络断了、用户传了非法数据。错误的代价不在于"发生了"，而在于：

- **没接住的错误**：进程崩溃，用户看到一坨 stack trace
- **接住但吞掉的错误**：`catch (e) {}` 静默吞掉——bug 藏起来了，更难查
- **没带上下文的错误**：`Error: something went wrong`——排查无从下手

好的错误处理让程序**可恢复**（重试、降级、提示）和**可排查**（日志带上下文）。

---

## 原理 — 一句话 + 示意图

**throw 把错误沿调用栈往上抛，直到遇到 catch 接住；没人接就轮到进程崩溃。**

```
main() ──→ fetchUser() ──→ parseData() ──→ 💥 throw ApiError
  │            │              │
  │            │         没有 catch，继续往上抛
  │            │
  │     有 try/catch → 接住，处理 ✅
  │
  （都没 catch）→ 进程崩溃 ❌
```

**异步版本**：async 函数里的 throw = 返回 rejected Promise，`await` 抛出该错误 → try/catch 接住；忘了 await 的错误静默丢失；完全没人处理的拒绝触发 `unhandledRejection`。

---

## 核心概念 — 分点讲解

### 1. 内置错误家族

`Error`（基类）、`TypeError`（类型错）、`RangeError`（越界）、`SyntaxError`（语法错）——区分错误种类靠 `instanceof`。

### 2. 自定义错误类：给错误一份"档案"

```typescript
class ApiError extends Error {
  readonly statusCode: number;
  constructor(statusCode: number, message: string) {
    super(message);
    this.name = "ApiError";       // 修正 name（否则显示 Error）
    this.statusCode = statusCode; // 附加上下文
  }
}

// 使用
if (e instanceof ApiError) {
  log(`[${e.statusCode}] ${e.message}`);   // 排查线索齐全
}
```

### 3. 异步错误的三条路

| 方式 | 场景 |
|---|---|
| `await` + `try/catch` | async/await 风格 |
| `.catch(e => ...)` | 链式风格、补救忘 await 的 Promise |
| `process.on("unhandledRejection")` | 全局兜底：记录日志、上报、优雅退出 |

**头号坑**：忘了 `await` 的 Promise 拒绝会静默丢失——这正是 unhandledRejection 存在的意义。

### 4. Result 模式 vs throw

```typescript
// Result：不抛异常，返回联合类型（s03 的判别联合！）
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };
const r = safeDivide(10, 0);   // 不会炸，返回 { ok: false, error: "..." }
if (!r.ok) { ... }             // 编译期强制你处理失败分支

// throw：让错误沿栈爆炸
throw new RangeError("除数不能为 0");
```

**选择标准**：

- **可预期的业务失败**（校验不过、用户不存在、除零）→ **Result**：调用方必须显式处理，失败路径写进类型
- **预期外的编程错误**（逻辑 bug、环境崩坏）→ **throw**：保留完整调用栈
- 混合用法：业务错误 Result、编程错误 throw（很多 Agent 框架的选择）

### 5. Node 的 error-first callback 传统（了解）

```typescript
// 老式 callback API：第一个参数永远是错误
fs.readFile("x.txt", (err, data) => {
  if (err) { ... }   // error-first
});
// 现代推荐：fs/promises + await（s11 的主角）
```

---

## 跟 Agent 的关系 — 连接到 Claude Code

Agent 系统是"错误处理密集型"软件——模型可能超时、API 可能 429、工具可能执行失败。s11_error_recovery 讲的恢复机制，落到代码就是本章的内容：

```typescript
// Agent 调用工具：业务失败用 Result，系统错误用 throw
const result = await tool.execute(args);     // Result<ToolError>：失败不炸
if (!result.ok) return recoverFrom(result.error);   // 恢复策略

// API 调用：throw + 全局兜底（重试、退避、换模型）
try {
  response = await api.call(...);
} catch (e) {
  if (e instanceof RateLimitError) await backoffRetry();
  else throw e;   // 交给上层或全局 handler
}
```

**"接住能恢复的，抛出让上层处理的，兜底剩下的"** ——这就是 Agent 错误恢复的静态结构。

---

## 试一下

```bash
node s32_typescript/s10_error_handling/code.ts

# 实验 1：把第 3 步 dangling 的 .catch 删掉，重跑——观察 unhandledRejection 触发
# 实验 2：给 ApiError 加一个 retryable: boolean 字段，模拟「可重试错误」
# 实验 3：写一个 Result 版本的 fetchUserFromApi，对比两种风格的调用代码
```

---

## 小结 — 记住这个就够了

1. **同步 try/catch/finally；异步 await+catch 或 .catch**；忘了 await 是头号坑
2. **自定义错误类**：继承 Error + 修正 name + 附加上下文
3. **unhandledRejection** = 最后的兜底网
4. **业务失败用 Result（编译期强制处理），编程错误用 throw（保留现场）**
