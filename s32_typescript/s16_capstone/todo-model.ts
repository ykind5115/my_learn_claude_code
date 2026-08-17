/**
 * s16 实战：todo-model.ts — 领域模型与请求体校验
 *
 * 知识点对照：
 *   - interface 描述形状（s02）
 *   - unknown → 类型守卫式校验（s01/s03）：外部数据先验再收
 *   - 业务失败抛 HttpError（s10 的选择标准）
 */

import { badRequest } from "./errors.ts";

export interface Todo {
  id: number;
  title: string;
  done: boolean;
  createdAt: string;
  doneAt: string | null;
}

export interface CreateTodoInput {
  title: string;
}

export interface PatchTodoInput {
  title?: string;
  done?: boolean;
}

/** 校验 POST /todos 的请求体（body 是 JSON.parse 的产物，类型 unknown） */
export function parseCreateBody(body: unknown): CreateTodoInput {
  const obj = ensureObject(body);
  const title = obj.title;
  if (typeof title !== "string" || title.trim() === "") {
    throw badRequest("title 必须是非空字符串");
  }
  return { title: title.trim() };
}

/** 校验 PATCH /todos/:id 的请求体（title 和 done 至少给一个） */
export function parsePatchBody(body: unknown): PatchTodoInput {
  const obj = ensureObject(body);
  const patch: PatchTodoInput = {};

  if ("title" in obj) {
    if (typeof obj.title !== "string" || obj.title.trim() === "") {
      throw badRequest("title 必须是非空字符串");
    }
    patch.title = obj.title.trim();
  }
  if ("done" in obj) {
    if (typeof obj.done !== "boolean") {
      throw badRequest("done 必须是布尔值");
    }
    patch.done = obj.done;
  }
  if (patch.title === undefined && patch.done === undefined) {
    throw badRequest("至少提供一个要修改的字段（title 或 done）");
  }
  return patch;
}

/** 把 unknown 收窄成「记录对象」——校验的第一道门 */
function ensureObject(body: unknown): Record<string, unknown> {
  if (typeof body !== "object" || body === null || Array.isArray(body)) {
    throw badRequest("请求体必须是 JSON 对象");
  }
  return body as Record<string, unknown>;
}
