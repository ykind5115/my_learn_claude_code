/**
 * s32-02: interface / type — 给对象形状贴标签
 *
 * ═══════════════════════════════════════════════════════════════
 * 学完本章你应该能回答：
 *   - interface 和 type 各有什么能力？什么时候用哪个？
 *   - 声明合并是什么？它有什么实际用途？
 *   - 可选属性、readonly、索引签名分别解决什么问题？
 * ═══════════════════════════════════════════════════════════════
 *
 * 启动方式:
 *     node s32_typescript/s02_interface_type/code.ts
 */

import { Color, print_step, print_note, print_key_point, print_section } from "../utils.ts";

// ── 供各步演示使用的类型定义 ──────────────────────────────────

// interface：描述对象形状的契约
interface User {
  name: string;
  age: number;
  email?: string;         // 可选属性：可有可无
  readonly id: string;    // 只读属性：创建后不能改
}

// type：也能描述对象形状
type Point = {
  x: number;
  y: number;
};

// 函数类型：描述一个函数长什么样
type Validator = (value: string) => boolean;

// 索引签名：任意数量的 key
type StringMap = {
  [key: string]: string;
};

function demo_all(): void {
  print_section("s32-02: interface / type");

  // ═══════════════════════════════════════════════════════════
  // 第 1 步: interface 描述对象形状
  // ═══════════════════════════════════════════════════════════
  print_step(1, "interface — 对象形状的契约");

  const u1: User = { name: "小明", age: 18, id: "u-1" };      // email 可选，可以没有
  const u2: User = { name: "小红", age: 20, id: "u-2", email: "hong@x.com" };

  console.log(`  u1 = ${JSON.stringify(u1)}`);
  console.log(`  u2 = ${JSON.stringify(u2)}`);
  print_note("u1 没写 email 也合法——可选属性。u2 写全了也合法。");
  print_key_point("interface = 一纸契约：对象必须提供哪些字段、字段是什么类型。\n    tsc 按契约检查每个字面量对象。");

  // ═══════════════════════════════════════════════════════════
  // 第 2 步: readonly — 只读属性
  // ═══════════════════════════════════════════════════════════
  print_step(2, "readonly — 贴上「禁止修改」的封条");

  const u3: User = { name: "阿强", age: 30, id: "u-3" };
  // u3.id = "hacked";  // ← 编译错误：id 是只读的
  // u3.age = 31;       // ← 编译错误：u3 是 const，属性也读不了
  console.log(`  u3.id 永远 = "${u3.id}"（readonly 封条 + const 冻结）`);
  print_key_point("readonly 是编译期封条——运行时其实还能改（标签擦除后没人管），\n    但它把「这个字段不该被改」写成了所有调用方都看得见的契约。");

  // ═══════════════════════════════════════════════════════════
  // 第 3 步: 函数类型与索引签名
  // ═══════════════════════════════════════════════════════════
  print_step(3, "函数类型 / 索引签名 — 更多形状");

  const isEmail: Validator = (v) => v.includes("@");
  const isLongEnough: Validator = (v) => v.length >= 6;

  console.log(`  isEmail("a@b.com") = ${isEmail("a@b.com")}`);
  console.log(`  isLongEnough("123456") = ${isLongEnough("123456")}`);

  const i18n: StringMap = { greeting: "你好", farewell: "再见", ok: "确定" };
  console.log(`  i18n 键值对 = ${JSON.stringify(i18n)}`);
  print_key_point("函数类型 = 函数的形状（参数+返回）；索引签名 = 「任意 key 都行」的形状。\n    两者让契约系统覆盖了函数和字典这两大类。");

  // ═══════════════════════════════════════════════════════════
  // 第 4 步: type vs interface 差异
  // ═══════════════════════════════════════════════════════════
  print_step(4, "type vs interface — 同一件事的两张脸");

  // interface 能做的：extends 继承
  interface AdminUser extends User {
    role: "admin" | "moderator";
  }

  // type 能做的：联合、交叉、从其他类型推导
  type Id = string | number;                       // 联合（interface 做不到）
  type NamedPoint = Point & { name: string };      // 交叉（两者都能做）

  const admin: AdminUser = { name: "管理员", age: 35, id: "a-1", role: "admin" };
  const namedPoint: NamedPoint = { x: 1, y: 2, name: "原点" };
  const id1: Id = "abc";
  const id2: Id = 123;

  console.log(`  admin = ${JSON.stringify(admin)}`);
  console.log(`  namedPoint = ${JSON.stringify(namedPoint)}`);
  console.log(`  Id 可以是字符串("${id1}")也可以是数字(${id2})`);
  print_key_point("差异只有两条：\n   ① type 能做联合/交叉/映射，interface 不能\n   ② interface 能声明合并（下一步），type 不能\n    现代实践：描述对象形状默认用 interface，需要联合等能力时用 type。");

  // ═══════════════════════════════════════════════════════════
  // 第 5 步: 声明合并
  // ═══════════════════════════════════════════════════════════
  print_step(5, "声明合并 — interface 的独门绝技");

  // 同一个名字声明两次 interface，字段自动合并！
  interface Player {
    name: string;
  }
  interface Player {
    score: number;   // 第二次声明"补丁式"扩展
  }

  const p: Player = { name: "选手A", score: 99 };
  console.log(`  Player 合并后 = ${JSON.stringify(p)}`);
  print_note("最典型用途：给第三方库的类型打补丁——不改库代码，扩展它的类型。");
  print_key_point("type 同名声明两次 = 报错；interface 同名声明两次 = 合并。\n    这就是「扩展第三方类型」的合法后门。");

  // ═══════════════════════════════════════════════════════════
  // 第 6 步: 结构化类型 — 鸭子类型
  // ═══════════════════════════════════════════════════════════
  print_step(6, "结构化类型 — 长得像就行，不需要声明身份");

  interface HasName { name: string }
  interface HasAge { age: number }

  const person = { name: "路人", age: 40, city: "北京" };  // 没有声明任何 interface

  const readName = (x: HasName): string => x.name;
  const readAge = (x: HasAge): number => x.age;

  console.log(`  readName(person) = "${readName(person)}"（person 自动满足 HasName）`);
  console.log(`  readAge(person) = ${readAge(person)}（person 也满足 HasAge）`);
  print_key_point("TS 是结构化类型（鸭子类型）：只要形状对得上，不需要 extends/声明。\n    和 Java 那种「必须登记身份」的名义类型完全不同——这让 TS 的接口极其轻量。");

  console.log();
  print_key_point("interface 画对象形状，type 补联合/交叉，readonly 封字段，可选属性管可选。\n    下一章：一个变量多种类型（union）+ 如何安全收窄（narrowing）。");
}

demo_all();
