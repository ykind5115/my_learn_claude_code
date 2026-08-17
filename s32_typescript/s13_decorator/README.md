# s32-13: Decorator — 给代码声明式地加功能

[← 返回概览](../README.md) | [上一章：高级类型](../s12_advanced_types/) | [下一章：Compiler API](../s14_compiler_api/)

> 一句话核心思想：**装饰器是「包装函数」的语法糖——把日志、计时、注册这类横切功能，用一行 @ 挂到类或方法上。**

---

## 问题 — 为什么需要装饰器？

看一个没有装饰器的服务类：

```typescript
class ApiService {
  fetchUser(id: number): string {
    console.log(`[log] → fetchUser(${id})`);       // 日志和业务混在一起
    const t1 = performance.now();                   // 计时也混在一起
    const result = `用户${id}`;                     // ← 真正的业务只有这一行
    console.log(`[log] ← fetchUser = ${result}`);
    console.log(`[measure] 耗时 ${performance.now() - t1}ms`);
    return result;
  }
}
```

日志、计时这类**横切关注点**（cross-cutting concerns）在每个方法里复制粘贴，业务逻辑被淹没。装饰器的答案：

```typescript
class ApiService {
  @log
  @measure("fetchUser")
  fetchUser(id: number): string {
    return `用户${id}`;      // 业务代码干干净净
  }
}
```

---

## 原理 — 一句话 + 示意图

**装饰器 = 包装函数的语法糖：编译时把 @log 翻译成「用 log 函数包装原方法」。**

```
你写的:                         编译后（概念上）:
@log                             fetchUser = log(原始fetchUser)
@measure("x")                    ↑
fetchUser() {...}                层层包装：先 measure 再 log（从下往上）
```

方法装饰器签名（TS5 标准装饰器）：

```typescript
function log<This, Args extends unknown[], Return>(
  originalMethod: (this: This, ...args: Args) => Return,   // 原方法
  context: ClassMethodDecoratorContext<...>,                // 上下文（名字、种类等）
): (this: This, ...args: Args) => Return { ... }            // 返回替换方法
```

---

## 核心概念 — 分点讲解

### 1. 三种装饰器

| 装饰器 | 接收 | 典型用途 |
|---|---|---|
| 类装饰器 | (原类, 上下文) | 依赖注入容器、组件注册 |
| 方法装饰器 | (原方法, 上下文) | 日志、计时、缓存、权限 |
| 字段装饰器 | (undefined, 上下文) | 序列化映射、数据绑定 |

### 2. 裸装饰器 vs 装饰器工厂

```typescript
@log                    // 裸装饰器：直接当装饰器用
@measure("fetchUser")   // 工厂：先接配置，返回真正的装饰器
```

需要传参数时用工厂（多包一层函数）。

### 3. 叠加顺序：从下往上应用

```typescript
@log          // ② 后应用：包在最外层
@measure("x") // ① 先应用：包在内层
method() {}
```

调用时的执行顺序：log 进 → measure 进 → 原方法 → measure 出 → log 出（code.ts 输出可证）。

### 4. 为什么本章不能 node 直跑？

装饰器是**不可擦除语法**——编译后真的生成包装代码（`__esDecorate` helper），所以：

```bash
npm run demo:s13    # = tsc -p s13_decorator && node s13_decorator/dist/code.js
```

**这是本模块唯一需要编译的章节**。编译产物是纯标准 JS——看一眼 `dist/code.js`，你看到的全是函数组合，没有任何"装饰器"概念。这正是 s00 说的：编译器把高级语法翻译成运行时能懂的东西。

### 5. 历史包袱提示

- 老代码里的 `experimentalDecorators`（旧版装饰器）和本章的**标准装饰器**语法不同
- TS 5.0+ 默认使用标准装饰器；读到旧资料时注意区分

---

## 跟 Agent 的关系 — 连接到 Claude Code

- NestJS（Node 生态最流行的后端框架之一）全站装饰器：`@Controller`、`@Get`、`@Inject`
- MCP server 框架的声明式 API 也是这个模式：`@tool("name")` 声明工具
- Agent 框架用类装饰器注册工具、用方法装饰器给工具加日志/限流

---

## 试一下

```bash
cd s32_typescript && npm run demo:s13

# 实验 1：给 fetchUser 再加一个 @log 重复装饰，看叠加输出
# 实验 2：写一个 @memo 装饰器（缓存方法返回值，参数相同直接返回缓存）
# 实验 3：打开 dist/code.js，找 __esDecorate，看装饰器编译成了什么
```

---

## 小结 — 记住这个就够了

1. **装饰器 = 包装函数的语法糖**——横切功能声明式挂载
2. **方法装饰器**：(原方法, 上下文) → 替换方法；**工厂**先配参数再装饰
3. **叠加从下往上应用**
4. **装饰器不可擦除**——本章是模块里唯一走 tsc 编译的章节
