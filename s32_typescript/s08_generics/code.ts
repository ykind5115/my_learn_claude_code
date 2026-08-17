/**
 * s32-08: 泛型 — 类型也能当参数
 *
 * ═══════════════════════════════════════════════════════════════
 * 学完本章你应该能回答：
 *   - 泛型解决什么问题？为什么不能直接用 any？
 *   - 泛型约束（extends）什么时候用？
 *   - Partial / Pick / Record 这些内置泛型各干什么？
 * ═══════════════════════════════════════════════════════════════
 *
 * 启动方式:
 *     node s32_typescript/s08_generics/code.ts
 */

import { Color, print_step, print_note, print_key_point, print_section } from "../utils.ts";

// ── 演示用定义 ──────────────────────────────────────────────

// 泛型函数：T 是「类型参数」——调用时才知道具体是什么
function identity<T>(value: T): T {
  return value;
}

// 没有泛型的笨办法：any 会丢掉所有类型信息
function identityAny(value: any): any {
  return value;
}

// 泛型约束：T 必须带 id 字段（extends 不是继承，是「至少长这样」）
interface HasId { id: string }
function findById<T extends HasId>(items: T[], id: string): T | undefined {
  return items.find((item) => item.id === id);
}

// 泛型接口：Result 模式（s10 会再见面），E 有默认类型参数
interface Result<T, E = Error> {
  ok: boolean;
  value?: T;
  error?: E;
}
// 成功分支：error 永远不会出现，用 never 表示
function ok<T>(value: T): Result<T, never> {
  return { ok: true, value };
}
function fail<E>(error: E): Result<never, E> {
  return { ok: false, error };
}

// 泛型类：一个装任意东西的盒子
class Box<T> {
  #content: T;
  constructor(content: T) {
    this.#content = content;
  }
  get(): T {
    return this.#content;
  }
  replace(newContent: T): void {
    this.#content = newContent;
  }
}

function demo_all(): void {
  print_section("s32-08: 泛型");

  // ═══════════════════════════════════════════════════════════
  // 第 1 步: 泛型 vs any — 类型信息的保留
  // ═══════════════════════════════════════════════════════════
  print_step(1, "泛型 vs any — 一个保留类型信息，一个全部丢掉");

  // 泛型：类型被推断并保留
  const s = identity("你好");
  const n = identity(42);
  console.log(`  identity("你好") 推断为 string: ${s.toUpperCase()}（可以放心用字符串方法）`);
  console.log(`  identity(42) 推断为 number: ${n.toFixed(2)}`);
  console.log(`  显式指定类型参数: identity<number>(${identity<number>(7)})`);

  // any：返回 any，后续任何操作都不检查
  const a = identityAny("你好");
  console.log(`  any 版本返回 any: ${String(a)}（调 a.不存在的属性() 编译期也不会拦）`);
  print_key_point("泛型 = 「类型参数化」：同一个函数适配多种类型，还保留每种类型的检查。\n    any = 把检查全关掉；泛型 = 检查跟着类型走。");

  // ═══════════════════════════════════════════════════════════
  // 第 2 步: 泛型约束 extends
  // ═══════════════════════════════════════════════════════════
  print_step(2, "泛型约束 — extends 不是继承，是「至少长这样」");

  interface User extends HasId { name: string; age: number }
  interface Product extends HasId { title: string; price: number }

  const users: User[] = [
    { id: "u-1", name: "小明", age: 18 },
    { id: "u-2", name: "小红", age: 20 },
  ];
  const products: Product[] = [
    { id: "p-1", title: "键盘", price: 199 },
  ];

  const foundUser = findById(users, "u-2");
  const foundProduct = findById(products, "p-1");
  console.log(`  在用户里找 u-2: ${foundUser?.name}（返回类型自动是 User）`);
  console.log(`  在商品里找 p-1: ${foundProduct?.title}（返回类型自动是 Product）`);
  print_note("同一个 findById，users 里返回 User，products 里返回 Product——T 被分别推断。");
  // findById([{ name: "没 id 的对象" }], "x");  // ← 编译错误：不满足 HasId 约束
  print_key_point("约束 = 给类型参数划最低要求：「T 必须至少有 id: string」。\n    有了约束，函数体内就能安全访问约束里声明的成员。");

  // ═══════════════════════════════════════════════════════════
  // 第 3 步: 泛型接口 — Result 模式
  // ═══════════════════════════════════════════════════════════
  print_step(3, "泛型接口 — Result<T> 模式");

  function safeParse(text: string): Result<number, string> {
    const n = Number(text);
    if (Number.isNaN(n)) return fail(`「${text}」不是数字`);
    return ok(n);
  }

  const r1 = safeParse("42");
  const r2 = safeParse("abc");

  if (r1.ok) {
    console.log(`  safeParse("42")  → 成功: ${r1.value}`);
  }
  if (!r2.ok) {
    console.log(`  safeParse("abc") → 失败: ${r2.error}`);
  }
  print_key_point("Result<T, E> = 「成功带 T 值 / 失败带 E 错误」的统一包装。\n    不抛异常也能传错误——s10 会拿它和 throw 全面对比。\n    注意 E 有默认值：Result<number> 等价于 Result<number, Error>。");

  // ═══════════════════════════════════════════════════════════
  // 第 4 步: 内置泛型工具
  // ═══════════════════════════════════════════════════════════
  print_step(4, "内置泛型 — Partial / Pick / Record");

  interface Todo { id: number; title: string; done: boolean }

  // Partial<T>：所有字段变可选 —— 适合「部分更新」
  function createTodo(partial: Partial<Todo>): Todo {
    return { id: 1, title: "默认任务", done: false, ...partial };
  }
  console.log(`  createTodo({ title: "学泛型" }) = ${JSON.stringify(createTodo({ title: "学泛型" }))}`);

  // Pick<T, K>：只挑几个字段 —— 适合「视图/摘要」
  const summary: Pick<Todo, "id" | "title"> = { id: 1, title: "学泛型" };
  console.log(`  Pick 出的摘要 = ${JSON.stringify(summary)}`);

  // Record<K, V>：键值字典 —— 适合「索引表」
  const todoById: Record<string, Todo> = {
    t1: { id: 1, title: "学泛型", done: false },
  };
  console.log(`  Record 索引表: todoById["t1"] = ${JSON.stringify(todoById["t1"])}`);

  print_note("Array<T>、Promise<T>、Map<K,V> 你其实一直在用——它们都是泛型。");
  print_key_point("内置泛型 = TS 官方提供的常用类型变换。\n    这些工具本质上都是类型层的小函数——s12 会手写它们的实现。");

  // ═══════════════════════════════════════════════════════════
  // 第 5 步: 泛型类
  // ═══════════════════════════════════════════════════════════
  print_step(5, "泛型类 — 一个装任意东西的盒子");

  const stringBox = new Box("苹果");
  console.log(`  Box<string> 取出: ${stringBox.get()}`);
  // stringBox.replace(42);   // ← 编译错误：Box<string> 只能装 string

  const numberBox = new Box(42);
  numberBox.replace(99);
  console.log(`  Box<number> 取出: ${numberBox.get()}`);
  print_key_point("泛型类 = 类的字段/方法参数化。\n    同一个 Box 类，装 string 的实例和装 number 的实例类型互不串味。");

  console.log();
  print_key_point("identity、约束、Result、内置工具、Box——类型参数化的套路齐了。\n    下一章：class——面向对象的家当。");
}

demo_all();
