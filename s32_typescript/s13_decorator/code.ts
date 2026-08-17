/**
 * s32-13: Decorator — 给代码声明式地加功能
 *
 * ═══════════════════════════════════════════════════════════════
 * 学完本章你应该能回答：
 *   - 装饰器解决什么问题？「声明式加功能」是什么意思？
 *   - 方法装饰器的两个参数（原方法、上下文）各是什么？
 *   - 装饰器工厂和裸装饰器有什么区别？叠加顺序是怎样的？
 * ═══════════════════════════════════════════════════════════════
 *
 * 注意：这是本模块唯一需要「编译」的章节！
 *   装饰器是不可擦除语法，node 不能直跑 .ts。
 *   运行方式: cd s32_typescript && npm run demo:s13
 *   （= tsc -p s13_decorator && node s13_decorator/dist/code.js）
 *
 * 本文件刻意不 import ../utils.ts（保持编译产物干净），
 * 自带一套迷你打印函数。
 */

// ── 迷你打印（自包含）────────────────────────────────────────
const C = {
  RESET: "\x1b[0m",
  HEADER: "\x1b[1m\x1b[36m",
  YELLOW: "\x1b[33m",
  MAGENTA: "\x1b[1m\x1b[35m",
  BOLD: "\x1b[1m",
} as const;
const step = (n: number, title: string): void =>
  console.log(`\n${C.HEADER}-- Step ${n}: ${title} --${C.RESET}`);
const note = (text: string): void => console.log(`  ${C.YELLOW}-> ${text}${C.RESET}`);
const key = (text: string): void => console.log(`  ${C.MAGENTA}* ${text}${C.RESET}`);
const line = "=".repeat(60);

// ── 装饰器定义 ────────────────────────────────────────────────

// 方法装饰器：接收「原方法 + 上下文」，返回「替换方法」
function log<This, Args extends unknown[], Return>(
  originalMethod: (this: This, ...args: Args) => Return,
  context: ClassMethodDecoratorContext<This, (this: This, ...args: Args) => Return>,
): (this: This, ...args: Args) => Return {
  const name = String(context.name);
  return function (this: This, ...args: Args): Return {
    console.log(`  [log] → ${name}(${args.join(", ")})`);
    const result = originalMethod.call(this, ...args);
    console.log(`  [log] ← ${name} = ${result}`);
    return result;
  };
}

// 装饰器工厂：先接配置，再返回真正的装饰器
function measure(label: string) {
  return function <This, Args extends unknown[], Return>(
    originalMethod: (this: This, ...args: Args) => Return,
    context: ClassMethodDecoratorContext<This, (this: This, ...args: Args) => Return>,
  ): (this: This, ...args: Args) => Return {
    return function (this: This, ...args: Args): Return {
      const t1 = performance.now();
      const result = originalMethod.call(this, ...args);
      console.log(`  [measure] ${label} 耗时 ${(performance.now() - t1).toFixed(1)}ms`);
      return result;
    };
  };
}

// 类装饰器：接收「原类 + 上下文」，可以登记、替换或增强
const registry: string[] = [];
function register<C extends new (...args: never[]) => object>(
  cls: C,
  context: ClassDecoratorContext<C>,
): C {
  registry.push(String(context.name));
  return cls;   // 原样返回（也可以返回子类替换）
}

// ── 使用装饰器 ────────────────────────────────────────────────

@register
class ApiService {
  @log
  @measure("fetchUser")
  fetchUser(id: number): string {
    return `用户${id}`;
  }

  @log
  greet(name: string): string {
    return `你好，${name}！`;
  }
}

console.log(`\n${C.BOLD}${line}${C.RESET}`);
console.log(`${C.HEADER}  s32-13: Decorator${C.RESET}`);
console.log(`${C.BOLD}${line}${C.RESET}\n`);

step(1, "裸装饰器 @log — 方法调用的进出日志");

const api = new ApiService();
const r1 = api.greet("小明");
console.log(`  调用结果: ${r1}`);
note("@log 把「打印日志」从业务逻辑里抽出来，业务方法里一行日志代码都没有。");

step(2, "装饰器工厂 @measure(label) — 先配参数再装饰");

const r2 = api.fetchUser(42);
console.log(`  调用结果: ${r2}`);
note("measure 是工厂：measure('fetchUser') 先接标签，返回真正的装饰器。");
note("叠加顺序：@log @measure 从下往上应用——measure 先包，log 再包（输出顺序可证）。");

step(3, "类装饰器 @register — 把类登记进注册表");

console.log(`  registry 内容: [${registry.join(", ")}]`);
note("类装饰器在类定义时执行一次——依赖注入容器、路由注册都是这个模式。");
key("装饰器 = 对类/方法的「包装函数」语法糖。\n    业务代码只写逻辑，横切功能（日志/计时/注册）用装饰器声明式挂上。\n    NestJS、MCP server 框架的声明式 API 都建立在这个机制上。");

step(4, "编译流程 — 为什么本章不能 node 直跑");

console.log(`  装饰器是不可擦除语法（编译后真的生成包装代码）。`);
console.log(`  运行方式: cd s32_typescript && npm run demo:s13`);
console.log(`  拆解: tsc -p s13_decorator（编译）→ node s13_decorator/dist/code.js（运行）`);
key("看一眼 dist/code.js：tsc 生成了 __esDecorate 等 helper，把装饰器翻译成\n    普通函数包装调用——运行时没有任何「装饰器」概念，全是函数组合。\n    这就是 s00 说的：编译器把高级语法翻译成运行时能懂的东西。");
