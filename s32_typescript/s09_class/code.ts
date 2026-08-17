/**
 * s32-09: class — 面向对象的家当
 *
 * ═══════════════════════════════════════════════════════════════
 * 学完本章你应该能回答：
 *   - public/private/protected 和 # 私有字段有什么区别？哪个是真的私有？
 *   - 抽象类（abstract）和接口（implements）各解决什么问题？
 *   - 为什么本模块的 code.ts 看不到参数属性？
 * ═══════════════════════════════════════════════════════════════
 *
 * 启动方式:
 *     node s32_typescript/s09_class/code.ts
 */

import { Color, print_step, print_note, print_key_point, print_section } from "../utils.ts";

// ── 演示用类 ──────────────────────────────────────────────────

// 注意：字段用「显式声明 + 构造函数赋值」。
// TS 有更短的参数属性写法 constructor(private x: number)，
// 但它不可擦除（node 直跑会报错），所以 code.ts 避开——README 细讲。
class BankAccount {
  readonly accountNo: string;   // 只读：构造后不可改
  private ownerName: string;    // 编译期私有：运行时字段名还是 ownerName
  #balance: number;             // 运行时真私有：存在私有槽里，外面拿不到
  protected createdAt: string;  // 子类可见，外部不可见

  constructor(accountNo: string, ownerName: string, initialBalance: number) {
    this.accountNo = accountNo;
    this.ownerName = ownerName;
    this.#balance = initialBalance;
    this.createdAt = new Date().toISOString().slice(0, 10);
  }

  deposit(amount: number): void {
    this.#balance += amount;
  }

  get balance(): number {        // getter：像属性一样读，内部是方法
    return this.#balance;
  }

  private maskOwner(): string {  // private 方法：只能类内部调用
    return this.ownerName.slice(0, 1) + "**";
  }

  describe(): string {
    return `账户 ${this.accountNo}（${this.maskOwner()}）余额: ${this.balance} 元`;
  }
}

// 抽象类：不能 new，只给子类当模板
abstract class Shape {
  abstract area(): number;       // 抽象方法：子类必须实现

  describe(): string {           // 普通方法：所有子类共享
    return `面积 = ${this.area().toFixed(2)}`;
  }
}

class Circle extends Shape {
  readonly radius: number;
  constructor(radius: number) {
    super();
    this.radius = radius;
  }
  area(): number {
    return Math.PI * this.radius ** 2;
  }
}

class Square extends Shape {
  readonly side: number;
  constructor(side: number) {
    super();
    this.side = side;
  }
  area(): number {
    return this.side ** 2;
  }
}

// implements：实现接口——「你必须提供这些能力」（没有 extends 的继承负担）
interface HasArea {
  area(): number;
}
class Rectangle implements HasArea {
  readonly w: number;
  readonly h: number;
  constructor(w: number, h: number) {
    this.w = w;
    this.h = h;
  }
  area(): number {
    return this.w * this.h;
  }
}

// getter + setter：读写都经过方法
class Temperature {
  #celsius: number;
  constructor(celsius: number) {
    this.#celsius = celsius;
  }
  get fahrenheit(): number {
    return this.#celsius * 9 / 5 + 32;
  }
  set fahrenheit(f: number) {
    if (f < -459.67) throw new Error("低于绝对零度，物理不存在");
    this.#celsius = (f - 32) * 5 / 9;
  }
}

