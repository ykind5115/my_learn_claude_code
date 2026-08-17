# s32-11: 文件系统 / subprocess — Agent 工具的文件层

[← 返回概览](../README.md) | [上一章：Error / 异常处理](../s10_error_handling/) | [下一章：高级类型](../s12_advanced_types/)

> 一句话核心思想：**fs/promises 读写文件、path.join 拼路径、流处理大数据、spawn 调用外部程序——这就是 Agent 的 Read/Write/Bash 工具的底层实现。**

---

## 问题 — 为什么文件操作有这么多讲究？

文件操作看似简单，坑都在细节里：

1. **异步 vs 同步**：同步读写会阻塞事件循环（s04）——几百个并发请求时服务器直接卡死
2. **路径**：Windows 用 `\`，Linux 用 `/`，字符串拼接跨平台必炸；相对路径依赖 cwd，换个目录跑就找不到文件
3. **大文件**：`readFile` 把整个文件读进内存——一个 10GB 的日志文件直接 OOM
4. **子进程安全**：把用户输入拼进 shell 命令 = 命令注入

---

## 原理 — 一句话 + 示意图

**文件是字节，路径是地址，流是水管，子进程是"在代码里开终端"。**

```
你的程序
   │
   ├─ fs/promises ──→ 操作系统 ──→ 硬盘（读写字节）
   │     readFile: 一口闷（小文件）
   │     createReadStream: 水管分块流（大文件）
   │
   ├─ path.join ──→ 拼出正确的地址（跨平台）
   │
   └─ child_process ──→ 启动另一个程序，通信拿结果
```

---

## 核心概念 — 分点讲解

### 1. fs 三代 API

| 版本 | 风格 | 用不用 |
|---|---|---|
| `fs.readFile` (callback) | error-first 回调 | 老代码里见，新代码别写 |
| `fs.readFileSync` | 同步阻塞 | 只在启动初始化时用 |
| `fs/promises` | Promise + await | **新代码默认** |

### 2. 路径铁律

```typescript
const notePath = join(import.meta.dirname, "data", "note.md");
// ❌ "data\\note.md"      —— 写死分隔符，跨平台炸
// ❌ join(process.cwd())   —— cwd 随启动目录变，换个目录跑就找不到
```

`import.meta.dirname` = 当前文件所在目录，**永远稳定**。本模块全量遵守。

### 3. 流：大数据的正确姿势

```typescript
// 一次性：1GB 文件 = 1GB 内存
const whole = await readFile(bigPath, "utf8");

// 流式：固定小块内存，边读边处理
const stream = createReadStream(bigPath, { highWaterMark: 64 * 1024 });
for await (const chunk of stream) { /* 每次 64KB */ }
```

流不仅用于文件——网络响应、日志追踪、数据处理管道，都是流。

### 4. exec vs spawn vs spawnSync

| API | 行为 | 场景 |
|---|---|---|
| `spawnSync` | 同步等待全部完成 | 演示、短命令 |
| `exec` | 缓冲全部输出（默认 1MB 上限） | 小输出、简单命令 |
| `spawn` | 流式输出，异步 | 大输出、长任务 |

**防命令注入**（重要）：

```typescript
// ❌ 用户输入拼进字符串——可以注入 ; rm -rf / 之类
exec(`git log ${userInput}`);

// ✅ 参数数组——输入永远只是「一个参数」，不是命令的一部分
spawn("git", ["log", userInput]);
```

---

## 跟 Agent 的关系 — 连接到 Claude Code

Agent 的文件操作工具（s02_tool_use）落到代码就是本章内容：

```typescript
// Read 工具 ≈ readFile
async function readTool(filePath: string): Promise<ToolResult> {
  const content = await readFile(join(workspaceRoot, filePath), "utf8");
  return { ok: true, content };
}

// Write 工具 ≈ writeFile
// Bash 工具 ≈ spawn(shell, ["-c", command])
```

- 路径解析用 `import.meta.dirname` + `join`，防止工具越权访问项目外文件
- 大文件读取用流，避免一个超大文件撑爆 Agent 进程
- Bash 工具的参数化调用是防注入的第一道防线

---

## 试一下

```bash
node s32_typescript/s11_fs_process/code.ts

# 实验 1：把第 4 步的 highWaterMark 改成 1024，看块数变化
# 实验 2：用 fs/promises 写一个函数：递归列出目录树（readdir withFileTypes 递归）
# 实验 3：spawnSync("git", ["status", "--short"]) 在仓库根目录跑，看输出
```

---

## 小结 — 记住这个就够了

1. **新代码用 fs/promises + await**；同步版本只在启动初始化时用
2. **路径 = path.join + import.meta.dirname**，绝不手拼字符串
3. **大文件走流**：readFile 一口闷，createReadStream 分块喝
4. **子进程参数用数组（spawn），不拼字符串（exec）**——防命令注入
