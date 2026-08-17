/**
 * s32-04: async / await / Promise — 异步世界的三件套
 *
 * ═══════════════════════════════════════════════════════════════
 * 学完本章你应该能回答：
 *   - Promise 有哪三种状态？状态之间如何流转？
 *   - async/await 和 Promise.then 是什么关系？
 *   - 微任务和宏任务谁先执行？Promise.all 为什么比串行快？
 * ═══════════════════════════════════════════════════════════════
 *
 * 启动方式:
 *     node s32_typescript/s04_async/code.ts
 */

import { join } from "node:path";
import { Color, print_step, print_note, print_key_point, print_section } from "../utils.ts";

// ── 工具函数 ──────────────────────────────────────────────────

/** 模拟网络请求：延迟 ms 毫秒后返回数据（或失败） */
function fakeFetch<T>(data: T, ms: number, shouldFail = false): Promise<T> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (shouldFail) reject(new Error("请求超时"));
      else resolve(data);
    }, ms);
  });
}

/** 用探针观察 Promise 当前状态（.then 回调在微任务里跑，同步返回时必然是 pending） */
function inspectPromise(p: Promise<unknown>): string {
  let state = "pending";
  p.then(
    () => { state = "fulfilled"; },
    () => { state = "rejected"; },
  );
  return state;
}

/** 异步获取用户名（模拟 API） */
async function fetchUserName(id: number): Promise<string> {
  const user = await fakeFetch({ id, name: `用户${id}` }, 80);
  return user.name;
}

