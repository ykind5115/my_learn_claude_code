# s32-06: Node.js — 代码跑在什么底座上

[← 返回概览](../README.md) | [上一章：ES Module](../s05_es_module/) | [下一章：npm / pnpm](../s07_pkg_manager/)

> 一句话核心思想：**Node = V8（执行 JS）+ libuv（异步 I/O 引擎），TypeScript 代码最终都跑在这两个底座上。**

---

## 问题 — 为什么 TypeScript 能写"后端"？

浏览器里的 JS 只能操作网页。Node.js 把 V8 引擎从浏览器里拆出来，装上了**操作系统能力**：

- 读写文件、开网络服务、跑子进程（浏览器做不到的事）
- 再加上 s04 的事件循环（异步 I/O），单线程也能支撑高并发

从此一门语言可以写前后端——这也是 Claude Code 能做成 CLI 工具的技术前提。

---

## 原理 — 一句话 + 示意图

**Node = V8（执行 JS 代码）+ libuv（异步 I/O 事件循环）+ 内置模块（操作系统能力的封装）。**

```
你的 TS 代码（类型被擦除后）
        │
        ▼
┌─────────────────────────────┐
│           Node.js           │
│  ┌─────────┐  ┌──────────┐  │
│  │   V8    │  │  libuv   │  │
│  │ 执行代码 │  │ 事件循环  │  │
│  └─────────┘  └──────────┘  │
│  内置模块: fs / http / path / │
│  child_process / crypto ...  │
└─────────────────────────────┘
        │
        ▼
      操作系统（文件、网络、进程）
```

---

## 核心概念 — 分点讲解

### 1. process 对象：代码与运行时的对话窗口

```typescript
process.version            // Node 版本
process.argv               // 启动参数（node code.ts 后面跟的东西）
process.env                // 环境变量 —— API Key 就住这里
process.cwd()              // 当前工作目录
process.exitCode           // 退出码（0 = 正常）
```

**环境变量的安全红线**：`ANTHROPIC_API_KEY` 这类密钥通过 `.env` 文件 → 环境变量 → `process.env` 进入程序，**永不写进代码或打印到日志**。这是 Agent 系统拿到 API Key 的标准路径。

### 2. Buffer：二进制数据的地基

```typescript
const buf = Buffer.from("你好", "utf8");  // 字符串 → 字节
buf.toString("base64");                    // 字节 → base64 文本
```

文件读写、网络传输，底层全是 Buffer（字节数组）。看到 `Buffer` 就想到"字节"。

### 3. 内置模块总览（node: 前缀）

| 模块 | 干什么 | 对应章节 |
|---|---|---|
| `node:fs` / `node:fs/promises` | 文件系统 | s11 |
| `node:path` | 路径拼接 | s11 |
| `node:child_process` | 跑子进程 | s11 |
| `node:http` | HTTP 服务器/客户端 | s16 |
| `node:crypto` | 加密、哈希 | — |
| `node:os` / `node:url` | 系统信息 / URL 解析 | — |

### 4. 最小 HTTP 服务器（引子）

```typescript
const server = createServer((req, res) => {
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify({ hello: "world" }));
});
await new Promise<void>((resolve) => server.listen(0, resolve));  // 端口 0 = 随机
```

三个要点：回调函数处理每个请求；**端口 0 让系统随机分配**（演示代码不打架）；用完 `server.close()`。完整 REST API 在 s16 展开。

---

## 跟 Agent 的关系 — 连接到 Claude Code

Claude Code 就是一个跑在 Node 上的 TS 程序：

- 你敲 `claude` → Node 加载 JS 入口 → 进入 Agent 循环（s01）
- Agent 的 Bash 工具 = `child_process.spawn` 一个 shell
- 工具的文件操作 = `node:fs` 的封装（s02_tool_use 的底层实现）
- API Key = `process.env.ANTHROPIC_API_KEY`

**你学的这个模块，就是 Claude Code 自己的技术栈。** 学 Node.js = 学 Agent 的运行时底座。

---

## 试一下

```bash
node s32_typescript/s06_node/code.ts
node s32_typescript/s06_node/code.ts --verbose extra-args   # 看 argv 变化

# 实验 1：把第 4 步的响应改成返回 process.version，重启看效果
# 实验 2：node -e "console.log(Object.keys(process.env).length)" 看看环境变量有多少
```

---

## 小结 — 记住这个就够了

1. **Node = V8 + libuv + 内置模块**——TS 代码的运行时底座
2. **process.env 是密钥的家**——敏感信息永不进代码/日志
3. **Buffer = 字节**——一切 I/O 的地基
4. **createServer + listen(0) + close**——HTTP 服务器最小内核，s16 再展开
