/**
 * s32-04 辅助演示：在 CommonJS 顶层（主上下文）观察事件循环排队
 * 由 code.ts 用子进程调用 —— 也顺便预告了 s11 的 child_process
 *
 * 为什么用 .cjs？因为 .ts/.mjs（ESM）的模块顶层本身运行在
 * promise 上下文里（模块加载器是异步的），只有 CJS 顶层
 * 才是「主上下文」——nextTick 排在最前。扩展名决定模块类型，
 * 这是下一章 s05 的主角。
 */

console.log("  ── 演示 B：CJS 顶层排队（子进程，主上下文）──");
console.log("  ① 同步代码（调用栈直接执行）");
process.nextTick(() => console.log("  ② process.nextTick（主上下文里最先执行的微任务）"));
Promise.resolve().then(() => console.log("  ③ Promise.then（微任务）"));
setTimeout(() => console.log("  ④ setTimeout（宏任务）"), 0);
console.log("  ⑤ 同步代码结束");
