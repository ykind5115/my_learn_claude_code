/**
 * s16 实战：todo-store.ts — JSON 文件持久化
 *
 * 知识点对照：
 *   - fs/promises + path.join + import.meta.dirname（s11 的铁律）
 *   - 数据文件不存在 = 首次运行（ENOENT 友好处理）
 *   - 损坏的 JSON 转成 500（错误处理 s10）
 */

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import type { Todo } from "./todo-model.ts";
import { HttpError } from "./errors.ts";

// 数据文件位置：本文件所在目录下的 data/todos.json
// 用 import.meta.dirname，从任何目录启动服务器都能找到数据
const dataDir = join(import.meta.dirname, "data");
const dataFile = join(dataDir, "todos.json");

export async function loadTodos(): Promise<Todo[]> {
  try {
    const raw = await readFile(dataFile, "utf8");
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      throw new HttpError(500, "数据文件损坏：根节点必须是数组");
    }
    return parsed as Todo[];
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code === "ENOENT") {
      return [];   // 首次运行：没有数据文件 = 空列表
    }
    if (e instanceof HttpError) throw e;
    throw new HttpError(500, "数据文件损坏：无法解析 data/todos.json");
  }
}

export async function saveTodos(todos: Todo[]): Promise<void> {
  await mkdir(dataDir, { recursive: true });
  await writeFile(dataFile, JSON.stringify(todos, null, 2), "utf8");
}