async function demo_all(): Promise<void> {
  print_section("s32-04: async / await / Promise");

  // ═══════════════════════════════════════════════════════════
  // 第 1 步: Promise 三态
  // ═══════════════════════════════════════════════════════════
  print_step(1, "Promise 三态 — pending → fulfilled / rejected");

  const p = fakeFetch("快递到了", 300);
  console.log(`  创建瞬间状态: ${inspectPromise(p)}`);
  print_note("Promise 一旦创建就开始干活，状态从 pending 出发，只能变化一次。");

  const result = await p;   // await = 等到状态不再是 pending
  console.log(`  await 之后拿到: "${result}"（状态已 fulfilled）`);

  // 三态流转图（打印版）
  console.log(`
        ┌────────────┐   resolve(值)   ┌──────────────┐
        │  pending   │ ──────────────→ │  fulfilled   │
        │  (进行中)  │                 │  (成功，有值) │
        └────────────┘                 └──────────────┘
               │
               │ reject(错误)
               ▼
        ┌──────────────┐
        │   rejected   │
        │ (失败，有错因) │
        └──────────────┘`);
  print_key_point("Promise = 一个「未来的结果」的占位盒：要么成功带值，要么失败带错因。\n    状态只能从 pending 变一次，之后永远不变——这叫 settled。");

  // ═══════════════════════════════════════════════════════════
  // 第 2 步: 回调地狱 → Promise → async/await
  // ═══════════════════════════════════════════════════════════
  print_step(2, "async/await — 让异步代码读起来像同步");

  // 回调风格（JS 老写法）：层层嵌套，又称回调地狱
  // fakeFetch({}, 100, (err, data) => {
  //   fakeFetch({}, 100, (err, data) => {
  //     fakeFetch({}, 100, (err, data) => {   // 越套越深……
  //     });
  //   });
  // });

  // async/await：同样的顺序依赖，写成直线
  const name1 = await fetchUserName(1);
  const name2 = await fetchUserName(2);
  console.log(`  顺序获取: ${name1} → ${name2}`);
  print_key_point("async/await 是 Promise 的语法糖：\n    async 函数必然返回 Promise，await 等价于 .then 的「暂停等结果」。\n    顺序依赖的代码从金字塔变成了直线。");

  // ═══════════════════════════════════════════════════════════
  // 第 3 步: 微任务 vs 宏任务
  // ═══════════════════════════════════════════════════════════
  print_step(3, "微任务 vs 宏任务 — 事件循环的排队规则（含一个官方陷阱）");

  // 演示 A：此刻我们正处在 async 续体（await 之后的代码）里，
  // 也就是「微任务上下文」——排队规则会和主上下文不同
  console.log("  ── 演示 A：async 续体内排队（当前进程）──");
  console.log("  ① 同步代码（调用栈直接执行）");
  process.nextTick(() => console.log("  ③ process.nextTick（微任务队列清空后才轮到）"));
  Promise.resolve().then(() => console.log("  ② Promise.then（微任务）"));
  console.log("  ④ 同步代码结束");
  await fakeFetch(null, 50);   // 让上面的排队全部跑完
  print_note("② 竟然排在 ③ 前面！因为此刻我们就在一个微任务（async 续体）里——\n    Node 官方文档：在 Promise 回调内调用 nextTick，回调排在微任务队列之后执行。");

  // 演示 B：用 .cjs 扩展名让子进程跑 CommonJS —— 只有 CJS 顶层
  // 才是「主上下文」，nextTick 排在最前（扩展名决定模块类型，s05 细讲）
  const { spawnSync } = await import("node:child_process");
  const topLevelDemo = join(import.meta.dirname, "event_loop_main.cjs");
  spawnSync(process.execPath, [topLevelDemo], { stdio: "inherit" });

  print_key_point("两次演示顺序不同，但两条铁律不变：\n    ① 同步代码最先执行；② 微任务整体先于宏任务。\n    而且 .ts/.mjs 的顶层同样是 promise 上下文（模块加载器本身是异步的）！\n    工程结论：别依赖 nextTick 和 Promise 之间的相对顺序。\n    「await 后面的代码」相当于包在微任务里——这就是 async 函数的执行机制。");

  // ═══════════════════════════════════════════════════════════
  // 第 4 步: Promise.all — 并行 vs 串行
  // ═══════════════════════════════════════════════════════════
  print_step(4, "Promise.all — 并行等待，时间省 5 倍");

  // 串行：一个一个等，总耗时 = 各耗时之和
  const t1 = performance.now();
  const serialNames: string[] = [];
  for (const id of [1, 2, 3, 4, 5]) {
    serialNames.push(await fetchUserName(id));
  }
  const serialMs = Math.round(performance.now() - t1);

  // 并行：全部同时出发，总耗时 = 最慢的那个
  const t2 = performance.now();
  const parallelNames = await Promise.all([1, 2, 3, 4, 5].map(fetchUserName));
  const parallelMs = Math.round(performance.now() - t2);

  console.log(`  串行 5 个请求: ${serialMs}ms  → ${serialNames.join(", ")}`);
  console.log(`  并行 5 个请求: ${parallelMs}ms  → ${parallelNames.join(", ")}`);
  print_key_point("相互独立的请求用 Promise.all 同时出发——总耗时约等于最慢的那个。\n    这是 Agent 一轮循环里并行调用多个工具时的底层机制。");

  // ═══════════════════════════════════════════════════════════
  // 第 5 步: 错误处理
  // ═══════════════════════════════════════════════════════════
  print_step(5, "错误处理 — try/catch 与 allSettled");

  try {
    await fakeFetch(null, 50, true);
  } catch (e) {
    console.log(`  try/catch 捕获: ${Color.WARNING}${(e as Error).message}${Color.RESET}`);
  }

  // Promise.all 遇错即停；allSettled 等全部结束，逐个看结果
  const settled = await Promise.allSettled([
    fakeFetch("成功任务", 50),
    fakeFetch(null, 50, true),
  ]);
  for (const s of settled) {
    if (s.status === "fulfilled") {
      console.log(`  allSettled: ${Color.SUCCESS}✅ ${s.value}${Color.RESET}`);
    } else {
      console.log(`  allSettled: ${Color.ERROR}❌ ${s.reason.message}${Color.RESET}`);
    }
  }
  print_key_point("await 的错误用 try/catch 接住（等价于 .catch）；\n    一批任务「一个都不能少」时用 allSettled——它永不 reject。");

  console.log();
  print_key_point("Promise 三态 → async/await 直线写法 → 微任务先于宏任务 → all 并行。\n    下一章：ES Module——把这些能力拆成模块组织起来。");
}

// 顶层 await：ESM 独有的能力——模块顶层可以直接 await（CJS 不行）
await demo_all();
