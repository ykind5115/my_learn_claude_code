/**
 * s32-05: ES Module — 把代码拆成可复用的模块
 *
 * ═══════════════════════════════════════════════════════════════
 * 学完本章你应该能回答：
 *   - 命名导出和默认导出的区别？什么时候用哪个？
 *   - 为什么同一个模块 import 两次只执行一次？
 *   - ESM 和 CJS 怎么互相调用？循环依赖为什么不会立刻爆炸？
 * ═══════════════════════════════════════════════════════════════
 *
 * 启动方式:
 *     node s32_typescript/s05_es_module/code.ts
 */

import { createRequire } from "node:module";
import { Color, print_step, print_note, print_key_point, print_section } from "../utils.ts";
import { greet, aValue, visitCounter, callB, readBValue } from "./lib-a.ts";
import defaultGreet, { bValue, updateBValue } from "./lib-b.ts";

// 同一个模块导入两次（两个命名空间）——用来演示模块缓存
import * as libA1 from "./lib-a.ts";
import * as libA2 from "./lib-a.ts";

function demo_all(): void {
  print_section("s32-05: ES Module");

  // ═══════════════════════════════════════════════════════════
  // 第 1 步: 命名导出 vs 默认导出
  // ═══════════════════════════════════════════════════════════
  print_step(1, "命名导出 vs 默认导出 — 模块的两种出口");

  console.log(`  命名导出: ${greet("小明")}（import { greet } 精确点名）`);
  console.log(`  命名导出: aValue = ${aValue}`);
  console.log(`  默认导出: ${defaultGreet("小红")}（import xxx 任意取名）`);
  print_note("命名导出：可以导多个，导入时必须用原名（或用 as 改名）。");
  print_note("默认导出：每个模块最多一个，导入方随便起名。");
  print_note("本模块所有相对导入都带 .ts 扩展名——Node ESM 的硬要求，缺了就报 ERR_MODULE_NOT_FOUND。");

  // ═══════════════════════════════════════════════════════════
  // 第 2 步: 模块缓存 — 同一个模块只执行一次
  // ═══════════════════════════════════════════════════════════
  print_step(2, "模块缓存 — 不管 import 多少次，只执行一次");

  const r1 = libA1.visit();
  const r2 = libA2.visit();
  console.log(`  libA1.visit() = ${r1}, libA2.visit() = ${r2}`);
  console.log(`  libA1 看到的计数器 = ${libA1.visitCounter.count}（libA2 是同一个实例！）`);
  print_key_point("模块按 URL 缓存：进程里第一次加载后，后续 import 直接复用同一份。\n    副作用（如计数器）只会发生一次——这就是模块级单例的由来。");

  console.log(`  当前模块 URL: ${import.meta.url}`);
  print_note("import.meta.url / import.meta.dirname 是模块的「自定位」能力，\n    本模块所有文件路径都基于它解析，绝不依赖 process.cwd()。");

  // ═══════════════════════════════════════════════════════════
  // 第 3 步: 循环依赖 + live binding
  // ═══════════════════════════════════════════════════════════
  print_step(3, "循环依赖 + 活绑定 — 为什么没炸？");

  // lib-a 和 lib-b 互相 import，但调用发生在两个模块都初始化完之后
  console.log(`  callB() 正常返回: ${callB()}`);
  console.log(`  读 bValue（初始）: ${readBValue()}`);

  // live binding：改完值，所有导入方立刻看到新值
  updateBValue("被更新过");
  console.log(`  直接导入的 bValue: ${bValue}`);
  console.log(`  透过 lib-a 读 bValue: ${readBValue()}`);
  print_key_point("ESM 的导出是「活绑定」（live binding）：导入方拿的是引用，不是拷贝。\n    循环依赖不炸的前提：别在模块初始化时互相读取顶层值——\n    函数延迟调用、let 活绑定，两个技巧让循环依赖可控。");

  // ═══════════════════════════════════════════════════════════
  // 第 4 步: ESM ↔ CJS 互操作
  // ═══════════════════════════════════════════════════════════
  print_step(4, "ESM ↔ CJS 互操作 — 新旧模块系统共存");

  // ESM 里用 createRequire 加载 CJS 模块
  const require = createRequire(import.meta.url);
  const legacy = require("./legacy.cjs") as {
    version: string;
    legacyGreet: (name: string) => string;
  };
  console.log(`  ESM 调 CJS: ${legacy.legacyGreet("小刚")}`);
  console.log(`  CJS 模块导出的 version 字段: ${legacy.version}`);

  print_note("反向（CJS 里同步 import ESM）做不到——CJS 只能用动态 import()（返回 Promise）。");
  print_key_point("Node 判定模块类型：package.json 的 \"type\": \"module\" 决定默认值，\n    .cjs 强制 CJS，.mjs 强制 ESM。本模块 package.json 声明了 ESM，\n    所以所有 .ts 都按 ESM 解析——这是模块能直跑的地基。");

  console.log();
  print_key_point("命名/默认导出、模块缓存、活绑定、互操作——模块化地基打好了。\n    下一章：Node.js——看这些模块跑在什么底座上。");
}

demo_all();