function demo_all(): void {
  print_section("s32-09: class");

  // ═══════════════════════════════════════════════════════════
  // 第 1 步: 字段、构造、方法、getter
  // ═══════════════════════════════════════════════════════════
  print_step(1, "字段 / 构造 / 方法 / getter — 类的基本件");

  const acc = new BankAccount("6222-0001", "王小明", 1000);
  acc.deposit(500);
  console.log(`  ${acc.describe()}`);
  console.log(`  读 getter: acc.balance = ${acc.balance}`);
  print_note("readonly 字段构造后不可改；getter 让「读余额」看起来像读属性。");

  // ═══════════════════════════════════════════════════════════
  // 第 2 步: private vs # — 编译期私有 vs 运行时私有
  // ═══════════════════════════════════════════════════════════
  print_step(2, "private vs # — 一个挡编译期，一个挡运行时");

  // acc.ownerName;        // ← 编译错误：private
  // acc.#balance;         // ← 编译错误 + 运行时也进不去
  // acc.maskOwner();      // ← 编译错误：private 方法

  // 但 private 只是编译期约定——运行时用 any 绕过
  const anyAcc = acc as any;
  console.log(`  绕过 private: anyAcc.ownerName = "${anyAcc.ownerName}"（拿到了！）`);
  console.log(`  绕过 #: anyAcc["#balance"] = ${anyAcc["#balance"]}（undefined，进不去）`);
  console.log(`  Object.keys(acc) = ${JSON.stringify(Object.keys(acc))}`);
  print_note("看到没：ownerName 在实例上，所以 any 能拿到；#balance 在私有槽里，字段列表都没有它。");
  print_key_point("# 私有 = 真私有（运行时隔离，Object.keys 都看不见）；\n    private/protected = 编译期约定（擦除后等于没有）。\n    数据安全要 #，团队协作提示用 private。");

  // ═══════════════════════════════════════════════════════════
  // 第 3 步: abstract — 抽象类模板
  // ═══════════════════════════════════════════════════════════
  print_step(3, "abstract — 给一族类立规矩");

  // const s = new Shape();  // ← 编译错误：抽象类不能实例化
  const shapes: Shape[] = [new Circle(2), new Square(3)];
  for (const shape of shapes) {
    console.log(`  ${shape.describe()}`);
  }
  print_note("Shape 定义了「必须有 area()」的规矩 + 共享的 describe()，子类只写差异。");
  print_key_point("abstract = 模板 + 规矩：不能 new，子类必须实现抽象方法。\n    数组元素统一标注 Shape，运行时每个元素用自己的 area()——这就是多态。");

  // ═══════════════════════════════════════════════════════════
  // 第 4 步: implements — 实现接口
  // ═══════════════════════════════════════════════════════════
  print_step(4, "implements — 声明「我提供这些能力」");

  const rect = new Rectangle(4, 5);
  const areaOf = (x: HasArea): number => x.area();
  console.log(`  Rectangle(4, 5) 面积 = ${areaOf(rect)}`);
  print_note("implements 只检查形状，不共享实现（不像 extends 会继承代码）。");
  print_key_point("extends = 继承实现（代码复用）；implements = 承诺接口（形状契约）。\n    一个类只能 extends 一个父类，但可以 implements 多个接口。");

  // ═══════════════════════════════════════════════════════════
  // 第 5 步: getter / setter — 读写都经过方法
  // ═══════════════════════════════════════════════════════════
  print_step(5, "getter / setter — 属性访问背后的方法");

  const t = new Temperature(25);
  console.log(`  25°C = ${t.fahrenheit.toFixed(1)}°F`);
  t.fahrenheit = 98.6;   // setter：校验 + 换算
  console.log(`  设置 98.6°F 后: t.fahrenheit = ${t.fahrenheit.toFixed(1)}°F（内部摄氏 37°C，#celsius 外部读不到）`);
  try {
    t.fahrenheit = -999;
  } catch (e) {
    console.log(`  ${Color.WARNING}setter 校验拦下: ${(e as Error).message}${Color.RESET}`);
  }
  print_key_point("getter/setter = 属性语法 + 方法逻辑：读时计算，写时校验。\n    这是数据封装的最后一课——外面永远通过门禁进，不直接摸数据。");

  console.log();
  print_key_point("class 家当齐了：字段/构造/getter、#真私有、abstract 模板、implements 契约。\n    下一章：Error / 异常处理——程序摔倒了怎么优雅地站起来。");
}

demo_all();
