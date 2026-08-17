/**
 * s32-15: 类型体操 — 把类型系统当编程语言玩
 *
 * ═══════════════════════════════════════════════════════════════
 * 学完本章你应该能回答：
 *   - 「类型体操」是什么？它有什么实际价值？
 *   - 递归条件类型怎么写？元组长度怎么当数字用？
 *   - 怎么用 @ts-expect-error 当类型层的「测试框架」？
 * ═══════════════════════════════════════════════════════════════
 *
 * 启动方式:
 *     node s32_typescript/s15_type_gymnastics/code.ts
 *     （类型体操发生在编译期——真正的验证请配合 npm run typecheck）
 */

import { Color, print_step, print_note, print_key_point, print_section } from "../utils.ts";

// ── 类型层定义（全部在编译期擦除）─────────────────────────────

// 体操 1：DeepReadonly —— 递归把对象所有层变只读
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};

// 体操 2：类型版加法 —— 元组长度就是数字
type BuildTuple<N extends number, Acc extends unknown[] = []> =
  Acc["length"] extends N ? Acc : BuildTuple<N, [...Acc, unknown]>;
type Add<A extends number, B extends number> = [...BuildTuple<A>, ...BuildTuple<B>]["length"];

// 体操 3：模板字面量类型 —— 字符串也能被类型系统解析
type EventName<T extends string> = `${T}Changed`;

// 体操 4：Flatten —— 递归剥掉嵌套数组
type Flatten<T> = T extends readonly (infer E)[] ? Flatten<E> : T;

// 体操 5：Equal —— 严格相等断言（体操界的「测试框架」）
type Equal<X, Y> =
  (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;

interface Config {
  server: { host: string; port: number };
  retries: number;
}

function demo_all(): void {
  print_section("s32-15: 类型体操");

  // ═══════════════════════════════════════════════════════════
  // 第 1 步: 类型体操是什么
  // ═══════════════════════════════════════════════════════════
  print_step(1, "类型体操是什么 — 类型系统的图灵完备");

  console.log(`  TS 的类型系统有：条件分支（extends ? :）、递归、循环（映射类型）、`);
  console.log(`  模式匹配（infer）、数据结构（元组/对象）——凑齐了编程语言的要素。`);
  print_note("「类型体操」= 用类型系统解题，代码不产出任何运行时行为。");
  print_key_point("实际价值排序：\n    ① 读懂/写出高质量库的类型（zod、trpc 的核心就是体操）\n    ② 给团队写更强的类型约束，把错误更早拦下\n    ③ 面试题（最不重要）。它是「锦上添花」，不是基础刚需——学不会不影响写应用。");

  // ═══════════════════════════════════════════════════════════
  // 第 2 步: DeepReadonly — 递归条件类型
  // ═══════════════════════════════════════════════════════════
  print_step(2, "DeepReadonly — 递归条件类型");

  const config: DeepReadonly<Config> = {
    server: { host: "localhost", port: 8080 },
    retries: 3,
  };
  console.log(`  初始 config = ${JSON.stringify(config)}`);

  // @ts-expect-error 深度只读：修改内层字段会编译报错（npm run typecheck 验证）
  config.server.host = "prod.example.com";
  console.log(`  运行时其实改动了: ${JSON.stringify(config)}`);

  print_note("看到矛盾了吗：typecheck 报错，node 照跑照改——readonly 只是编译期封条（s00 心智模型）。");
  print_key_point("递归模板：T[K] extends object ? DeepReadonly<T[K]> : T[K]\n    一层套一层，直到叶子。注意 object 判断会把数组/函数也递归——\n    生产级实现要特判（真实库都有一堆边界处理）。");

  // ═══════════════════════════════════════════════════════════
  // 第 3 步: 类型版加法 — 元组长度当数字
  // ═══════════════════════════════════════════════════════════
  print_step(3, "类型版加法 — 元组长度就是数字");

  const sum: Add<3, 4> = 7;
  console.log(`  Add<3, 4> 的答案 = ${sum}（类型层面已算出是 7）`);
  // @ts-expect-error 类型层面 3+4=7，不是 8
  const wrong: Add<3, 4> = 8;
  console.log(`  被 @ts-expect-error 拦下的错误答案: ${wrong}`);

  print_key_point("两步：\n    ① BuildTuple<N> 递归造出长度为 N 的元组（Acc['length'] extends N 是递归出口）\n    ② 两个元组拼接后的 length 就是和。\n    数字→元组→拼→长度，这是类型体操最经典的编码技巧。");

  // ═══════════════════════════════════════════════════════════
  // 第 4 步: 模板字面量类型 — 字符串解析
  // ═══════════════════════════════════════════════════════════
  print_step(4, "模板字面量类型 — 字符串也能被类型系统解析");

  const evt: EventName<"volume"> = "volumeChanged";
  console.log(`  EventName<"volume"> 推导出的字符串 = "${evt}"`);
  // @ts-expect-error 必须是 "volumeChanged"，别的字符串不行
  const badEvt: EventName<"volume"> = "volumeDidChange";
  console.log(`  被拦下的错误字符串: "${badEvt}"`);

  print_note("EventName<T> = `${T}Changed` —— 类型系统把字符串拼出来再当约束。");
  print_note("更狠的用法：infer 反向解析 `Hello, ${infer Name}`，从字符串里提取类型。");

  // ═══════════════════════════════════════════════════════════
  // 第 5 步: Flatten + Equal — 递归与断言
  // ═══════════════════════════════════════════════════════════
  print_step(5, "Flatten + Equal — 递归剥壳与相等断言");

  const flat: Flatten<number[][][]> = 42;
  console.log(`  Flatten<number[][][]> 剥三层壳后 = ${flat}（类型是 number）`);

  const eqTrue: Equal<Add<1, 2>, 3> = true;
  console.log(`  Equal<Add<1, 2>, 3> = ${eqTrue}`);
  // @ts-expect-error Add<1,2> 是 3，不等于 4
  const eqFalse: Equal<Add<1, 2>, 4> = true;
  console.log(`  被拦下的错误断言: ${eqFalse}`);

  print_key_point("Equal<X, Y> 是体操界的「测试框架」：\n    写断言 + npm run typecheck = 类型层的单元测试。\n    @ts-expect-error = 断言「这里必须报错」——本章每个结论都靠它验证。");

  // ═══════════════════════════════════════════════════════════
  // 第 6 步: 体操的边界 — 什么时候别用
  // ═══════════════════════════════════════════════════════════
  print_step(6, "体操的边界 — 什么时候别用");

  console.log(`  ① 递归深度有限（几百层就到顶，BuildTuple<1000> 会爆）`);
  console.log(`  ② 编译变慢：每个体操都是编译器要跑的程序`);
  console.log(`  ③ 可读性换来的收益要划算——写代码是给人看的`);
  print_key_point("体操是库作者的利器、业务代码的奢侈品：\n    库的核心类型可以雕琢到极致，业务代码里简单清晰的类型最值钱。\n    看完本章，读 .d.ts 不再怕——这就是最大的收获。");

  console.log();
  print_key_point("DeepReadonly、类型加法、模板字面量、Equal 断言——体操五连通关。\n    下一章（最后一章）：s16 综合实战——用 TS + Node 独立写一个 HTTP API。");
}

demo_all();
