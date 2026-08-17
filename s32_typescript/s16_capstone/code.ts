/**
 * s32-16: 综合实战 — 用 TypeScript + Node.js 独立写一个 HTTP API
 *
 * ═══════════════════════════════════════════════════════════════
 * 学完本章你应该能回答：
 *   - 一个 REST API 的完整结构：路由 → 校验 → 存取 → 错误映射
 *   - 如何把前面 15 章的知识组装成一个真实应用？
 * ═══════════════════════════════════════════════════════════════
 *
 * 启动方式:
 *     演示模式（自动跑一遍全部端点，推荐先跑这个）:
 *         node s32_typescript/s16_capstone/code.ts
 *
 *     真实服务器模式（手动 curl / 浏览器玩）:
 *         node s32_typescript/s16_capstone/code.ts --serve 3000
 *
 * 文件分工:
 *     code.ts       入口：演示模式 / --serve 模式
 *     server.ts     HTTP 服务器 + 路由 + 请求体解析
 *     todo-model.ts 领域模型 + 请求体校验
 *     todo-store.ts JSON 文件持久化
 *     errors.ts     HttpError + 错误响应
 */

import { rm } from "node:fs/promises";
import { join } from "node:path";
import { Color, print_step, print_note, print_key_point, print_section } from "../utils.ts";
import { createTodoServer } from "./server.ts";

// ── 手写 argv 解析（5 行；生产项目会用 commander 这类库）────────
const args = process.argv.slice(2);
const serveIdx = args.indexOf("--serve");
const servePort = serveIdx !== -1 ? Number(args[serveIdx + 1] ?? 3000) : null;

async function main(): Promise<void> {
  print_section("s32-16: 综合实战 — HTTP API 服务器");

  if (servePort !== null) {
    await runServerMode(servePort);
    return;
  }
  await runDemoMode();
}

/** --serve 模式：真实服务器，Ctrl+C 退出 */
async function runServerMode(port: number): Promise<void> {
  const server = createTodoServer();
  await new Promise<void>((resolve) => server.listen(port, resolve));
  console.log(`  ${Color.SUCCESS}🚀 服务器已启动${Color.RESET}`);
  console.log();
  console.log(`  ${Color.BOLD}API 端点:${Color.RESET}`);
  console.log(`    GET    http://localhost:${port}/health     健康检查`);
  console.log(`    GET    http://localhost:${port}/todos      列出全部`);
  console.log(`    POST   http://localhost:${port}/todos      创建（body: {"title":"..."}）`);
  console.log(`    GET    http://localhost:${port}/todos/:id  查看单条`);
  console.log(`    PATCH  http://localhost:${port}/todos/:id  修改（body: {"done":true}）`);
  console.log(`    DELETE http://localhost:${port}/todos/:id  删除`);
  console.log();
  console.log(`  ${Color.DIM}数据保存在 s16_capstone/data/todos.json，重启不丢。Ctrl+C 退出。${Color.RESET}`);
  console.log();
  console.log(`  ${Color.DIM}试试: curl http://localhost:${port}/todos${Color.RESET}`);
}

/** 演示模式：随机端口起服务器 → fetch 遍历全部端点 → 关闭清理 */
async function runDemoMode(): Promise<void> {
  print_step(0, "先看文件分工（模块拆分本身就是教学内容）");
  console.log(`  code.ts        → 入口：演示 / --serve 两种模式`);
  console.log(`  server.ts      → HTTP 服务器 + 路由 + 请求体解析（s06 内核的完整版）`);
  console.log(`  todo-model.ts  → Todo 类型 + unknown 校验（s02/s03）`);
  console.log(`  todo-store.ts  → JSON 持久化（s11 fs/promises）`);
  console.log(`  errors.ts      → HttpError 分层（s10）`);

  // 端口 0 = 随机分配，演示不打架
  const server = createTodoServer();
  await new Promise<void>((resolve) => server.listen(0, resolve));
  const addr = server.address();
  const port = typeof addr === "object" && addr !== null ? addr.port : 0;
  const base = `http://127.0.0.1:${port}`;
  print_note(`服务器已启动，随机端口 ${port}`);

  // 把每个请求封装成可打印的一步（rawBody 用于发送「非法 JSON」这类原始文本）
  let stepNum = 0;
  const api = async (
    label: string,
    method: string,
    path: string,
    body?: unknown,
    rawBody?: string,
  ): Promise<Response> => {
    stepNum += 1;
    print_step(stepNum, label);
    const resp = await fetch(`${base}${path}`, {
      method,
      headers: body !== undefined || rawBody !== undefined ? { "Content-Type": "application/json" } : undefined,
      body: rawBody ?? (body !== undefined ? JSON.stringify(body) : undefined),
    });
    const json = await resp.json() as unknown;
    const statusColor = resp.status < 400 ? Color.SUCCESS : Color.WARNING;
    console.log(`  ${method} ${path} → ${statusColor}${resp.status}${Color.RESET}`);
    console.log(`  响应: ${JSON.stringify(json)}`);
    return resp;
  };

  // ── 全端点自测 ──────────────────────────────────────────────
  await api("健康检查", "GET", "/health");
  await api("创建待办 #1", "POST", "/todos", { title: "学 TypeScript" });
  await api("创建待办 #2", "POST", "/todos", { title: "学 Node.js" });
  await api("列出全部（应看到 2 条）", "GET", "/todos");
  await api("标记 #1 完成", "PATCH", "/todos/1", { done: true });
  await api("修改 #2 标题", "PATCH", "/todos/2", { title: "学 Node.js 文件系统" });
  await api("查看单条 #1", "GET", "/todos/1");
  await api("删除 #2", "DELETE", "/todos/2");
  await api("列出全部（应只剩 1 条）", "GET", "/todos");

  // ── 错误路径自测 ────────────────────────────────────────────
  await api("错误路径：title 为空", "POST", "/todos", { title: "   " });
  await api("错误路径：body 不是对象", "POST", "/todos", ["数组不是对象"]);
  await api("错误路径：id 不存在", "GET", "/todos/999");
  await api("错误路径：未知路径", "GET", "/nope");
  await api("错误路径：非法 JSON", "POST", "/todos", undefined, "{{{ 这不是 JSON");

  // ── 重启后数据仍在（持久化证明）──────────────────────────────
  print_step(++stepNum, "重启服务器 — 数据还在吗？");
  server.close();
  const server2 = createTodoServer();
  await new Promise<void>((resolve) => server2.listen(0, resolve));
  const addr2 = server2.address();
  const port2 = typeof addr2 === "object" && addr2 !== null ? addr2.port : 0;
  const resp = await fetch(`http://127.0.0.1:${port2}/todos`);
  const afterRestart = (await resp.json()) as unknown[];
  console.log(`  重启后 GET /todos → ${JSON.stringify(afterRestart)}`);
  console.log(`  ${Color.SUCCESS}✅ 数据在 data/todos.json 里，重启不丢${Color.RESET}`);
  server2.close();

  // ── 清理演示数据（--serve 模式才会保留你的真实数据）──────────
  await rm(join(import.meta.dirname, "data"), { recursive: true, force: true });
  print_note("演示数据已清理（演示模式自动清空；--serve 模式保存你的数据）。");

  print_key_point("恭喜！你独立写出了一个完整的 HTTP API：\n    类型设计（s02/s03）→ 校验（s03）→ 持久化（s11）→ 错误分层（s10）→ 模块拆分（s05）。\n    再用 --serve 模式跑起来，这就是一个可以对外服务的应用。");
}

await main();
