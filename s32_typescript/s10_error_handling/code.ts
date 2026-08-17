/**
 * s32-10: Error / 异常处理 — 程序摔倒了怎么优雅地站起来
 *
 * ═══════════════════════════════════════════════════════════════
 * 学完本章你应该能回答：
 *   - 自定义错误类为什么要修正 name 和附加上下文？
 *   - 异步错误和不处理 Promise 拒绝（unhandledRejection）各怎么应对？
 *   - throw 和 Result 模式各适合什么场景？
 * ═══════════════════════════════════════════════════════════════
 *
 * 启动方式:
 *     node s32_typescript/s10_error_handling/code.ts
 */

import { Color, print_step, print_note, print_key_point, print_section } from "../utils.ts";

// ── 演示用定义 ──────────────────────────────────────────────

// 自定义错误类：附加上下文（状态码），修正 name
class ApiError extends Error {
  readonly statusCode: number;
  constructor(statusCode: number, message: string) {
    super(message);
    this.name = "ApiError";   // 不修正的话 instanceof 检查时 name 还是 "Error"
    this.statusCode = statusCode;
  }
}

// 业务错误用 Result（呼应 s08 的泛型接口）
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };

function safeDivide(a: number, b: number): Result<number, string> {
  if (b === 0) return { ok: false, error: "除数不能为 0" };
  return { ok: true, value: a / b };
}

// 深层业务逻辑：抛自定义错误
function fetchUserFromApi(id: number): { name: string } {
  if (id <= 0) throw new ApiError(400, "id 必须是正数");
  if (id > 100) throw new ApiError(404, "用户不存在");
  return { name: `用户${id}` };
}

// 异步函数：throw 会变成 reject
async function fetchUserAsync(id: number): Promise<{ name: string }> {
  await new Promise((r) => setTimeout(r, 30));   // 模拟网络延迟
  return fetchUserFromApi(id);
}

const sleep = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

async function demo_all(): Promise<void> {
  print_section("s32-10: Error / 异常处理");

  // ═══════════════════════════════════════════════════════════
  // 第 1 步: throw / try / catch / finally
  // ═══════════════════════════════════════════════════════════
  print_step(1, "throw / try / catch / finally — 基本功");

  console.log(`  内置错误家族: Error（基类）、TypeError（类型错）、RangeError（越界）、SyntaxError（语法错）`);

  try {
    throw new TypeError("这里传错了类型");
  } catch (e) {
    console.log(`  catch 捕获: ${(e as Error).name}: ${(e as Error).message}`);
  } finally {
    console.log(`  finally: 无论成不成，这行都执行（关闭文件/连接的好地方）`);
  }
  print_key_point("throw 抛出 → 调用栈逐层往上找 catch → 找到就接住，找不到进程崩溃。\n    finally 用于清理资源——文件句柄、数据库连接都靠它善后。");

  // ═══════════════════════════════════════════════════════════
  // 第 2 步: 自定义错误类 — 带上下文的错误
  // ═══════════════════════════════════════════════════════════
  print_step(2, "自定义错误类 — 错误也要带上下文");

  for (const id of [42, 0, 999]) {
    try {
      const user = fetchUserFromApi(id);
      console.log(`  ${Color.SUCCESS}√ id=${id}:${Color.RESET} ${user.name}`);
    } catch (e) {
      if (e instanceof ApiError) {
        console.log(`  ${Color.WARNING}× id=${id}:${Color.RESET} [${e.name} ${e.statusCode}] ${e.message}`);
      } else {
        console.log(`  ${Color.ERROR}× id=${id}:${Color.RESET} 未知错误: ${(e as Error).message}`);
      }
    }
  }
  print_key_point("自定义错误类 = 继承 Error + 修正 name + 附加字段（statusCode 等）。\n    instanceof 判断错误种类，字段携带排查线索——错误从「一句话」变成「一份档案」。");

  // ═══════════════════════════════════════════════════════════
  // 第 3 步: 异步错误
  // ═══════════════════════════════════════════════════════════
  print_step(3, "异步错误 — async 里的 throw 变成 reject");

  try {
    await fetchUserAsync(-5);
  } catch (e) {
    if (e instanceof ApiError) {
      console.log(`  await + try/catch: [${e.statusCode}] ${e.message}`);
    }
  }

  // 经典坑：忘了 await，错误没人接
  const dangling = fetchUserAsync(-6);
  dangling.catch((e) => {
    console.log(`  忘了 await 的 Promise: 靠 .catch 补救 → ${(e as Error).message}`);
  });
  await sleep(80);
  print_key_point("async 函数里的 throw = 返回一个 rejected Promise。\n    接住它只有两条路：await + try/catch，或者 .catch。\n    忘了 await 的错误会静默丢失——这是异步 bug 的头号来源。");

  // ═══════════════════════════════════════════════════════════
  // 第 4 步: unhandledRejection — 完全没人接的拒绝
  // ═══════════════════════════════════════════════════════════
  print_step(4, "unhandledRejection — 完全没人接的拒绝");

  // 挂一个临时全局监听器，看 Node 怎么把「漏网的拒绝」交给你
  const onUnhandled = (reason: unknown) => {
    console.log(`  ${Color.ERROR}unhandledRejection 捕获:${Color.RESET} ${(reason as Error).message}`);
  };
  process.on("unhandledRejection", onUnhandled);
  void Promise.reject(new Error("没人 await 也没人 .catch 的拒绝"));
  await sleep(80);
  process.removeListener("unhandledRejection", onUnhandled);
  print_key_point("没有监听器时，unhandledRejection 直接让进程以非 0 码退出（Node 15+）。\n    真实工程常挂全局监听：记录日志、上报监控、决定是否优雅关闭。\n    Agent 系统的错误恢复（s11_error_recovery）就是在这种边界上工作的。");

  // ═══════════════════════════════════════════════════════════
  // 第 5 步: Result 模式 vs throw
  // ═══════════════════════════════════════════════════════════
  print_step(5, "Result 模式 vs throw — 两条路线怎么选");

  console.log(`  Result 风格：`);
  const r1 = safeDivide(10, 2);
  const r2 = safeDivide(10, 0);
  if (r1.ok) console.log(`    10/2 → ${r1.value}`);
  if (!r2.ok) console.log(`    10/0 → ${r2.error}（不抛异常，正常返回）`);

  console.log(`  throw 风格（同样的除零）：`);
  try {
    const v = divideOrThrow(10, 0);
    console.log(`    ${v}`);
  } catch (e) {
    console.log(`    被 throw: ${(e as Error).message}`);
  }

  print_key_point("选择标准：\n    ① 可预期的业务失败（校验不过、用户不存在）→ Result：调用方必须显式处理，编译期可见\n    ② 预期外的编程错误（逻辑 bug、环境崩坏）→ throw：让错误沿着栈爆炸，留下完整现场\n    混合用法（很多 Agent 框架）：业务错误走 Result，编程错误走 throw。");
}

// throw 风格版本（放这里是为了和 safeDivide 对照）
function divideOrThrow(a: number, b: number): number {
  if (b === 0) throw new RangeError("除数不能为 0");
  return a / b;
}

await demo_all();
print_key_point("try/catch/finally → 自定义错误 → 异步错误 → 全局兜底 → Result 路线图。\n    下一章：文件系统 / subprocess——Agent 工具的文件层。");
