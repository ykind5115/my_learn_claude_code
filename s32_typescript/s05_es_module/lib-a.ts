/**
 * s32-05 辅助模块 A：
 *   - 命名导出（greet / aValue）
 *   - 模块级状态（visitCounter）—— 演示模块缓存
 *   - 与 lib-b 循环依赖（lib-b 也导入了本模块）
 */

import { bValue, getB } from "./lib-b.ts";

export const aValue = "A";

// 模块级状态：整个进程里这个模块只执行一次
export const visitCounter = { count: 0 };
export function visit(): number {
  visitCounter.count += 1;
  return visitCounter.count;
}

export function greet(name: string): string {
  return `你好，${name}！`;
}

// 调用 lib-b 的函数 —— 循环依赖在「调用时」早已初始化完成，所以没问题
export function callB(): string {
  return getB();
}

// live binding：拿到的永远是 lib-b 的「当前值」，不是快照
export function readBValue(): string {
  return bValue;
}
