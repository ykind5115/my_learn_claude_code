/**
 * s32-12: 高级类型 — keyof、条件类型、infer 的进阶玩法
 *
 * ═══════════════════════════════════════════════════════════════
 * 学完本章你应该能回答：
 *   - keyof 和索引访问类型怎么用？
 *   - 条件类型为什么对 union 会「自动分配」？
 *   - infer 提取的是什么？
 *   - Partial/Pick/Record 自己手写出来长什么样？
 * ═══════════════════════════════════════════════════════════════
 *
 * 启动方式:
 *     node s32_typescript/s12_advanced_types/code.ts
 *     （类型层面的结论要配合 npm run typecheck 验证——运行只是演示）
 */

import { Color, print_step, print_note, print_key_point, print_section } from "../utils.ts";

// ── 类型层定义（全部在编译期擦除）─────────────────────────────

interface User { name: string; age: number; email: string }

// keyof + 索引访问：泛型安全取值
function getProp<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// 条件类型：类型层的 if
type IsString<T> = T extends string ? true : false;

// 分布式条件类型：T 是 union 时，逐个判断再拼回 union
type ToArray<T> = T extends unknown ? T[] : never;

// infer：从结构里「提取」子类型
type ReturnTypeOf<T> = T extends (...args: never[]) => infer R ? R : never;
type ElementOf<T> = T extends readonly (infer E)[] ? E : never;

// 手写映射类型：Partial / Pick / Record 的实现
type MyPartial<T> = { [K in keyof T]?: T[K] };
type MyPick<T, K extends keyof T> = { [P in K]: T[P] };
type MyRecord<K extends string | number | symbol, V> = { [P in K]: V };

// 一个返回结构复杂的函数，供 infer 提取
function makeResult(): { code: number; data: string[] } {
  return { code: 200, data: ["a", "b"] };
}

function demo_all(): void {
  print_section("s32-12: 高级类型");

  // ═══════════════════════════════════════════════════════════
  // 第 1 步: keyof + 索引访问
  // ═══════════════════════════════════════════════════════════
  print_step(1, "keyof + 索引访问 — 从形状里取「钥匙」");

  const user: User = { name: "小明", age: 18, email: "ming@x.com" };

  // keyof User = "name" | "age" | "email"
  const keys: Array<keyof User> = ["name", "age", "email"];
  console.log(`  keyof User 的钥匙集合: [${keys.join(", ")}]`);

  // getProp 按钥匙取值，返回类型跟着钥匙变
  const uName = getProp(user, "name");   // string
  const uAge = getProp(user, "age");     // number
  console.log(`  getProp(user, "name") = "${uName}"（返回类型 string）`);
  console.log(`  getProp(user, "age") = ${uAge.toFixed(1)}（返回类型 number，.toFixed 可用）`);
  // getProp(user, "不存在的键")  // ← 编译错误：K 必须属于 keyof User
  print_key_point("keyof 取形状的钥匙集合，索引访问 T[K] 用钥匙取对应类型。\n    两者结合 = 「类型安全的取属性」——这就是 Lodash.get 的类型版。");

  // ═══════════════════════════════════════════════════════════
  // 第 2 步: 条件类型 + 分布式
  // ═══════════════════════════════════════════════════════════
  print_step(2, "条件类型 — 类型层的 if，还会自动分配");

  const isStr1: IsString<"hello"> = true;
  const isStr2: IsString<42> = false;
  console.log(`  IsString<"hello"> = ${isStr1}（true）`);
  console.log(`  IsString<42> = ${isStr2}（false）`);

  // 分布式：union 会被拆开逐个判断，再拼回 union
  const arr1: ToArray<string | number> = ["a", "b"];   // string[] | number[]
  const arr2: ToArray<string | number> = [1, 2];       // 两种都合法
  console.log(`  ToArray<string | number> 允许 [${JSON.stringify(arr1)}] 也允许 [${JSON.stringify(arr2)}]`);
  print_key_point("T extends unknown ? T[] : never —— unknown 恒为真，但「分配」才是重点：\n    string | number 被拆成 string[] | number[] 再拼回。\n    很多内置类型（Exclude/Extract）就是靠分布式条件类型实现的。");

  // ═══════════════════════════════════════════════════════════
  // 第 3 步: infer — 从结构里提取
  // ═══════════════════════════════════════════════════════════
  print_step(3, "infer — 从结构里「挖」出子类型");

  const ret: ReturnTypeOf<typeof makeResult> = { code: 200, data: ["x"] };
  console.log(`  ReturnTypeOf<makeResult> 提取出: ${JSON.stringify(ret)}（code/data 全类型安全）`);

  const usersArr: User[] = [];
  const elem: ElementOf<typeof usersArr> = { name: "提取", age: 1, email: "e@x.com" };
  console.log(`  ElementOf<User[]> 提取出元素类型: ${JSON.stringify(elem)}`);
  print_key_point("infer 只能出现在条件类型的 extends 分支里，意思是「猜出这个位置的类型，\n    猜出来就命名为 R/E 拿来用」。\n    看懂 infer 就读懂了 90% 的复杂 .d.ts。");

  // ═══════════════════════════════════════════════════════════
  // 第 4 步: 手写映射类型
  // ═══════════════════════════════════════════════════════════
  print_step(4, "手写映射类型 — 内置工具的内部实现");

  // MyPartial：所有字段变可选
  const partialUser: MyPartial<User> = { name: "只填一个字段也行" };
  console.log(`  MyPartial<User> 允许部分字段: ${JSON.stringify(partialUser)}`);

  // MyPick：挑字段
  const picked: MyPick<User, "name" | "age"> = { name: "小明", age: 18 };
  console.log(`  MyPick<User, "name" | "age"> = ${JSON.stringify(picked)}`);

  // MyRecord：键值字典
  const dict: MyRecord<string, number> = { a: 1, b: 2 };
  console.log(`  MyRecord<string, number> = ${JSON.stringify(dict)}`);

  print_note("这些「手写版」和内置的 Partial/Pick/Record 行为完全一致——s08 的谜底揭开了。");
  print_key_point("映射类型 = 遍历钥匙集合 + 逐把钥匙定新类型：\n    [K in keyof T] 遍历，后面写每个 K 的新类型。\n    Partial 加 ?，Readonly 加 readonly，Pick 缩小钥匙集合——就这三板斧。");

  // ═══════════════════════════════════════════════════════════
  // 第 5 步: satisfies — 检查形状但不改变推断
  // ═══════════════════════════════════════════════════════════
  print_step(5, "satisfies — 检查形状但不改变推断");

  // satisfies：只校验形状，不改变推断（保留字面量要配 as const）
  const config = {
    host: "localhost",
    port: 8080,
    retry: 3,
  } as const satisfies Record<string, string | number>;

  // config.port 的类型是字面量 8080（若写成 const config: Record<...> 会退化成 number）
  const portLiteral: 8080 = config.port;
  console.log(`  config = ${JSON.stringify(config)}，且 config.port 保留字面量类型 ${portLiteral}`);

  // const bad: Record<string, string> = { port: 8080 };  // ← 编译错误：number 不满足 string
  print_key_point("「标注」会改变推断（port 变 number），「satisfies」只检查不改变。\n    注意：保留字面量类型要写 as const satisfies（单用 satisfies 仍会加宽）。\n    既享受类型检查，又保留字面量精度——现代 TS 的推荐写法。");

  console.log();
  print_key_point("keyof → 条件类型 → infer → 映射类型 → satisfies，高级玩法通关。\n    下一章：Decorator——唯一需要编译的章节（tsc 登场）。");
}

demo_all();
