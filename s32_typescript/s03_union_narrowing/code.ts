/**
 * s32-03: union / narrowing — 一个变量多种类型，如何安全收窄
 *
 * ═══════════════════════════════════════════════════════════════
 * 学完本章你应该能回答：
 *   - union 类型解决什么问题？
 *   - narrowing 有哪些手段？各自适用什么场景？
 *   - 什么是判别联合（discriminated union）？never 如何做穷尽检查？
 * ═══════════════════════════════════════════════════════════════
 *
 * 启动方式:
 *     node s32_typescript/s03_union_narrowing/code.ts
 */

import { Color, print_step, print_note, print_key_point, print_section } from "../utils.ts";

// ── 供各步演示使用的类型定义 ──────────────────────────────────

// union：一个变量可以是这几种类型之一
type Id = string | number;

// 判别联合：每个成员带一个字面量"标签字段"（status），用来区分彼此
type ApiResponse =
  | { status: "success"; data: string[] }
  | { status: "error"; code: number; message: string };

// 类型守卫（type guard）：一个返回 boolean 的"验证函数"，true 时 TS 就知道 x 是 ApiResponse
function isApiResponse(x: unknown): x is ApiResponse {
  if (typeof x !== "object" || x === null) return false;
  const s = (x as { status?: unknown }).status;
  return s === "success" || s === "error";
}

// never 穷尽检查的哨兵：任何值都赋不进 never
function assertNever(x: never): never {
  throw new Error(`穷尽检查失败：出现了未处理的分支 ${String(x)}`);
}

function demo_all(): void {
  print_section("s32-03: union / narrowing");

  // ═══════════════════════════════════════════════════════════
  // 第 1 步: union — 「或」类型
  // ═══════════════════════════════════════════════════════════
  print_step(1, "union — 一个变量可以是多种类型之一");

  const id1: Id = "user-abc";   // 字符串
  const id2: Id = 42;           // 数字
  console.log(`  id1 = "${id1}", id2 = ${id2} —— 同一个 Id 类型装下了两种值`);

  // 但直接访问 union 的成员很危险：TS 只允许访问「所有成员共有」的属性和方法
  // id1.toUpperCase();  // ← 编译错误：number 没有 toUpperCase
  print_key_point("union = 「或」。变量类型变成「string 或 number」后，\n    能安全调用的只剩两者共有的能力——想用独有能力，必须先收窄。");

  // ═══════════════════════════════════════════════════════════
  // 第 2 步: typeof narrowing
  // ═══════════════════════════════════════════════════════════
  print_step(2, "typeof 收窄 — 用运行时类型判断区分分支");

  function formatValue(v: string | number | boolean): string {
    if (typeof v === "string") return `字符串 "${v}"`;
    if (typeof v === "number") return `数字 ${v.toFixed(2)}`;  // 这里 v 已收窄为 number
    return `布尔 ${v ? "真" : "假"}`;                          // 剩下只有 boolean
  }

  console.log(`  formatValue("hi")   → ${formatValue("hi")}`);
  console.log(`  formatValue(3.14159) → ${formatValue(3.14159)}`);
  console.log(`  formatValue(true)   → ${formatValue(true)}`);
  print_key_point("typeof 检查之后，该分支里变量的类型自动变窄。\n    这叫 control flow analysis（控制流分析）——TS 跟着 if 走。");

  // ═══════════════════════════════════════════════════════════
  // 第 3 步: in 收窄 — 用属性存在性区分对象
  // ═══════════════════════════════════════════════════════════
  print_step(3, "in 收窄 — 用「有没有这个属性」区分对象");

  type Bird = { fly: () => string; wingspan: number };
  type Fish = { swim: () => string; depth: number };

  function move(animal: Bird | Fish): string {
    if ("fly" in animal) {
      return `翅膀 ${animal.wingspan}cm：${animal.fly()}`;  // 收窄为 Bird
    }
    return `水深 ${animal.depth}m：${animal.swim()}`;        // 收窄为 Fish
  }

  const eagle: Bird = { fly: () => "展翅高飞", wingspan: 200 };
  const tuna: Fish = { swim: () => "深潜觅食", depth: 800 };

  console.log(`  move(eagle) → ${move(eagle)}`);
  console.log(`  move(tuna)  → ${move(tuna)}`);
  print_note("typeof 区分基本类型，in 区分对象形状——两种最常用的收窄手段。");

  // ═══════════════════════════════════════════════════════════
  // 第 4 步: 判别联合 + 穷尽检查
  // ═══════════════════════════════════════════════════════════
  print_step(4, "判别联合 + never 穷尽检查 — 工业级写法");

  function handle(r: ApiResponse): string {
    switch (r.status) {                    // status 就是"判别字段"
      case "success":
        return `✅ 成功：${r.data.length} 条数据 [${r.data.join(", ")}]`;  // 自动收窄
      case "error":
        return `❌ 失败(${r.code})：${r.message}`;                          // 自动收窄
      default:
        // 走到这里说明 r.status 的类型是 never——即「不可能发生」
        // 若有人以后给 ApiResponse 加了第三种情况，这一行会编译报错！
        return assertNever(r);
    }
  }

  const ok: ApiResponse = { status: "success", data: ["苹果", "香蕉"] };
  const err: ApiResponse = { status: "error", code: 500, message: "服务器开小差了" };

  console.log(`  handle(ok)  → ${handle(ok)}`);
  console.log(`  handle(err) → ${handle(err)}`);
  print_key_point("判别联合 = 每个成员带一个字面量标签字段的 union。\n    switch 标签 + never 兜底 = 编译器帮你保证「所有情况都处理了」。\n    以后加了新成员漏了处理，编译期直接报错——这就是穷尽检查。");

  // ═══════════════════════════════════════════════════════════
  // 第 5 步: 类型守卫 — 收窄从 unknown 开始
  // ═══════════════════════════════════════════════════════════
  print_step(5, "类型守卫（type guard）— 从 unknown 到精确类型的安全通道");

  // 模拟"从外部世界"收到的数据（API 响应、用户输入）——类型未知
  const rawInputs: unknown[] = [
    { status: "success", data: ["外部数据"] },
    { status: "error", code: 404, message: "找不到资源" },
    "这根本不是对象",                      // 混进来的脏数据
    { status: "weird", whatever: true },   // 伪造的 status
  ];

  for (const raw of rawInputs) {
    if (isApiResponse(raw)) {
      console.log(`  ${Color.GREEN}√ 通过守卫:${Color.RESET} ${handle(raw)}`);
    } else {
      console.log(`  ${Color.WARNING}× 拒绝脏数据:${Color.RESET} ${JSON.stringify(raw)}`);
    }
  }
  print_key_point("`x is ApiResponse` 是 TS 最强大的收窄签名之一：\n    函数返回 true 时，TS 相信你的判断并把 x 收窄。\n    unknown → 守卫 → 精确类型，这就是 Claude Code 处理 API 响应的日常。");

  console.log();
  print_key_point("union 表达「或」，narrowing 把「或」变回「具体」：\n    typeof 分基本类型，in 分对象形状，判别字段 + never 做穷尽检查。\n    下一章：async / await / Promise——异步世界的三件套。");
}

demo_all();
