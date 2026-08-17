/**
 * s16 实战：server.ts — HTTP 服务器核心（手写路由 + JSON 解析）
 *
 * 知识点对照：
 *   - createServer + listen（s06 的最小内核，这里长成完整版）
 *   - URL/路由解析、判别式方法分发
 *   - 请求体读取：async 迭代（s04/s11 的 for await）
 *   - 错误分层：业务错误 HttpError → 400/404，未知错误 → 500（s10）
 */

import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { HttpError, notFound } from "./errors.ts";
import { parseCreateBody, parsePatchBody } from "./todo-model.ts";
import type { Todo } from "./todo-model.ts";
import { loadTodos, saveTodos } from "./todo-store.ts";

export function createTodoServer() {
  return createServer(async (req, res) => {
    try {
      await handleRequest(req, res);
    } catch (e) {
      if (e instanceof HttpError) {
        sendJson(res, e.statusCode, { error: e.message });
      } else {
        console.error("内部错误:", e);
        sendJson(res, 500, { error: "服务器内部错误" });
      }
    }
  });
}

async function handleRequest(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");
  const method = req.method ?? "GET";
  const path = url.pathname;

  // 健康检查（也方便 --serve 模式验证服务器活着）
  if (method === "GET" && path === "/health") {
    sendJson(res, 200, { status: "ok", time: new Date().toISOString() });
    return;
  }

  // 集合路由：GET 列表 / POST 创建
  if (path === "/todos") {
    if (method === "GET") {
      const todos = await loadTodos();
      sendJson(res, 200, todos);
      return;
    }
    if (method === "POST") {
      const body = await readJsonBody(req);
      const input = parseCreateBody(body);      // unknown → 校验 → 精确类型（s03）
      const todos = await loadTodos();
      const nextId = todos.reduce((max, t) => Math.max(max, t.id), 0) + 1;
      const todo: Todo = {
        id: nextId,
        title: input.title,
        done: false,
        createdAt: new Date().toISOString(),
        doneAt: null,
      };
      todos.push(todo);
      await saveTodos(todos);
      sendJson(res, 201, todo);
      return;
    }
  }

  // 单条路由：/todos/:id
  const match = path.match(/^\/todos\/(\d+)$/);
  if (match) {
    const id = Number(match[1]);
    const todos = await loadTodos();
    const idx = todos.findIndex((t) => t.id === id);
    if (idx === -1) throw notFound(`id=${id} 的待办`);

    if (method === "GET") {
      sendJson(res, 200, todos[idx]);
      return;
    }
    if (method === "PATCH") {
      const body = await readJsonBody(req);
      const patch = parsePatchBody(body);
      if (patch.title !== undefined) todos[idx].title = patch.title;
      if (patch.done !== undefined) {
        todos[idx].done = patch.done;
        todos[idx].doneAt = patch.done ? new Date().toISOString() : null;
      }
      await saveTodos(todos);
      sendJson(res, 200, todos[idx]);
      return;
    }
    if (method === "DELETE") {
      const [removed] = todos.splice(idx, 1);
      await saveTodos(todos);
      sendJson(res, 200, { deleted: removed });
      return;
    }
  }

  // 走到这里：路由存在但方法不支持，或路径不存在
  if (path.startsWith("/todos")) {
    throw new HttpError(405, `不支持的请求方法: ${method}`);
  }
  throw notFound(`路径 ${path}`);
}

/** 读取并解析 JSON 请求体（body 是流——for await 分块读） */
async function readJsonBody(req: IncomingMessage): Promise<unknown> {
  let raw = "";
  for await (const chunk of req) {
    raw += chunk;
  }
  if (raw === "") return null;
  try {
    return JSON.parse(raw) as unknown;
  } catch {
    throw new HttpError(400, "请求体不是合法的 JSON");
  }
}

/** 统一 JSON 响应 */
function sendJson(res: ServerResponse, statusCode: number, data: unknown): void {
  res.writeHead(statusCode, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(data));
}
