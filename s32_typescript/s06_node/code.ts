/**
 * s32-06: Node.js — 代码跑在什么底座上
 *
 * ═══════════════════════════════════════════════════════════════
 * 学完本章你应该能回答：
 *   - Node 是什么？V8 和 libuv 各负责什么？
 *   - process 对象能做什么？API Key 从哪来？
 *   - 最小 HTTP 服务器由哪几部分组成？
 * ═══════════════════════════════════════════════════════════════
 *
 * 启动方式:
 *     node s32_typescript/s06_node/code.ts
 */

import { createServer } from "node:http";
import { spawnSync } from "node:child_process";
import { Color, print_step, print_note, print_key_point, print_section } from "../utils.ts";

async function demo_all(): Promise<void> {
  print_section("s32-06: Node.js");

  // ═══════════════════════════════════════════════════════════
  // 第 1 步: process — 与运行时对话的窗口
  // ═══════════════════════════════════════════════════════════
  print_step(1, "process — 代码与运行时对话的窗口");

  console.log(`  process.version   = ${process.version}`);
  console.log(`  process.platform  = ${process.platform}`);
  console.log(`  process.cwd()     = ${process.cwd()}`);
  const extraArgs = process.argv.slice(2);
  console.log(`  argv 额外参数     = [${extraArgs.join(", ") || "无（node code.ts 后面可以加参数）"}]`);

  const apiKey = process.env.ANTHROPIC_API_KEY;
  console.log(`  ANTHROPIC_API_KEY = ${apiKey ? `${Color.SUCCESS}已配置（值保密，不打印）${Color.RESET}` : `${Color.DIM}未配置${Color.RESET}`}`);
  print_key_point("process.env 是 Agent 拿到 API Key 的地方（.env → 环境变量 → process.env）。\n    敏感信息永不写进代码或日志——这是工程红线。");

  // ═══════════════════════════════════════════════════════════
  // 第 2 步: Buffer — 二进制数据的地基
  // ═══════════════════════════════════════════════════════════
  print_step(2, "Buffer — Node 处理二进制数据的地基");

  const buf = Buffer.from("你好，TypeScript", "utf8");
  console.log(`  原文: 你好，TypeScript`);
  console.log(`  UTF-8 字节数: ${buf.length}（汉字 3 字节/个，英文 1 字节/个）`);
  const b64 = buf.toString("base64");
  console.log(`  base64 编码: ${b64}`);
  console.log(`  解码回来: ${Buffer.from(b64, "base64").toString("utf8")}`);
  print_note("文件读写、网络传输的底层全是 Buffer（字节数组）。");
  print_note("事件循环 s04 已经玩过：同步 → 微任务 → 宏任务，Node 靠它单线程跑出高并发。");

  // ═══════════════════════════════════════════════════════════
  // 第 3 步: child_process — 在代码里跑别的程序
  // ═══════════════════════════════════════════════════════════
  print_step(3, "child_process — 在代码里跑别的程序");

  const r = spawnSync(process.execPath, ["-e", "console.log('我是子进程的输出')"], { encoding: "utf8" });
  console.log(`  子进程 stdout: ${r.stdout.trim()}`);
  print_note("Agent 的 Bash 工具本质就是 spawn 一个 shell 执行命令（完整版 s11 展开）。");

  // ═══════════════════════════════════════════════════════════
  // 第 4 步: 最小 HTTP 服务器
  // ═══════════════════════════════════════════════════════════
  print_step(4, "最小 HTTP 服务器 — 十几行跑起一个服务");

  // createServer 的回调就是"请求处理器"：每个请求进来都调它
  const server = createServer((req, res) => {
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ hello: "world", url: req.url }));
  });

  // 端口 0 = 让操作系统随机分配，演示不怕端口冲突
  await new Promise<void>((resolve) => server.listen(0, resolve));
  const addr = server.address();
  const port = typeof addr === "object" && addr !== null ? addr.port : 0;
  print_note(`服务器已启动，监听随机端口 ${port}`);

  // 用 fetch 自请求（Node 18+ 自带 fetch）
  const resp = await fetch(`http://127.0.0.1:${port}/test?x=1`);
  const body = (await resp.json()) as { hello: string; url: string };
  console.log(`  GET /test → ${JSON.stringify(body)}`);

  server.close();   // 演示完立刻关闭，不留悬挂进程
  print_note("服务器已关闭。");
  print_key_point("createServer + listen = 服务器的最小内核：\n    回调函数处理每个请求，端口 0 随机分配，演示完 close 收尾。\n    s16 会把这个内核扩展成完整的 REST API。");

  console.log();
  print_key_point("process、Buffer、子进程、HTTP 内核——运行时底座摸了一遍。\n    下一章：npm / pnpm——把别人的代码装进自己的项目。");
}

await demo_all();
