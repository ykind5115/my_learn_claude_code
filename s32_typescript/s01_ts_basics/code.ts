/**
 * s32-01: TypeScript 基础语法 — 给数据贴上第一个标签
 *
 * ═══════════════════════════════════════════════════════════════
 * 学完本章你应该能回答：
 *   - 类型标注和类型推断有什么区别？各适合什么场景？
 *   - any 和 unknown 有什么不同？为什么尽量别用 any？
 *   - 为什么类型错误挡不住 node 运行代码？
 * ═══════════════════════════════════════════════════════════════
 *
 * 启动方式:
 *     node s32_typescript/s01_ts_basics/code.ts
 */

import { Color, print_step, print_note, print_key_point, print_section } from "../utils.ts";

function demo_all(): void {
  print_section("s32-01: TypeScript 基础语法");

  // ═══════════════════════════════════════════════════════════
  // 第 1 步: 类型标注 vs 类型推断
  // ═══════════════════════════════════════════════════════════
  print_step(1, "类型标注 vs 类型推断 — 标签可以手写，也可以自动贴");

  // 显式标注：自己写标签
  const name: string = "小明";
  const age: number = 18;

  // 类型推断：不写标签，TS 从值猜出来
  const inferredName = "小红";   // 推断为 string
  const inferredAge = 20;        // 推断为 number

  console.log(`  标注:   name=${name} (${typeof name}), age=${age} (${typeof age})`);
  console.log(`  推断:   inferredName=${inferredName} (${typeof inferredName}), inferredAge=${inferredAge} (${typeof inferredAge})`);
  print_note("两个写法的运行时行为完全一样——标签不改变值。");
  print_key_point("能推断的就不写（省事），推断不出来或想表达意图的才写。\n    函数参数、对象形状通常显式标注；简单变量交给推断。");

  // ═══════════════════════════════════════════════════════════
  // 第 2 步: 基本类型全家福
  // ═══════════════════════════════════════════════════════════
  print_step(2, "基本类型全家福 — 标签都有哪些款式");

  const isStudent: boolean = true;
  const score: number = 99.5;          // 整数和小数都是 number
  const nothing: null = null;          // 空
  const notSet: undefined = undefined; // 未定义
  const big: bigint = 9007199254740993n; // 超大整数（n 结尾）
  const sym: symbol = Symbol("id");    // 唯一标识

  console.log(`  boolean=${isStudent}, number=${score}, bigint=${big}`);
  console.log(`  null=${nothing}, undefined=${notSet}, symbol=${String(sym)}`);
  print_key_point("string/number/boolean/bigint/symbol/null/undefined ——\n    7 种基本类型，其中 null/undefined 通常靠 strictNullChecks 参与检查（本模块 tsconfig 开了 strict）。");

  // ═══════════════════════════════════════════════════════════
  // 第 3 步: 数组 / 元组 / as const
  // ═══════════════════════════════════════════════════════════
  print_step(3, "数组 / 元组 / as const — 三种容器标签");

  const nums: number[] = [1, 2, 3];            // 数组：元素同类型
  const pair: [string, number] = ["age", 18];  // 元组：长度和每个位置类型都固定
  const status = { code: 200, text: "OK" } as const;  // as const：值变成字面量类型

  console.log(`  数组: [${nums.join(", ")}]`);
  console.log(`  元组: pair = ["${pair[0]}", ${pair[1]}]`);
  console.log(`  as const: status = ${JSON.stringify(status)}`);
  print_note("as const 之后，status.code 的类型是字面量 200（不是 number），\n    且属性全部变只读——想改 status.code 会被 tsc 拦下。");

  // ═══════════════════════════════════════════════════════════
  // 第 4 步: any vs unknown
  // ═══════════════════════════════════════════════════════════
  print_step(4, "any vs unknown — 逃课生 vs 转学生");

  // any：告诉质检员"别查我"，任何操作都放行
  const danger: any = 123;
  try {
    // 编译期：完全放行。运行时：123.toUpperCase 不存在 → 崩溃
    const boom = danger.toUpperCase();
    console.log(`  这行不会执行: ${boom}`);
  } catch (e) {
    console.log(`  ${Color.WARNING}any 的运行时崩溃: ${(e as Error).message}${Color.RESET}`);
  }
  print_note("any 编译期不报错，运行时爆炸——类型安全网形同虚设。");

  // unknown：安全版——用之前必须先确认类型
  const mystery: unknown = "可能是任何东西";
  // mystery.toUpperCase();  // ← 编译错误：unknown 上不能直接调用方法
  if (typeof mystery === "string") {
    console.log(`  unknown 收窄后安全使用: ${mystery.toUpperCase()}`);
  }
  print_key_point("unknown = 带检查的 any。收到外部数据（API 响应、用户输入）用 unknown，\n    确认类型后再用——Claude Code 处理 API 响应就是这套思路。");

  // ═══════════════════════════════════════════════════════════
  // 第 5 步: @ts-expect-error — 编译期 vs 运行时的分界线
  // ═══════════════════════════════════════════════════════════
  print_step(5, "@ts-expect-error — 类型错误只挡编译期，挡不住运行时");

  // @ts-expect-error 下一行有类型错误 —— 质检员在 typecheck 时知道这里"预期有错"
  const wrong: number = "这不是数字";

  console.log(`  wrong 运行时实际值: "${wrong}" (typeof=${typeof wrong})`);
  print_note("运行 `npm run typecheck` 时 tsc 会跳过这行（@ts-expect-error 声明的预期错误）。");
  print_key_point("node 直跑照常执行——类型标签被撕掉，运行时没有任何检查。\n    类型错误 = 编译期红灯；运行时错误 = 另一种完全独立的事。");

  // ═══════════════════════════════════════════════════════════
  // 第 6 步: 函数标注
  // ═══════════════════════════════════════════════════════════
  print_step(6, "函数标注 — 给输入和输出都贴上标签");

  function greet(user: { name: string }, times: number = 1): string {
    return `你好，${user.name}！`.repeat(times);
  }

  function sum(...nums: number[]): number {
    return nums.reduce((a, b) => a + b, 0);
  }

  // 可选参数用 ?，调用时可传可不传
  function log(message: string, level?: "info" | "warn"): string {
    return `[${level ?? "info"}] ${message}`;
  }

  console.log(`  greet: ${greet({ name: "小明" })}`);
  console.log(`  greet(times=3): ${greet({ name: "小明" }, 3)}`);
  console.log(`  sum(1,2,3,4,5): ${sum(1, 2, 3, 4, 5)}`);
  console.log(`  log: ${log("启动成功")} / ${log("磁盘快满", "warn")}`);
  print_key_point("参数标注 = 输入契约，返回标注 = 输出契约。\n    函数签名的类型写清楚了，调用方不用看函数体就知道怎么用。");

  // ═══════════════════════════════════════════════════════════
  // 第 7 步: enum 的替代写法（README 会讲 enum 是什么）
  // ═══════════════════════════════════════════════════════════
  print_step(7, "enum 替代写法 — 为什么本模块看不到 enum");

  // enum 是"不可擦除"语法（编译后真的会生成 JS 代码），node 直跑会报错。
  // 现代社区主流替代：as const 对象 + 联合类型
  const TodoStatus = { Pending: "pending", Done: "done" } as const;
  type TodoStatus = (typeof TodoStatus)[keyof typeof TodoStatus];  // "pending" | "done"

  const markDone = (s: TodoStatus): TodoStatus => {
    return s === TodoStatus.Pending ? TodoStatus.Done : TodoStatus.Pending;
  };
  console.log(`  markDone("pending") = "${markDone("pending")}"`);
  print_key_point("const 对象 + as const = enum 的全部好处（类型安全 + 可遍历），\n    还能 node 直跑。这就是「可擦除语法优先」的工程实践。");

  // ═══════════════════════════════════════════════════════════
  // 演示结束
  // ═══════════════════════════════════════════════════════════
  console.log();
  print_key_point("类型标注、推断、any/unknown、@ts-expect-error —— 基础标签贴法齐了。\n    下一章：给对象形状贴标签（interface / type）。");
}

demo_all();
